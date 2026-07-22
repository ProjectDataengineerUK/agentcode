#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path


SOURCE_ROOT = Path(__file__).resolve().parent.parent


def resolve_project_root() -> Path:
    current = Path.cwd().resolve()
    for candidate in [current, *current.parents]:
        if (candidate / ".agentcodex").exists():
            return candidate
    return SOURCE_ROOT


def slugify(value: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9]+", "_", value.strip())
    normalized = re.sub(r"_+", "_", normalized).strip("_")
    return normalized.upper()


def print_usage() -> int:
    print(
        "Usage: python3 scripts/agentcodex.py new-context <feature-or-topic> "
        "[--kind feature|session] [--owner <owner>]"
    )
    return 1


def main() -> int:
    args = sys.argv[1:]
    if not args:
        return print_usage()

    kind = "feature"
    owner = "agentcodex"
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
        if arg == "--owner":
            if i + 1 >= len(args):
                return print_usage()
            owner = args[i + 1].strip()
            i += 2
            continue
        return print_usage()

    raw_scope = " ".join(scope_parts).strip()
    if not raw_scope:
        return print_usage()

    if kind not in {"feature", "session"}:
        print("Invalid --kind. Expected 'feature' or 'session'.", file=sys.stderr)
        return 1

    project_root = resolve_project_root()
    template_path = project_root / ".agentcodex" / "templates" / "CONTEXT_HISTORY_TEMPLATE.md"
    history_dir = project_root / ".agentcodex" / "history"
    scope = slugify(raw_scope)
    if not scope:
        print("Feature or topic must contain at least one alphanumeric character.", file=sys.stderr)
        return 1

    today = date.today().isoformat()
    prefix = "CONTEXT" if kind == "feature" else "SESSION"
    filename = f"{prefix}_{scope}_{today}.md"
    destination = history_dir / filename

    if not template_path.exists():
        print(f"Missing context history template: {template_path}", file=sys.stderr)
        return 1

    history_dir.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        print(f"History entry already exists: {destination}", file=sys.stderr)
        return 1

    content = template_path.read_text(encoding="utf-8")
    content = content.replace("{SCOPE}", scope)
    content = content.replace("{KIND}", kind)
    content = content.replace("{OWNER}", owner)
    content = content.replace("{DATE}", today)
    content = content.replace("{FILENAME}", filename)
    destination.write_text(content, encoding="utf-8")

    print(f"Created context history entry: {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
