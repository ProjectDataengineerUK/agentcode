#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
KB_ROOT = ROOT / ".agentcodex" / "kb"
IMPORTS_ROOT = ROOT / ".agentcodex" / "imports"
CONFIG_PATH = KB_ROOT / "upstream-sync.json"
ALLOWED_SUBDIRS = ("concepts", "patterns", "reference", "specs")


def print_usage() -> int:
    print(
        "Usage: python3 scripts/agentcodex.py sync-kb-upstreams "
        "[--refresh-imports] [--apply] [--domain <domain>]"
    )
    return 1


def load_config() -> list[dict[str, str]]:
    if not CONFIG_PATH.exists():
        raise SystemExit(f"Missing KB upstream sync config: {CONFIG_PATH}")
    data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    return list(data.get("domains", []))


def copy_file(source: Path, destination: Path, apply: bool, actions: list[str]) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        if source.read_bytes() == destination.read_bytes():
            return
        actions.append(f"update: {destination.relative_to(ROOT)}")
    else:
        actions.append(f"create: {destination.relative_to(ROOT)}")
    if apply:
        shutil.copyfile(source, destination)


def sync_dir(source_dir: Path, dest_dir: Path, apply: bool, actions: list[str]) -> None:
    for source in sorted(source_dir.rglob("*")):
        if not source.is_file():
            continue
        relative = source.relative_to(source_dir)
        copy_file(source, dest_dir / relative, apply, actions)


def refresh_imports() -> None:
    for source in ("agentspec", "ecc"):
        subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "import_upstreams.py"), source],
            cwd=str(ROOT),
            check=True,
        )
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "generate_import_catalog.py")],
        cwd=str(ROOT),
        check=True,
    )


def main() -> int:
    args = sys.argv[1:]
    apply = False
    refresh = False
    selected_domain: str | None = None

    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--apply":
            apply = True
            i += 1
            continue
        if arg == "--refresh-imports":
            refresh = True
            i += 1
            continue
        if arg == "--domain":
            if i + 1 >= len(args):
                return print_usage()
            selected_domain = args[i + 1].strip()
            i += 2
            continue
        return print_usage()

    if refresh:
        refresh_imports()

    actions: list[str] = []
    synced_domains: list[str] = []

    for item in load_config():
        local_domain = item["local_domain"]
        if selected_domain and selected_domain != local_domain:
            continue
        source_root = IMPORTS_ROOT / item["source"] / item["upstream_path"]
        if not source_root.exists():
            print(f"Skipping {local_domain}: missing upstream path {source_root}", file=sys.stderr)
            continue

        target_root = KB_ROOT / local_domain
        target_root.mkdir(parents=True, exist_ok=True)

        for filename in ("index.md", "quick-reference.md"):
            source_file = source_root / filename
            if source_file.exists():
                copy_file(source_file, target_root / filename, apply, actions)

        for subdir in ALLOWED_SUBDIRS:
            source_dir = source_root / subdir
            if source_dir.exists():
                sync_dir(source_dir, target_root / subdir, apply, actions)

        synced_domains.append(local_domain)

    mode = "Applied" if apply else "Dry run"
    print(f"{mode} KB upstream sync for: {', '.join(synced_domains) if synced_domains else 'no domains'}")
    if actions:
        for action in actions:
            print(f"- {action}")
    else:
        print("- no KB changes detected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
