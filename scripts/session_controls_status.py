#!/usr/bin/env python3
from __future__ import annotations

import json
import sys

from session_controls import build_payload


def main() -> int:
    args = sys.argv[1:]
    as_json = len(args) == 1 and args[0] == "--json"
    if args and not as_json:
        print("Usage: python3 scripts/agentcodex.py session-controls [--json]")
        return 1

    payload = build_payload()
    if as_json:
        print(json.dumps(payload, indent=2))
        return 0

    context = payload["context_budget"]
    cost = payload["cost_summary"]
    print("# Session Controls")
    print()
    print("## Context Budget")
    print(f"- status: {context['status']}")
    print(f"- input_tokens: {context['input_tokens']}")
    print(f"- remaining_tokens: {context['remaining_tokens']}")
    print(f"- usage_ratio: {context['usage_ratio']}")
    print()
    print("## Cost Summary")
    print(f"- total_operations: {cost['total_operations']}")
    for tier, count in sorted(cost["by_tier"].items()):
        print(f"- {tier}: {count}")
    print()
    print(f"- report_path: {payload['report_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
