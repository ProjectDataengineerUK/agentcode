#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
OBS_LOGS_ROOT = ROOT / ".agentcodex" / "observability" / "logs"
ARTIFACTS_ROOT = ROOT / ".agentcodex" / "memory" / "candidates"
REPORTS_ROOT = ROOT / ".agentcodex" / "reports" / "memory"


def load_log_events(limit_per_file: int = 20) -> list[dict]:
    items: list[dict] = []
    if not OBS_LOGS_ROOT.exists():
        return items
    for path in sorted(OBS_LOGS_ROOT.glob("*.jsonl")):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        for raw in lines[-limit_per_file:]:
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                continue
            payload["_source_log"] = str(path.relative_to(ROOT))
            items.append(payload)
    return items


def to_candidates(events: list[dict]) -> list[dict]:
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    candidates: list[dict] = []
    for index, event in enumerate(events, start=1):
        script = str(event.get("script", "unknown"))
        status = str(event.get("status", "unknown"))
        stage = str(event.get("stage", "runtime"))
        summary = event.get("summary") or event.get("message") or f"{script} reported {status}"
        references = [event["_source_log"]]
        if "run_path" in event:
            references.append(str(event["run_path"]))
        candidates.append(
            {
                "memory_type": "episodic",
                "scope": {"type": "project", "value": "agentcodex"},
                "candidate_id": f"log-knowledge:{index}",
                "event_title": f"log event from {script}",
                "event_summary": str(summary),
                "actors": ["sentinel", script],
                "timestamp": str(event.get("timestamp", now)),
                "outcome": f"status={status}; stage={stage}",
                "references": references,
                "importance": 0.62 if status == "success" else 0.81,
                "tags": ["logs", "sentinel", script, status, stage],
                "sensitivity": "internal",
                "retention_policy": "episodic-default",
                "owner": "agentcodex",
            }
        )
    return candidates


def write_outputs(candidates: list[dict]) -> tuple[Path, Path]:
    ARTIFACTS_ROOT.mkdir(parents=True, exist_ok=True)
    REPORTS_ROOT.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y-%m-%d")
    json_path = ARTIFACTS_ROOT / f"log-knowledge-extract-{stamp}.json"
    report_path = REPORTS_ROOT / "log-knowledge-report.md"
    json_path.write_text(json.dumps(candidates, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Log Knowledge Extract Report",
        "",
        f"- generated_at: {datetime.now(UTC).isoformat()}",
        f"- extracted: {len(candidates)}",
        f"- candidates_path: {json_path.relative_to(ROOT)}",
        "",
        "## Candidates",
        "",
    ]
    if not candidates:
        lines.append("- none")
    else:
        for item in candidates[:25]:
            lines.append(f"- `{item['candidate_id']}`: {item['event_summary']}")
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, report_path


def main() -> int:
    as_json = len(sys.argv) == 2 and sys.argv[1] == "--json"
    if len(sys.argv) > 2 or (len(sys.argv) == 2 and not as_json):
        print("Usage: python3 scripts/agentcodex.py extract-log-knowledge [--json]")
        return 1
    candidates = to_candidates(load_log_events())
    json_path, report_path = write_outputs(candidates)
    payload = {
        "candidates": candidates,
        "candidates_path": str(json_path.relative_to(ROOT)),
        "report_path": str(report_path.relative_to(ROOT)),
    }
    if as_json:
        print(json.dumps(payload, indent=2))
    else:
        print("# Log Knowledge Extract")
        print()
        print(f"- extracted: {len(candidates)}")
        print(f"- candidates_path: {payload['candidates_path']}")
        print(f"- report_path: {payload['report_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
