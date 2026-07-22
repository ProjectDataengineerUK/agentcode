#!/usr/bin/env python3
"""AgentCodex Judge V0 - cross-model second opinion via OpenRouter."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path


class JudgeError(RuntimeError):
    def __init__(self, message: str, exit_code: int) -> None:
        super().__init__(message)
        self.exit_code = exit_code


@dataclass(frozen=True, slots=True)
class LedgerEntry:
    date: str
    ts: str
    model: str
    target: str
    verdict: str
    cost_usd: float | None = None

    @classmethod
    def from_json(cls, raw: str) -> LedgerEntry | None:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return None
        return cls(
            date=str(data.get("date", "")),
            ts=str(data.get("ts", "")),
            model=str(data.get("model", "")),
            target=str(data.get("target", "")),
            verdict=str(data.get("verdict", "")),
            cost_usd=data.get("cost_usd"),
        )

    def to_dict(self) -> dict[str, str | float | None]:
        return {key: value for key, value in asdict(self).items() if value is not None or key == "cost_usd"}


REPO_ROOT = Path(__file__).resolve().parent.parent
LEDGER = REPO_ROOT / ".agentcodex" / "storage" / "judge-ledger.jsonl"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "openai/gpt-4o-mini"
DEFAULT_BUDGET = 10

PHASE_MODEL_DEFAULTS: dict[str, str] = {
    "generic": DEFAULT_MODEL,
    "define": "openai/gpt-4o",
    "design": "openai/gpt-4o",
    "build": "openai/gpt-4o",
}

GENERIC_SYSTEM_PROMPT = """You are a senior reviewer providing a second opinion on output produced by another AI. Catch hallucinated APIs, wrong invariants, insecure patterns, and logic errors.

Return raw JSON only, matching this schema:
{
  "verdict": "PASS" | "FAIL",
  "confidence": 0.0,
  "summary": "One sentence.",
  "concerns": [{"severity": "high" | "medium" | "low", "issue": "...", "evidence": "..."}],
  "suggested_fixes": ["..."]
}

PASS means no high-severity issues and confidence >= 0.70. FAIL means any high-severity issue or confidence < 0.70. Cite line numbers, function names, section names, or exact strings as evidence."""

DEFINE_SYSTEM_PROMPT = """You are a senior product engineer judging an AgentCodex DEFINE requirements artifact. Focus on missing or vague acceptance criteria, ambiguous scope, unvalidated assumptions, contradictions, missing non-functional requirements, user/persona gaps, and unmeasurable success criteria.

Return raw JSON only with verdict, confidence, summary, concerns, and suggested_fixes. PASS means ready for design. FAIL means any high-severity gap or confidence < 0.70."""

DESIGN_SYSTEM_PROMPT = """You are a senior architect judging an AgentCodex DESIGN artifact. Focus on hallucinated APIs, wrong invariants, missing edge cases, unsafe defaults, unjustified decisions, missing rollback stories, migration risks, security gaps, and scalability blind spots.

Return raw JSON only with verdict, confidence, summary, concerns, and suggested_fixes. PASS means safe enough to build. FAIL means any high-severity concern or confidence < 0.70."""

BUILD_SYSTEM_PROMPT = """You are a senior engineer judging code or an AgentCodex BUILD_REPORT artifact. Focus on concrete bugs, race conditions, resource leaks, missing error handling, unsafe SQL, secrets, injection risks, destructive operations, and incorrect API usage.

