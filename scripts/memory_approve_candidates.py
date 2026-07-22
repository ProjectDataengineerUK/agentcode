#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from memory_candidate_flow import (
    approve_all,
    build_kb_update_candidates,
    display_path,
    ensure_within_allowed_roots,
    ingest_approved,
    latest_candidates_file,
    ALLOWED_REVIEW_ROOTS,
    review_path_for,
    write_report,
)


def main() -> int:
    args = sys.argv[1:]
    as_json = False
    review_arg = None
    if args:
        if len(args) == 1 and args[0] == "--json":
            as_json = True
        elif len(args) == 1:
            review_arg = args[0]
        elif len(args) == 2 and args[1] == "--json":
            review_arg = args[0]
            as_json = True
        else:
            print("Usage: python3 scripts/agentcodex.py memory-approve-candidates [review-file] [--json]")
            return 1

    try:
        review_path = Path(review_arg).resolve() if review_arg else review_path_for(latest_candidates_file())
        review_path = ensure_within_allowed_roots(review_path, ALLOWED_REVIEW_ROOTS, "review file")
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    approved = approve_all(review_path)
    kb_updates, kb_update_path = build_kb_update_candidates(review_path)
    ingested_payload, ingested_ids = ingest_approved(review_path)
    report = write_report(
        "approve-candidates-report.md",
        [
            "# Memory Candidate Approval Report",
            "",
            f"- review_path: {display_path(review_path)}",
            f"- approved_changed: {approved['changed']}",
            f"- ingested: {len(ingested_ids)}",
            f"- kb_update_candidates: {len(kb_updates)}",
            f"- kb_update_path: {display_path(kb_update_path)}",
        ],
    )
    result = {
        "review_path": display_path(review_path),
        "approved_changed": approved["changed"],
        "ingested": len(ingested_ids),
        "ingested_ids": ingested_ids,
        "kb_update_candidates": len(kb_updates),
        "kb_update_path": display_path(kb_update_path),
        "report_path": display_path(report),
    }
    if as_json:
        print(json.dumps(result, indent=2))
    else:
        print("# Memory Candidate Approval")
        print()
        print(f"- review_path: {result['review_path']}")
        print(f"- approved_changed: {result['approved_changed']}")
        print(f"- ingested: {result['ingested']}")
        print(f"- kb_update_candidates: {result['kb_update_candidates']}")
        print(f"- kb_update_path: {result['kb_update_path']}")
        print(f"- report_path: {result['report_path']}")
        for memory_id in ingested_ids:
            print(f"- ingested_id: {memory_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
