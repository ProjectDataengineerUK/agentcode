#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from state_utils import (
    ensure_agentcodex_dirs,
    latest_matching,
    load_project_state,
    max_evidence,
    now_iso,
    resolve_root,
    save_project_state,
)


ARCHITECTURE_PATTERNS = [
    re.compile(r"primary_architecture\s*:\s*(.+)", re.IGNORECASE),
    re.compile(r"architecture\s*:\s*(.+)", re.IGNORECASE),
    re.compile(r"surface\s*:\s*(.+)", re.IGNORECASE),
]
EVIDENCE_PATTERNS = {
    "runtime-pass": [re.compile(r"\bruntime-pass\b", re.IGNORECASE), re.compile(r"\bruntime validated\b", re.IGNORECASE)],
    "deploy-pass": [re.compile(r"\bdeploy-pass\b", re.IGNORECASE), re.compile(r"\bdeploy(ed)?\s+(ok|done|passed|green)\b", re.IGNORECASE)],
    "ci-pass": [re.compile(r"\bci-pass\b", re.IGNORECASE), re.compile(r"\b(ci|github actions|pipeline)\s+(ok|passed|green)\b", re.IGNORECASE)],
    "local-pass": [re.compile(r"\blocal-pass\b", re.IGNORECASE), re.compile(r"\btests?\s+passing\b", re.IGNORECASE)],
}
POSITIVE_STATUS_RE = re.compile(r"\b(done|complete|completed|shipped|ready|passed)\b", re.IGNORECASE)
NEGATIVE_STATUS_RE = re.compile(r"\b(partial|missing|blocked|failed|pending|in progress|todo)\b", re.IGNORECASE)


def print_usage() -> int:
    print("Usage: python3 scripts/agentcodex.py status-reconcile [target-project-dir] [--json]")
    return 1


def candidate_artifacts(root: Path) -> list[Path]:
    items: list[Path] = []
    for rel in [
        "AGENTS.md",
        ".agentcodex/history/CONTEXT-HISTORY.md",
        ".agentcodex/ops/project-standard-status.md",
        ".agentcodex/reports/project-readiness-report.md",
        ".agentcodex/reports/start-maturity-report.md",
    ]:
        path = root / rel
        if path.exists():
            items.append(path)

    for pattern in [
        ".agentcodex/reports/status-handoff*.md",
        ".agentcodex/reports/final-delivery-report*.md",
        ".agentcodex/reports/BUILD_REPORT*.md",
        ".agentcodex/history/CONTEXT_*.md",
    ]:
        match = latest_matching(root, pattern)
        if match is not None:
            items.append(match)
    return items


def normalize_architecture(value: str) -> str:
    lowered = value.strip().casefold()
    lowered = re.sub(r"`", "", lowered)
    lowered = re.sub(r"\s+", " ", lowered)
    return lowered.strip(" -.")


def extract_architecture_signals(text: str) -> list[str]:
    signals: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        for pattern in ARCHITECTURE_PATTERNS:
            match = pattern.search(stripped)
            if match:
                candidate = normalize_architecture(match.group(1))
                if len(candidate) >= 8:
                    signals.append(candidate)
        if "databricks" in stripped.casefold() and any(token in stripped.casefold() for token in ("frontend", "surface", "backend", "apps")):
            candidate = normalize_architecture(stripped)
            if len(candidate) >= 8:
                signals.append(candidate)
    return signals


def extract_evidence_level(text: str) -> str:
    hits: list[str] = []
    for level, patterns in EVIDENCE_PATTERNS.items():
        if any(pattern.search(text) for pattern in patterns):
            hits.append(level)
    return max_evidence(hits)


def extract_status_tone(text: str) -> str:
    positive = POSITIVE_STATUS_RE.search(text) is not None
    negative = NEGATIVE_STATUS_RE.search(text) is not None
    if positive and negative:
        return "mixed"
    if positive:
        return "positive"
    if negative:
        return "negative"
    return "neutral"


