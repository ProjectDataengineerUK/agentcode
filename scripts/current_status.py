#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
STATUS_PATH = ROOT / "docs" / "STATUS.md"


def load_sections() -> tuple[str, dict[str, list[str]]]:
    lines = STATUS_PATH.read_text(encoding="utf-8").splitlines()
    title = lines[0] if lines else "# Status"
    sections: dict[str, list[str]] = {}
    current = "_intro"
    sections[current] = []
    for line in lines[1:]:
        if line.startswith("## "):
            current = line[3:].strip().casefold()
            sections[current] = [line]
            continue
        sections.setdefault(current, []).append(line)
    return title, sections


def print_usage() -> int:
    print("Usage: python3 scripts/agentcodex.py status [section]")
    print("Example: python3 scripts/agentcodex.py status memory")
    return 1


def main() -> int:
    if len(sys.argv) > 2:
        return print_usage()

    title, sections = load_sections()
    if len(sys.argv) == 1:
        print(STATUS_PATH.read_text(encoding="utf-8").rstrip())
        return 0

    requested = sys.argv[1].strip().casefold()
    aliases = {
        "memory": "memory",
        "kb": "kb control plane",
        "kb-control-plane": "kb control plane",
        "control-plane": "control plane",
        "enterprise": "control plane",
        "automation": "automation",
        "project-standard": "project standard",
        "surface": "current surface",
    }
    resolved = aliases.get(requested, requested)
    section = sections.get(resolved)
    if section is None:
        print(f"Unknown status section: {sys.argv[1]}", file=sys.stderr)
        print(f"Available sections: {', '.join(key for key in sections if key != '_intro')}", file=sys.stderr)
        return 1

    print(title)
    print()
    intro = [line for line in sections.get("_intro", []) if line.strip()]
    if intro:
        print("\n".join(intro))
        print()
    print("\n".join(section).rstrip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