Return raw JSON only with verdict, confidence, summary, concerns, and suggested_fixes. PASS means no high-severity correctness issue. FAIL means any high-severity bug or confidence < 0.70."""

PHASE_SYSTEM_PROMPTS: dict[str, str] = {
    "generic": GENERIC_SYSTEM_PROMPT,
    "define": DEFINE_SYSTEM_PROMPT,
    "design": DESIGN_SYSTEM_PROMPT,
    "build": BUILD_SYSTEM_PROMPT,
}


def today_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")


def read_ledger_entries() -> list[LedgerEntry]:
    if not LEDGER.exists():
        return []
    entries: list[LedgerEntry] = []
    for raw_line in LEDGER.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.strip()
        if not stripped:
            continue
        entry = LedgerEntry.from_json(stripped)
        if entry is not None:
            entries.append(entry)
    return entries


def load_today_count() -> int:
    today = today_utc()
    return sum(1 for entry in read_ledger_entries() if entry.date == today)


def append_ledger(model: str, target: str, verdict: str, cost_usd: float | None = None) -> None:
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    entry = LedgerEntry(
        date=today_utc(),
        ts=dt.datetime.now(dt.timezone.utc).isoformat(),
        model=model,
        target=target,
        verdict=verdict,
        cost_usd=cost_usd,
    )
    with LEDGER.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry.to_dict()) + "\n")


def show_ledger() -> int:
    entries = read_ledger_entries()
    if not entries:
        print("No judge calls recorded yet.")
        return 0
    today = today_utc()
    today_calls = [entry for entry in entries if entry.date == today]
    budget = int(os.environ.get("JUDGE_BUDGET", DEFAULT_BUDGET))
    print(f"Judge Ledger - {LEDGER.relative_to(REPO_ROOT)}")
    print(f"  Today ({today}): {len(today_calls)} / {budget} calls")
    print(f"  All-time:        {len(entries)} calls")
    if today_calls:
        print("\n  Today's calls:")
        for entry in today_calls:
            print(f"    [{entry.verdict:4}] {entry.model}  {entry.target}")
    return 0


def call_openrouter(api_key: str, model: str, content: str, context: str, phase: str = "generic") -> dict[str, object]:
    system_prompt = PHASE_SYSTEM_PROMPTS.get(phase, GENERIC_SYSTEM_PROMPT)
    user_prompt = f"Context: {context}\n\n--- CONTENT TO JUDGE ---\n{content}\n--- END CONTENT ---"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.1,
        "max_tokens": 1500,
    }
    request = urllib.request.Request(
        OPENROUTER_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/ProjectDataengineerUK/agentcodex",
            "X-Title": "AgentCodex Judge V0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
        raise JudgeError(f"OpenRouter HTTP {exc.code}: {body[:300]}", 4) from exc
    except urllib.error.URLError as exc:
        raise JudgeError(f"Network error: {exc.reason}", 4) from exc

    try:
        api_response = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise JudgeError(f"OpenRouter returned non-JSON envelope: {raw[:200]}", 4) from exc

    try:
        content_str = api_response["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as exc:
        raise JudgeError(f"Unexpected OpenRouter response shape: {raw[:400]}", 4) from exc

    content_str = re.sub(r"^```(?:json)?\s*\n?", "", str(content_str).strip())
    content_str = re.sub(r"\n?```\s*$", "", content_str)
    try:
        verdict: dict[str, object] = json.loads(content_str)
    except json.JSONDecodeError as exc:
        raise JudgeError(f"Judge returned non-JSON:\n{content_str[:500]}", 4) from exc

    usage = api_response.get("usage", {})
    if usage:
        verdict["_usage"] = usage
    return verdict


def render_markdown(verdict: dict[str, object], target: str, model: str) -> str:
    verdict_value = str(verdict.get("verdict", "FAIL")).upper()
    confidence = float(verdict.get("confidence", 0) or 0)
    summary = str(verdict.get("summary", ""))
    concerns = verdict.get("concerns", [])
    fixes = verdict.get("suggested_fixes", [])
    lines = [
        f"## Judge Verdict - {verdict_value}",
        "",
        f"**Target:** `{target}`  |  **Model:** `{model}`  |  **Confidence:** {confidence:.2f}",
        "",
        f"**Summary:** {summary}",
        "",
    ]
    if isinstance(concerns, list) and concerns:
        lines.extend(["### Concerns", "", "| Severity | Issue | Evidence |", "|---|---|---|"])
        for concern in concerns:
            if not isinstance(concern, dict):
                continue
            severity = str(concern.get("severity", "?")).replace("|", "\\|")
            issue = str(concern.get("issue", "")).replace("|", "\\|")
            evidence = str(concern.get("evidence", "")).replace("|", "\\|")
            lines.append(f"| {severity} | {issue} | {evidence} |")
        lines.append("")
    if isinstance(fixes, list) and fixes:
        lines.extend(["### Suggested Fixes", ""])
        lines.extend(f"- {fix}" for fix in fixes)
        lines.append("")
    usage = verdict.get("_usage", {})
    if isinstance(usage, dict) and usage:
        lines.append(f"*Tokens - prompt: {usage.get('prompt_tokens', '?')}  completion: {usage.get('completion_tokens', '?')}*")
        lines.append("")
    lines.append("_Judge is advisory. AgentCodex remains responsible for verification and final decisions._")
    return "\n".join(lines) + "\n"


def resolve_model(phase: str, explicit_model: str | None) -> str:
    if explicit_model:
        return explicit_model
    if os.environ.get("JUDGE_MODEL"):
        return os.environ["JUDGE_MODEL"]
    return PHASE_MODEL_DEFAULTS.get(phase, DEFAULT_MODEL)


def read_target(args: argparse.Namespace) -> tuple[str, str, int]:
    if args.stdin:
        content = sys.stdin.read()
        return content, "<stdin>", 0
    if not args.target:
        return "", "", 2
    target_path = Path(args.target).expanduser().resolve()
    if not target_path.exists():
        print(f"[ERROR] File not found: {target_path}", file=sys.stderr)
        return "", "", 2
    if target_path.stat().st_size > 200_000:
        print("[ERROR] File exceeds 200KB. Judge V0 does not chunk large files.", file=sys.stderr)
        return "", "", 2
    content = target_path.read_text(encoding="utf-8", errors="replace")
    try:
        label = str(target_path.relative_to(REPO_ROOT))
    except ValueError:
        label = str(target_path)
    return content, label, 0


def main() -> int:
    parser = argparse.ArgumentParser(description="AgentCodex Judge V0 - OpenRouter second opinion")
    parser.add_argument("target", nargs="?", help="Path to file to judge, or use --stdin")
    parser.add_argument("--stdin", action="store_true", help="Read content from stdin")
    parser.add_argument("--phase", choices=sorted(PHASE_SYSTEM_PROMPTS), default="generic")
    parser.add_argument("--model", default=None, help="OpenRouter model slug")
    parser.add_argument("--context", default="General code/content review - flag anything the author may have missed.")
    parser.add_argument("--strict", action="store_true", help="Return failure status on FAIL; kept for phase command gating")
    parser.add_argument("--ledger", action="store_true", help="Show budget usage")
    parser.add_argument("--json", action="store_true", help="Emit raw JSON verdict")
    args = parser.parse_args()

    if args.ledger:
        return show_ledger()

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("[ERROR] OPENROUTER_API_KEY not set.", file=sys.stderr)
        print("  Get a key at https://openrouter.ai/keys and export it.", file=sys.stderr)
        return 2

    content, target_label, read_code = read_target(args)
    if read_code:
        parser.error("Provide a file path or --stdin")
        return read_code
    if not content.strip():
        print("[ERROR] Target content is empty.", file=sys.stderr)
        return 2

    budget = int(os.environ.get("JUDGE_BUDGET", DEFAULT_BUDGET))
    used = load_today_count()
    if used >= budget:
        print(f"[ERROR] Daily budget exhausted: {used}/{budget} calls today.", file=sys.stderr)
        return 3

    model = resolve_model(args.phase, args.model)
    try:
        verdict = call_openrouter(api_key, model, content, args.context, args.phase)
    except JudgeError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return exc.exit_code

    verdict_value = str(verdict.get("verdict", "FAIL")).upper()
    append_ledger(model, target_label, verdict_value)
    if args.json:
        print(json.dumps(verdict, indent=2))
    else:
        print(render_markdown(verdict, target_label, model))
    _ = args.strict
    return 0 if verdict_value == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
