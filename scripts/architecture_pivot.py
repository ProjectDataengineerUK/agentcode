#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from state_utils import ensure_agentcodex_dirs, load_project_state, now_iso, resolve_root, save_project_state


MANDATORY_ARTIFACTS = [
    "AGENTS.md",
    ".agentcodex/PROJECT_AGENTSCODEX.md",
    ".agentcodex/history/CONTEXT-HISTORY.md",
    ".agentcodex/reports/status-reconcile.md",
    ".agentcodex/ops/project-standard-status.md",
]


def print_usage() -> int:
    print(
        "Usage: python3 scripts/agentcodex.py architecture-pivot "
        "[target-project-dir] --to <new-architecture> [--from <old-architecture>] [--rationale <text>] [--json]"
    )
    return 1


def slugify(value: str) -> str:
    lowered = re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")
    return lowered or "architecture-pivot"


def parse_args(argv: list[str]) -> tuple[Path, str, str, str, bool] | None:
    target_arg: str | None = None
    previous = ""
    new_value = ""
    rationale = ""
    as_json = False
    index = 0
    while index < len(argv):
        current = argv[index]
        if current == "--json":
            as_json = True
            index += 1
            continue
        if current == "--from" and index + 1 < len(argv):
            previous = argv[index + 1].strip()
            index += 2
            continue
        if current == "--to" and index + 1 < len(argv):
            new_value = argv[index + 1].strip()
            index += 2
            continue
        if current == "--rationale" and index + 1 < len(argv):
            rationale = argv[index + 1].strip()
            index += 2
            continue
        if current.startswith("--"):
            return None
        if target_arg is None:
            target_arg = current
            index += 1
            continue
        return None
    if not new_value:
        return None
    return resolve_root(target_arg), previous, new_value, rationale, as_json


def write_report(root: Path, previous: str, new_value: str, rationale: str, pending: list[str]) -> Path:
    reports_dir = root / ".agentcodex" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    path = reports_dir / f"architecture-pivot-{now_iso()[:10]}-{slugify(new_value)[:48]}.md"
    lines = [
        "# Architecture Pivot Report",
        "",
        f"- generated_at: {now_iso()}",
        f"- target_root: {root}",
        f"- previous_architecture: {previous or 'unknown'}",
        f"- new_architecture: {new_value}",
        f"- rationale: {rationale or 'not provided'}",
        "",
        "## Before Vs After",
        "",
        f"- before: {previous or 'unknown'}",
        f"- after: {new_value}",
        "",
        "## Mandatory Propagation Targets",
        "",
    ]
    for artifact in pending:
        lines.append(f"- pending: {artifact}")
    lines.extend(
        [
            "",
            "## Completion Rule",
            "",
            "- Run `agentcodex status-reconcile` after updating the affected artifacts.",
            "- Clear pending targets only after the source files and reports reflect the new architecture.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def main() -> int:
    parsed = parse_args(sys.argv[1:])
    if parsed is None:
        return print_usage()
    root, previous, new_value, rationale, as_json = parsed
    if not root.exists():
        print(f"Target does not exist: {root}", file=sys.stderr)
        return 1

    ensure_agentcodex_dirs(root)
    state = load_project_state(root)
    inferred_previous = previous or str(state.get("architecture", {}).get("canonical", ""))
    pending = [artifact for artifact in MANDATORY_ARTIFACTS if (root / artifact).exists() or artifact == "AGENTS.md"]
    report_path = write_report(root, inferred_previous, new_value, rationale, pending)

    history = list(state.get("history", []))
    history.append(
        {
            "kind": "architecture-pivot",
            "recorded_at": now_iso(),
            "from": inferred_previous,
            "to": new_value,
            "rationale": rationale,
            "report_path": str(report_path.relative_to(root)),
        }
    )
    state["history"] = history[-20:]
    state["architecture"] = {
        "canonical": new_value,
        "previous": inferred_previous,
        "pending_reconciliation": True,
        "pending_artifacts": pending,
        "last_pivot_report": str(report_path.relative_to(root)),
    }
    state["reconciliation"] = {
        "needs_reconciliation": True,
        "contradictions": ["architecture pivot pending propagation"],
        "last_report": str(report_path.relative_to(root)),
    }
    state_path = save_project_state(root, state)
    payload = {
        "target_root": str(root),
        "previous_architecture": inferred_previous,
        "new_architecture": new_value,
        "rationale": rationale,
        "pending_artifacts": pending,
        "report_path": str(report_path.relative_to(root)),
        "state_path": str(state_path.relative_to(root)),
    }
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("# Architecture Pivot")
        print()
        print(f"- previous_architecture: {inferred_previous or 'unknown'}")
        print(f"- new_architecture: {new_value}")
        print(f"- pending_artifacts: {len(pending)}")
        print(f"- report_path: {payload['report_path']}")
        print(f"- state_path: {payload['state_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
