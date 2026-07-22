#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

STRUCTURE_GROUPS = {
    "control_plane": [
        ".agentcodex/reports",
        ".agentcodex/history",
        ".agentcodex/archive",
        ".agentcodex/workflows",
        ".agentcodex/state",
        ".agentcodex/observability",
        ".agentcodex/memory",
    ],
    "project_runtime": [
        ".agentcodex/features",
        ".agentcodex/ops",
        ".agentcodex/commands",
        ".agentcodex/templates",
    ],
    "knowledge_routing": [
        ".agentcodex/kb",
        ".agentcodex/routing",
        ".agentcodex/roles",
        ".agentcodex/registry",
        ".agentcodex/maturity",
    ],
    "bootstrap_distribution": [
        ".agentcodex/bootstrap",
        ".codex",
        "plugins/agentcodex",
        "src/agentcodex_cli",
        "scripts",
    ],
    "source_reference": [
        ".agentcodex/imports",
        ".agentcodex/cache",
    ],
}


def print_usage() -> int:
    print("Usage: python3 scripts/agentcodex.py project-structure [--json]")
    return 1


def summarize() -> dict[str, object]:
    groups: dict[str, list[dict[str, object]]] = {}
    for name, paths in STRUCTURE_GROUPS.items():
        items: list[dict[str, object]] = []
        for rel in paths:
            path = ROOT / rel
            items.append(
                {
                    "path": rel,
                    "exists": path.exists(),
                    "kind": "dir" if path.is_dir() else "file" if path.is_file() else "missing",
                }
            )
        groups[name] = items
    return {
        "root": str(ROOT),
        "groups": groups,
    }


def write_report(payload: dict[str, object]) -> Path:
    path = ROOT / ".agentcodex" / "reports" / "project-structure.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Project Structure Report",
        "",
        f"- root: {payload['root']}",
        "",
    ]
    for group, items in payload["groups"].items():
        lines.extend([f"## {group}", ""])
        for item in items:
            lines.append(f"- {item['path']}: {item['kind']}")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> int:
    as_json = len(sys.argv) == 2 and sys.argv[1] == "--json"
    if len(sys.argv) > 2 or (len(sys.argv) == 2 and not as_json):
        return print_usage()
    payload = summarize()
    report_path = write_report(payload)
    payload["report_path"] = str(report_path.relative_to(ROOT))
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("# Project Structure")
        print()
        for group, items in payload["groups"].items():
            present = sum(1 for item in items if item["exists"])
            print(f"- {group}: {present}/{len(items)} paths present")
        print(f"- report_path: {payload['report_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
