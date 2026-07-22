#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from state_utils import ensure_agentcodex_dirs, load_approval_gates, now_iso, resolve_root, save_approval_gates


VALID_STATUSES = {"pending", "approved", "dispatched", "executed", "expired", "invalidated"}


def print_usage() -> int:
    print(
        "Usage: python3 scripts/agentcodex.py approval-gate-sync "
        "[target-project-dir] <gate-id> <pending|approved|dispatched|executed|expired|invalidated> "
        "[--commit <sha>] [--run <id-or-url>] [--note <text>] [--json]"
    )
    return 1


def parse_args(argv: list[str]) -> tuple[Path, str, str, str, str, str, bool] | None:
    target_arg: str | None = None
    gate_id = ""
    status = ""
    commit = ""
    run_ref = ""
    note = ""
    as_json = False
    positionals: list[str] = []
    index = 0
    while index < len(argv):
        current = argv[index]
        if current == "--json":
            as_json = True
            index += 1
            continue
        if current == "--commit" and index + 1 < len(argv):
            commit = argv[index + 1].strip()
            index += 2
            continue
        if current == "--run" and index + 1 < len(argv):
            run_ref = argv[index + 1].strip()
            index += 2
            continue
        if current == "--note" and index + 1 < len(argv):
            note = argv[index + 1].strip()
            index += 2
            continue
        if current.startswith("--"):
            return None
        positionals.append(current)
        index += 1

    if len(positionals) == 2:
        gate_id, status = positionals
    elif len(positionals) == 3:
        target_arg, gate_id, status = positionals
    else:
        return None
    if status not in VALID_STATUSES:
        return None
    return resolve_root(target_arg), gate_id, status, commit, run_ref, note, as_json


def write_report(root: Path, payload: dict[str, object]) -> Path:
    path = root / ".agentcodex" / "reports" / "approval-gates.md"
    lines = [
        "# Approval Gate Report",
        "",
        f"- generated_at: {payload['generated_at']}",
        f"- target_root: {payload['target_root']}",
        "",
    ]
    for gate_id, item in payload["gates"].items():
        lines.extend(
            [
                f"## {gate_id}",
                "",
                f"- status: {item['status']}",
                f"- updated_at: {item['updated_at']}",
                f"- commit: {item.get('commit', '') or 'n/a'}",
                f"- run: {item.get('run', '') or 'n/a'}",
                f"- note: {item.get('note', '') or 'n/a'}",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> int:
    parsed = parse_args(sys.argv[1:])
    if parsed is None:
        return print_usage()
    root, gate_id, status, commit, run_ref, note, as_json = parsed
    if not root.exists():
        print(f"Target does not exist: {root}", file=sys.stderr)
        return 1

    ensure_agentcodex_dirs(root)
    payload = load_approval_gates(root)
    gates = dict(payload.get("gates", {}))
    gates[gate_id] = {
        "status": status,
        "updated_at": now_iso(),
        "commit": commit,
        "run": run_ref,
        "note": note,
    }
    payload["gates"] = gates
    report_path = write_report(root, {"generated_at": now_iso(), "target_root": str(root), "gates": gates})
    state_path = save_approval_gates(root, payload)
    response = {
        "generated_at": now_iso(),
        "target_root": str(root),
        "gate_id": gate_id,
        "status": status,
        "commit": commit,
        "run": run_ref,
        "note": note,
        "report_path": str(report_path.relative_to(root)),
        "state_path": str(state_path.relative_to(root)),
    }
    if as_json:
        print(json.dumps(response, indent=2, sort_keys=True))
    else:
        print("# Approval Gate Sync")
        print()
        print(f"- gate_id: {gate_id}")
        print(f"- status: {status}")
        print(f"- report_path: {response['report_path']}")
        print(f"- state_path: {response['state_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