def summarize_artifact(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8", errors="replace")
    architecture = sorted(set(extract_architecture_signals(text)))
    evidence_level = extract_evidence_level(text)
    tone = extract_status_tone(text)
    return {
        "path": str(path),
        "modified_at": now_iso() if not path.exists() else None,
        "architecture_signals": architecture,
        "evidence_level": evidence_level,
        "status_tone": tone,
    }


def artifact_timestamp(path: Path) -> str:
    return now_iso() if not path.exists() else Path(path).stat().st_mtime_ns.__str__()


def build_payload(root: Path) -> dict[str, object]:
    artifacts = []
    architecture_map: dict[str, list[str]] = {}
    evidence_levels: list[str] = []
    tones: set[str] = set()

    for path in candidate_artifacts(root):
        summary = summarize_artifact(path)
        summary["modified_at"] = artifact_timestamp(path)
        artifacts.append(summary)
        for value in summary["architecture_signals"]:
            architecture_map.setdefault(str(value), []).append(str(path.relative_to(root)))
        evidence_levels.append(str(summary["evidence_level"]))
        tones.add(str(summary["status_tone"]))

    contradictions: list[str] = []
    if len(architecture_map) > 1:
        contradictions.append("multiple architecture claims detected")
    if "positive" in tones and "negative" in tones:
        contradictions.append("mixed completion signals detected")

    canonical_architecture = ""
    if architecture_map:
        canonical_architecture = max(
            architecture_map.items(),
            key=lambda item: (len(item[1]), item[0]),
        )[0]

    return {
        "generated_at": now_iso(),
        "target_root": str(root),
        "canonical_architecture": canonical_architecture,
        "architecture_candidates": architecture_map,
        "max_evidence_level": max_evidence(evidence_levels),
        "contradictions": contradictions,
        "needs_reconciliation": bool(contradictions),
        "artifacts": artifacts,
    }


def write_report(root: Path, payload: dict[str, object]) -> Path:
    path = root / ".agentcodex" / "reports" / "status-reconcile.md"
    lines = [
        "# Status Reconciliation Report",
        "",
        f"- generated_at: {payload['generated_at']}",
        f"- target_root: {payload['target_root']}",
        f"- canonical_architecture: {payload['canonical_architecture'] or 'unknown'}",
        f"- max_evidence_level: {payload['max_evidence_level']}",
        f"- needs_reconciliation: {str(payload['needs_reconciliation']).lower()}",
        "",
        "## Contradictions",
        "",
    ]
    contradictions = payload["contradictions"]
    if contradictions:
        for item in contradictions:
            lines.append(f"- {item}")
    else:
        lines.append("- none")

    lines.extend(["", "## Architecture Candidates", ""])
    architecture_candidates = payload["architecture_candidates"]
    if architecture_candidates:
        for architecture, sources in architecture_candidates.items():
            lines.append(f"- {architecture}")
            for source in sources:
                lines.append(f"  - source: {source}")
    else:
        lines.append("- none detected")

    lines.extend(["", "## Artifact Signals", ""])
    for item in payload["artifacts"]:
        lines.append(f"### {Path(str(item['path'])).name}")
        lines.append("")
        lines.append(f"- path: {Path(str(item['path'])).relative_to(root)}")
        lines.append(f"- modified_at: {item['modified_at']}")
        lines.append(f"- evidence_level: {item['evidence_level']}")
        lines.append(f"- status_tone: {item['status_tone']}")
        if item["architecture_signals"]:
            lines.append(f"- architecture_signals: {', '.join(item['architecture_signals'])}")
        else:
            lines.append("- architecture_signals: none")
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


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
    payload = build_payload(root)
    report_path = write_report(root, payload)

    state = load_project_state(root)
    state["architecture"] = {
        "canonical": payload["canonical_architecture"],
        "candidates": payload["architecture_candidates"],
    }
    state["evidence"] = {"max_level": payload["max_evidence_level"]}
    state["reconciliation"] = {
        "needs_reconciliation": payload["needs_reconciliation"],
        "contradictions": payload["contradictions"],
        "last_report": str(report_path.relative_to(root)),
    }
    state_path = save_project_state(root, state)
    payload["report_path"] = str(report_path.relative_to(root))
    payload["state_path"] = str(state_path.relative_to(root))

    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("# Status Reconcile")
        print()
        print(f"- canonical_architecture: {payload['canonical_architecture'] or 'unknown'}")
        print(f"- max_evidence_level: {payload['max_evidence_level']}")
        print(f"- needs_reconciliation: {str(payload['needs_reconciliation']).lower()}")
        print(f"- report_path: {payload['report_path']}")
        print(f"- state_path: {payload['state_path']}")
        if payload["contradictions"]:
            print("- contradictions:")
            for item in payload["contradictions"]:
                print(f"  - {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
