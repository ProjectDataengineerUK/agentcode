#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

from memory_lifecycle import extract_seed_memories


ROOT = Path(__file__).resolve().parent.parent
REPORTS_ROOT = ROOT / ".agentcodex" / "reports" / "memory"
ARTIFACTS_ROOT = ROOT / ".agentcodex" / "memory" / "candidates"


def write_candidates(payload: list[dict]) -> tuple[Path, Path]:
    REPORTS_ROOT.mkdir(parents=True, exist_ok=True)
    ARTIFACTS_ROOT.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y-%m-%d")
    json_path = ARTIFACTS_ROOT / f"memory-extract-{timestamp}.json"
    md_path = REPORTS_ROOT / "extract-report.md"
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Memory Extract Report",
        "",
        f"- generated_at: {datetime.now(UTC).isoformat()}",
        f"- extracted: {len(payload)}",
        f"- candidates_path: {json_path.relative_to(ROOT)}",
        "",
        "## Candidates",
        "",
    ]
    if not payload:
        lines.append("- none")
    else:
        for item in payload:
            label = item.get("canonical_fact") or item.get("event_summary") or item.get("trigger")
            lines.append(f"- `{item['memory_type']}`: {label}")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, md_path


def main() -> int:
    as_json = len(sys.argv) == 2 and sys.argv[1] == "--json"
    if len(sys.argv) > 2 or (len(sys.argv) == 2 and not as_json):
        print("Usage: python3 scripts/agentcodex.py memory-extract [--json]")
        return 1
    payload = extract_seed_memories()
    json_path, md_path = write_candidates(payload)
    if as_json:
        print(
            json.dumps(
                {
                    "candidates": payload,
                    "candidates_path": str(json_path.relative_to(ROOT)),
                    "report_path": str(md_path.relative_to(ROOT)),
                },
                indent=2,
            )
        )
    else:
        print("# Memory Extract")
        print()
        print(f"- extracted: {len(payload)}")
        print(f"- candidates_path: {json_path.relative_to(ROOT)}")
        print(f"- report_path: {md_path.relative_to(ROOT)}")
        for item in payload:
            label = item.get("canonical_fact") or item.get("event_summary") or item.get("trigger")
            print(f"- {item['memory_type']}: {label}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
