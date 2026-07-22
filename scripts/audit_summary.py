#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
OBS_ROOT = ROOT / ".agentcodex" / "observability"
REPORTS_ROOT = ROOT / ".agentcodex" / "reports" / "audit"


def collect_run_stats() -> dict[str, object]:
    runs_root = OBS_ROOT / "runs"
    counter = Counter()
    statuses = Counter()
    if runs_root.exists():
        for path in runs_root.glob("*.json"):
            payload = json.loads(path.read_text(encoding="utf-8"))
            counter[payload.get("script", "unknown")] += 1
            statuses[payload.get("status", "unknown")] += 1
    return {
        "runs_by_script": dict(counter),
        "runs_by_status": dict(statuses),
        "total_runs": sum(counter.values()),
    }


def collect_failure_stats() -> dict[str, object]:
    failures_path = OBS_ROOT / "failures" / "source-failures.json"
    if not failures_path.exists():
        return {"source_failures": 0, "failures_by_stage": {}}
    payload = json.loads(failures_path.read_text(encoding="utf-8"))
    stage_counter = Counter()
    for item in payload:
        stage_counter[item.get("stage", "unknown")] += 1
    return {
        "source_failures": len(payload),
        "failures_by_stage": dict(stage_counter),
    }


def write_report(payload: dict[str, object]) -> Path:
    REPORTS_ROOT.mkdir(parents=True, exist_ok=True)
    path = REPORTS_ROOT / "audit-summary.md"
    lines = [
        "# Audit Summary",
        "",
        f"- generated_at: {payload['generated_at']}",
        f"- total_runs: {payload['total_runs']}",
        f"- source_failures: {payload['source_failures']}",
        "",
        "## Runs By Script",
        "",
    ]
    for key, value in sorted(payload["runs_by_script"].items()):
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Runs By Status", ""])
    for key, value in sorted(payload["runs_by_status"].items()):
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Failures By Stage", ""])
    if not payload["failures_by_stage"]:
        lines.append("- none")
    else:
        for key, value in sorted(payload["failures_by_stage"].items()):
            lines.append(f"- {key}: {value}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def main() -> int:
    as_json = len(sys.argv) == 2 and sys.argv[1] == "--json"
    if len(sys.argv) > 2 or (len(sys.argv) == 2 and not as_json):
        print("Usage: python3 scripts/agentcodex.py audit-summary [--json]")
        return 1
    payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        **collect_run_stats(),
        **collect_failure_stats(),
    }
    report_path = write_report(payload)
    payload["report_path"] = str(report_path.relative_to(ROOT))
    if as_json:
        print(json.dumps(payload, indent=2))
    else:
        print("# Audit Summary")
        print()
        print(f"- total_runs: {payload['total_runs']}")
        print(f"- source_failures: {payload['source_failures']}")
        print(f"- report_path: {payload['report_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
