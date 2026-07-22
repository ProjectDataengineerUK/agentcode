#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
UPDATES_ROOT = ROOT / ".agentcodex" / "kb" / "update-candidates"


def load_update_files() -> list[Path]:
    if not UPDATES_ROOT.exists():
        return []
    return sorted(UPDATES_ROOT.glob("*.json"), key=lambda path: path.stat().st_mtime, reverse=True)


def summarize(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    items = payload.get("items", [])
    return {
        "path": str(path.relative_to(ROOT)),
        "generated_from": payload.get("generated_from", ""),
        "candidates": len(items),
        "suggested_domains": sorted({item.get("suggested_domain", "unknown") for item in items}),
        "status_counts": {
            "proposed": sum(1 for item in items if item.get("status") == "proposed"),
            "other": sum(1 for item in items if item.get("status") != "proposed"),
        },
    }


def main() -> int:
    as_json = len(sys.argv) == 2 and sys.argv[1] == "--json"
    if len(sys.argv) > 2 or (len(sys.argv) == 2 and not as_json):
        print("Usage: python3 scripts/agentcodex.py review-kb-updates [--json]")
        return 1
    summaries = [summarize(path) for path in load_update_files()]
    if as_json:
        print(json.dumps({"updates": summaries}, indent=2))
        return 0
    print("# KB Update Candidates")
    print()
    if not summaries:
        print("- none")
        return 0
    for item in summaries:
        print(
            f"- {item['path']}: candidates={item['candidates']} "
            f"domains={','.join(item['suggested_domains']) or 'none'} "
            f"proposed={item['status_counts']['proposed']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
