#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

from state_utils import ensure_agentcodex_dirs, load_project_state, now_iso, resolve_root, save_project_state


def print_usage() -> int:
    print("Usage: python3 scripts/agentcodex.py failure-pattern-promote [target-project-dir] [--json]")
    return 1


def normalize_reason(value: str) -> str:
    value = value.strip().casefold()
    value = re.sub(r"\d{4}-\d{2}-\d{2}t[0-9:\-+.z]+", "<timestamp>", value)
    value = re.sub(r"\b[0-9a-f]{6,}\b", "<id>", value)
    return value


def load_failure_events(root: Path) -> list[dict[str, str]]:
    events: list[dict[str, str]] = []
    failures_root = root / ".agentcodex" / "observability" / "failures"
    logs_root = root / ".agentcodex" / "observability" / "logs"
    if failures_root.exists():
        for path in sorted(failures_root.glob("*.json")):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if not isinstance(payload, list):
                continue
            for item in payload:
                events.append(
                    {
                        "script": str(item.get("script", path.stem)),
                        "stage": str(item.get("stage", "unknown")),
                        "reason": str(item.get("reason", item.get("message", "unknown failure"))),
                        "source": str(path.relative_to(root)),
                    }
                )
    if logs_root.exists():
        for path in sorted(logs_root.glob("*.jsonl")):
            try:
                lines = path.read_text(encoding="utf-8").splitlines()
            except OSError:
                continue
            for raw in lines:
                try:
                    item = json.loads(raw)
                except json.JSONDecodeError:
                    continue
                if str(item.get("level", "")).casefold() != "error":
                    continue
                reason = item.get("reason") or item.get("error") or item.get("message") or "unknown failure"
                events.append(
                    {
                        "script": str(item.get("script", path.stem)),
                        "stage": str(item.get("stage", "runtime")),
                        "reason": str(reason),
                        "source": str(path.relative_to(root)),
                    }
                )
    return events


def classify_pattern(reason: str) -> tuple[str, list[str], list[str]]:
    normalized = normalize_reason(reason)
    if "name resolution" in normalized or "temporary failure in name resolution" in normalized:
        return (
            "network-resolution-failure",
            [
                "add environment preflight for network or DNS reachability before source sync",
                "downgrade source update checks to expected-environment warnings when network is unavailable",
            ],
            ["preflight", "docs/runbook", "observability"],
        )
    if "approved memory roots" in normalized or "must stay within approved" in normalized:
        return (
            "memory-root-policy-failure",
            [
                "surface the approved roots earlier in command help and validation errors",
                "add a guardrail that suggests the correct candidate directory before ingest runs",
            ],
            ["validation", "memory", "guardrail"],
        )
    if "principal" in normalized or "permission" in normalized or "auth" in normalized:
        return (
            "identity-or-permission-failure",
            [
                "split governance-time identity checks from runtime deploy checks",
                "add stack-specific preflight for principals, secrets, and workspace resources",
            ],
            ["preflight", "governance", "deploy"],
        )
    if "manifest" in normalized or "schema" in normalized:
        return (
            "manifest-schema-failure",
            [
                "add local schema validation before deploy",
                "promote the schema issue into a regression test or validation command",
            ],
            ["validation", "deploy", "regression"],
        )
    return (
        "general-recurrent-failure",
        [
            "capture a repo-local runbook entry with reproduction and mitigation",
            "decide whether the failure should become a validator or regression test",
        ],
        ["runbook", "guardrail"],
    )


