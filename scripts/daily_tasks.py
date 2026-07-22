#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from collections import OrderedDict
from datetime import date, datetime, UTC
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
HISTORY_DIR = ROOT / ".agentcodex" / "history"
TEMPLATE_PATH = ROOT / ".agentcodex" / "templates" / "DAILY_TASKS_TEMPLATE.md"

SECTION_NAMES = ("Done", "In Progress", "Backlog")
SECTION_ALIASES = {
    "done": "Done",
    "in-progress": "In Progress",
    "progress": "In Progress",
    "backlog": "Backlog",
}


def print_usage() -> int:
    print(
        "Usage: python3 scripts/agentcodex.py daily-tasks "
        "[--date YYYY-MM-DD] [--owner <owner>] "
        "[--done <task>] [--in-progress <task>] [--backlog <task>]"
    )
    return 1


def now_iso() -> str:
    return datetime.now(UTC).isoformat()


def slugify(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", value.strip())
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    return cleaned.upper() or "TASKS"


def resolve_project_root() -> Path:
    current = Path.cwd().resolve()
    for candidate in [current, *current.parents]:
        if (candidate / ".agentcodex").exists():
            return candidate
    return ROOT


def extract_section(text: str, heading: str) -> list[str]:
    pattern = rf"## {re.escape(heading)}\n(.*?)(?:\n## |\Z)"
    match = re.search(pattern, text, re.DOTALL)
    if not match:
        return []
    values: list[str] = []
    for raw_line in match.group(1).splitlines():
        line = raw_line.strip()
        if line.startswith("- "):
            item = line[2:].strip()
            if item:
                values.append(item)
    return values


def parse_existing(path: Path) -> dict[str, list[str]]:
    if not path.exists():
        return {name: [] for name in SECTION_NAMES}
    text = path.read_text(encoding="utf-8")
    return {name: extract_section(text, name) for name in SECTION_NAMES}


def dedupe(values: list[str]) -> list[str]:
    ordered: OrderedDict[str, None] = OrderedDict()
    for value in values:
        cleaned = value.strip()
        if cleaned:
            ordered.setdefault(cleaned, None)
    return list(ordered.keys())


def merge_tasks(existing: dict[str, list[str]], additions: dict[str, list[str]]) -> dict[str, list[str]]:
    merged = {name: list(existing.get(name, [])) for name in SECTION_NAMES}
    for section in SECTION_NAMES:
        for task in additions.get(section, []):
            task = task.strip()
            if not task:
                continue
            for other in SECTION_NAMES:
                if other != section and task in merged[other]:
                    merged[other] = [item for item in merged[other] if item != task]
            if task not in merged[section]:
                merged[section].append(task)
    for section in SECTION_NAMES:
        merged[section] = dedupe(merged[section])
    return merged


def render_daily_tasks(date_value: str, owner: str, tasks: dict[str, list[str]]) -> str:
    lines = [
        f"# DAILY_TASKS_{date_value.replace('-', '_')}",
        "",
        "## Metadata",
        "",
        f"- date: `{date_value}`",
        f"- owner: `{owner}`",
        f"- updated_at: `{now_iso()}`",
        "",
    ]
    for section in SECTION_NAMES:
        lines.extend([f"## {section}", ""])
        items = tasks.get(section, [])
        if items:
            lines.extend(f"- {item}" for item in items)
        else:
            lines.append("- [none]")
        lines.append("")
    lines.extend(
        [
            "## Notes",
            "",
            "- This file is a daily operational snapshot of done, in-progress, and backlog tasks.",
            "- Move an item between sections by re-running the command with the new status.",
            "",
        ]
    )
    return "\n".join(lines)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def main() -> int:
    project_root = resolve_project_root()
    if not (project_root / ".agentcodex").exists():
        print("AgentCodex is not installed in this directory. Install it before running daily-tasks.", file=sys.stderr)
        return 1

    history_dir = project_root / ".agentcodex" / "history"
    history_dir.mkdir(parents=True, exist_ok=True)

    args = sys.argv[1:]
    if not args:
        return print_usage()

    target_date = date.today().isoformat()
    owner = "agentcodex"
    additions: dict[str, list[str]] = {name: [] for name in SECTION_NAMES}

    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--date":
            if i + 1 >= len(args):
                return print_usage()
            target_date = args[i + 1].strip()
            i += 2
            continue
        if arg == "--owner":
            if i + 1 >= len(args):
                return print_usage()
            owner = args[i + 1].strip()
            i += 2
            continue
        if arg in {"--done", "--in-progress", "--backlog"}:
            if i + 1 >= len(args):
                return print_usage()
            section = SECTION_ALIASES[arg[2:]]
            additions[section].append(args[i + 1].strip())
            i += 2
            continue
        return print_usage()

    filename = f"DAILY_TASKS_{target_date}.md"
    destination = history_dir / filename
    existing = parse_existing(destination)
    merged = merge_tasks(existing, additions)
    write_text(destination, render_daily_tasks(target_date, owner, merged))
    print(f"Updated daily task history: {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
