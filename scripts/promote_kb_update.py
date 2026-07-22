#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
KB_ROOT = ROOT / ".agentcodex" / "kb"
UPDATES_ROOT = KB_ROOT / "update-candidates"


def slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower())
    return value.strip("-") or "kb-update"


def load_payload(path_arg: str) -> tuple[Path, dict]:
    path = Path(path_arg)
    if not path.is_absolute():
        path = (ROOT / path).resolve()
    try:
        path.relative_to(UPDATES_ROOT.resolve())
    except ValueError:
        raise ValueError(f"candidate file must stay within {UPDATES_ROOT.relative_to(ROOT)}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    return path, payload


def group_key(item: dict) -> tuple[str, str]:
    tags = item.get("tags", [])
    source_tag = next((tag for tag in tags if tag not in {"logs", "sentinel", "runtime", "unknown"}), "general")
    target_dir = item.get("suggested_path", ".agentcodex/kb/operations/observability/")
    return str(target_dir), str(source_tag)


def resolve_target_dir(target_dir_str: str) -> Path:
    raw = Path(target_dir_str)
    if raw.is_absolute():
        raise ValueError("suggested_path must be repo-local, not absolute")
    resolved = (ROOT / raw).resolve()
    try:
        resolved.relative_to(KB_ROOT.resolve())
    except ValueError:
        raise ValueError(f"suggested_path must stay within {KB_ROOT.relative_to(ROOT)}")
    return resolved


def write_grouped_page(target_dir: Path, source_tag: str, items: list[dict]) -> Path:
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / f"candidate-group-{slugify(source_tag)}.md"
    if target_path.exists():
        return target_path

    lines = [
        f"# Candidate Group {source_tag}",
        "",
        "## Purpose",
        "",
        "Capture grouped operational knowledge derived from reviewed Sentinel or observability logs.",
        "",
        "## Signals",
        "",
    ]
    for item in items:
        lines.append(f"- {item.get('summary', '')}")
    lines.extend(["", "## References", ""])
    seen_refs: set[str] = set()
    for item in items:
        for ref in item.get("references", []):
            if ref in seen_refs:
                continue
            seen_refs.add(ref)
            lines.append(f"- {ref}")
    lines.extend(["", "## Local Notes", ""])
    lines.append(f"- grouped candidates: {len(items)}")
    lines.append(f"- source tag: {source_tag}")
    lines.append(f"- promoted from reviewed operational evidence")
    target_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return target_path


def promote(path: Path, payload: dict) -> tuple[list[str], list[Path]]:
    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for item in payload.get("items", []):
        if item.get("status") != "proposed":
            continue
        grouped[group_key(item)].append(item)

    written: list[Path] = []
    promoted_ids: list[str] = []
    for (target_dir_str, source_tag), items in grouped.items():
        target_dir = resolve_target_dir(target_dir_str)
        target_path = write_grouped_page(target_dir, source_tag, items)
        if target_path not in written:
            written.append(target_path)
        for item in items:
            item["status"] = "promoted"
            item["promoted_to"] = str(target_path.relative_to(ROOT))
            promoted_ids.append(item.get("candidate_id", ""))

    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return promoted_ids, written


def main() -> int:
    args = sys.argv[1:]
    as_json = False
    if not args:
        print("Usage: python3 scripts/agentcodex.py promote-kb-update <candidate-file> [--json]")
        return 1
    if args[-1] == "--json":
        as_json = True
        args = args[:-1]
    if len(args) != 1:
        print("Usage: python3 scripts/agentcodex.py promote-kb-update <candidate-file> [--json]")
        return 1
    try:
        path, payload = load_payload(args[0])
        promoted_ids, written = promote(path, payload)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    result = {
        "candidate_file": str(path.relative_to(ROOT)),
        "promoted": len(promoted_ids),
        "promoted_ids": promoted_ids,
        "written_paths": [str(item.relative_to(ROOT)) for item in written],
    }
    if as_json:
        print(json.dumps(result, indent=2))
    else:
        print("# Promote KB Update")
        print()
        print(f"- candidate_file: {result['candidate_file']}")
        print(f"- promoted: {result['promoted']}")
        for item in result["written_paths"]:
            print(f"- written: {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
