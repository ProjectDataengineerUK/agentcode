#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

from new_context_history import resolve_project_root, slugify


SECTION_NAMES = [
    "Current State",
    "Decisions",
    "Open Gaps",
    "Next Recommended Step",
    "Resume Prompt",
]


def print_usage() -> int:
    print("Usage: python3 scripts/agentcodex.py resume-context <feature-or-topic> [--kind feature|session]")
    return 1


def collect_section(text: str, heading: str) -> list[str]:
    pattern = rf"## {re.escape(heading)}\n(.*?)(?:\n## |\Z)"
    match = re.search(pattern, text, re.DOTALL)
    if not match:
        return []
    lines: list[str] = []
    for raw_line in match.group(1).splitlines():
        line = raw_line.strip()
        if line:
            lines.append(line)
    return lines


def summarize_lines(lines: list[str]) -> list[str]:
    summary: list[str] = []
    for line in lines:
        if line.startswith("- "):
            value = line[2:].strip()
            if value and not value.endswith(":"):
                summary.append(value)
    return summary[:3]


def main() -> int:
    args = sys.argv[1:]
    if not args:
        return print_usage()

    kind = "feature"
    scope_parts: list[str] = []
    i = 0
    while i < len(args):
        arg = args[i]
        if not arg.startswith("--"):
            scope_parts.append(arg)
            i += 1
            continue
        if arg == "--kind":
            if i + 1 >= len(args):
                return print_usage()
            kind = args[i + 1].strip().lower()
            i += 2
            continue
        return print_usage()

    if kind not in {"feature", "session"}:
        print("Invalid --kind. Expected 'feature' or 'session'.", file=sys.stderr)
        return 1

    raw_scope = " ".join(scope_parts).strip()
    if not raw_scope:
        return print_usage()

    scope = slugify(raw_scope)
    prefix = "CONTEXT" if kind == "feature" else "SESSION"
    pattern = f"{prefix}_{scope}_*.md"

    project_root = resolve_project_root()
    history_dir = project_root / ".agentcodex" / "history"
    if not history_dir.exists():
        print(f"History directory not found: {history_dir}", file=sys.stderr)
        return 1

    matches = sorted(history_dir.glob(pattern))
    if not matches:
        print(f"No context history entry found for {prefix.lower()} scope '{scope}'.", file=sys.stderr)
        return 1

    latest = matches[-1]
    text = latest.read_text(encoding="utf-8")

    print(f"Resume file: {latest}")
    for section in SECTION_NAMES:
        summary = summarize_lines(collect_section(text, section))
        if not summary:
            continue
        print(f"\n{section}:")
        for item in summary:
            print(f"- {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
