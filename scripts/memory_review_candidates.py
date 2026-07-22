#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from memory_candidate_flow import build_review, display_path, load_candidates, write_report


def main() -> int:
    args = sys.argv[1:]
    candidate_path = None
    as_json = False
    if args:
        if len(args) == 1 and args[0] == "--json":
            as_json = True
        elif len(args) == 1:
            candidate_path = args[0]
        elif len(args) == 2 and args[1] == "--json":
            candidate_path = args[0]
            as_json = True
        else:
            print("Usage: python3 scripts/agentcodex.py memory-review-candidates [candidate-file] [--json]")
            return 1

    try:
        source_path, candidates = load_candidates(path=None if candidate_path is None else Path(candidate_path).resolve())
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    review_path, payload = build_review(source_path, candidates)
    report = write_report(
        "review-candidates-report.md",
        [
            "# Memory Candidate Review Report",
            "",
            f"- source_candidates: {display_path(source_path)}",
            f"- review_path: {display_path(review_path)}",
            f"- candidates: {len(candidates)}",
        ],
    )
    result = {
        "source_candidates": display_path(source_path),
        "review_path": display_path(review_path),
        "report_path": display_path(report),
        "candidates": len(candidates),
    }
    if as_json:
        print(json.dumps(result, indent=2))
    else:
        print("# Memory Candidate Review")
        print()
        print(f"- source_candidates: {result['source_candidates']}")
        print(f"- review_path: {result['review_path']}")
        print(f"- report_path: {result['report_path']}")
        print(f"- candidates: {result['candidates']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
