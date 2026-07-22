#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

from memory_lifecycle import lint_memories


ROOT = Path(__file__).resolve().parent.parent
REPORTS_ROOT = ROOT / ".agentcodex" / "reports" / "memory"


def write_report(issues: list, stats: dict[str, int]) -> Path:
    REPORTS_ROOT.mkdir(parents=True, exist_ok=True)
    path = REPORTS_ROOT / "lint-report.md"
    lines = [
        "# Memory Lint Report",
        "",
        f"- generated_at: {datetime.now(UTC).isoformat()}",
        "",
        "## Stats",
        "",
    ]
    for key, value in stats.items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Issues", ""])
    if not issues:
        lines.append("- none")
    else:
        for issue in issues:
            lines.append(f"- [{issue.severity}] {issue.check} `{issue.memory_id}`: {issue.message}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def main() -> int:
    as_json = len(sys.argv) == 2 and sys.argv[1] == "--json"
    if len(sys.argv) > 2 or (len(sys.argv) == 2 and not as_json):
        print("Usage: python3 scripts/agentcodex.py memory-lint [--json]")
        return 1
    issues, stats = lint_memories()
    report_path = write_report(issues, stats)
    payload = {
        "issues": [issue.__dict__ for issue in issues],
        "stats": stats,
        "report_path": str(report_path.relative_to(ROOT)),
    }
    if as_json:
        print(json.dumps(payload, indent=2))
    else:
        print("# Memory Lint")
        print()
        print(f"- issues: {len(issues)}")
        print(f"- report_path: {payload['report_path']}")
        for issue in issues[:10]:
            print(f"- [{issue.severity}] {issue.check} `{issue.memory_id}`: {issue.message}")
    return 0 if not any(issue.severity == "error" for issue in issues) else 1


if __name__ == "__main__":
    raise SystemExit(main())