def build_patterns(events: list[dict[str, str]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for event in events:
        key = (event["script"], normalize_reason(event["reason"]))
        grouped[key].append(event)
    patterns: list[dict[str, object]] = []
    for (script, normalized_reason), items in sorted(grouped.items(), key=lambda item: len(item[1]), reverse=True):
        class_id, recommendations, tags = classify_pattern(normalized_reason)
        patterns.append(
            {
                "pattern_id": f"{script}:{class_id}",
                "script": script,
                "normalized_reason": normalized_reason,
                "occurrences": len(items),
                "stages": sorted({item["stage"] for item in items}),
                "sources": sorted({item["source"] for item in items}),
                "recommended_actions": recommendations,
                "tags": sorted(set(tags + [script, class_id])),
            }
        )
    return patterns


def build_memory_candidates(patterns: list[dict[str, object]]) -> list[dict[str, object]]:
    candidates: list[dict[str, object]] = []
    for pattern in patterns:
        if int(pattern["occurrences"]) < 2:
            continue
        candidates.append(
            {
                "memory_type": "procedural",
                "scope": {"type": "project", "value": "agentcodex"},
                "procedure_title": f"Failure pattern: {pattern['pattern_id']}",
                "trigger": f"repeated failure in {pattern['script']}: {pattern['normalized_reason']}",
                "steps": list(pattern["recommended_actions"]),
                "constraints": ["promote only after human review", "prefer repo-local validation before external runtime retries"],
                "success_signals": ["failure is detected earlier", "operator sees recommended next action immediately"],
                "failure_signals": ["same failure repeats without new guardrail or runbook"],
                "source": "failure-pattern-promote",
                "approval_state": "proposed",
                "updated_at": now_iso().replace("+00:00", "Z"),
                "tags": list(pattern["tags"]),
                "owner": "agentcodex",
            }
        )
    return candidates


def write_outputs(root: Path, payload: dict[str, object], candidates: list[dict[str, object]]) -> tuple[Path, Path | None]:
    report_path = root / ".agentcodex" / "reports" / "failure-pattern-promotion.md"
    lines = [
        "# Failure Pattern Promotion Report",
        "",
        f"- generated_at: {payload['generated_at']}",
        f"- target_root: {payload['target_root']}",
        f"- detected_patterns: {len(payload['patterns'])}",
        f"- promoted_candidates: {len(candidates)}",
        "",
    ]
    for pattern in payload["patterns"]:
        lines.extend(
            [
                f"## {pattern['pattern_id']}",
                "",
                f"- script: {pattern['script']}",
                f"- occurrences: {pattern['occurrences']}",
                f"- stages: {', '.join(pattern['stages'])}",
                f"- normalized_reason: {pattern['normalized_reason']}",
                "- recommended_actions:",
            ]
        )
        for action in pattern["recommended_actions"]:
            lines.append(f"  - {action}")
        lines.append("")
    report_path.write_text("\n".join(lines), encoding="utf-8")

    candidates_path: Path | None = None
    if candidates:
        candidates_root = root / ".agentcodex" / "memory" / "candidates"
        candidates_root.mkdir(parents=True, exist_ok=True)
        candidates_path = candidates_root / f"failure-patterns-{now_iso()[:10]}.json"
        candidates_path.write_text(json.dumps(candidates, indent=2) + "\n", encoding="utf-8")
    return report_path, candidates_path


def main() -> int:
    args = sys.argv[1:]
    target_arg: str | None = None
    as_json = False
    for arg in args:
        if arg == "--json":
            as_json = True
        elif target_arg is None:
            target_arg = arg
        else:
            return print_usage()
    root = resolve_root(target_arg)
    if not root.exists():
        print(f"Target does not exist: {root}", file=sys.stderr)
        return 1
    ensure_agentcodex_dirs(root)
    events = load_failure_events(root)
    patterns = build_patterns(events)
    candidates = build_memory_candidates(patterns)
    payload = {
        "generated_at": now_iso(),
        "target_root": str(root),
        "patterns": patterns,
    }
    report_path, candidates_path = write_outputs(root, payload, candidates)
    state = load_project_state(root)
    state["failure_patterns"] = {
        "patterns": patterns,
        "last_report": str(report_path.relative_to(root)),
        "candidate_path": str(candidates_path.relative_to(root)) if candidates_path else "",
    }
    state_path = save_project_state(root, state)
    payload["report_path"] = str(report_path.relative_to(root))
    payload["candidate_path"] = str(candidates_path.relative_to(root)) if candidates_path else ""
    payload["state_path"] = str(state_path.relative_to(root))
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("# Failure Pattern Promote")
        print()
        print(f"- detected_patterns: {len(patterns)}")
        print(f"- promoted_candidates: {len(candidates)}")
        print(f"- report_path: {payload['report_path']}")
        if payload["candidate_path"]:
            print(f"- candidate_path: {payload['candidate_path']}")
        print(f"- state_path: {payload['state_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
