#!/usr/bin/env python3
from __future__ import annotations

import shutil
import tarfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PLUGIN_ROOT = ROOT / "plugins" / "agentcodex"
DIST_ROOT = ROOT / "dist" / "plugins"
STAGE_ROOT = DIST_ROOT / "agentcodex"


def reset_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def copy_plugin_tree(src: Path, dest: Path) -> None:
    ignore = shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo")
    shutil.copytree(src, dest, dirs_exist_ok=True, ignore=ignore)


def build_archive(source_dir: Path, archive_path: Path) -> None:
    with tarfile.open(archive_path, "w:gz") as tar:
        tar.add(source_dir, arcname="agentcodex")


def main() -> int:
    if not (PLUGIN_ROOT / "runtime" / "agentcodex-runtime").exists():
        raise SystemExit(
            "Missing runtime bundle. Run `python3 scripts/build_plugin_runtime.py` before packaging the plugin."
        )

    reset_dir(STAGE_ROOT)
    copy_plugin_tree(PLUGIN_ROOT, STAGE_ROOT)

    archive_path = DIST_ROOT / "agentcodex-plugin-0.1.0.tar.gz"
    DIST_ROOT.mkdir(parents=True, exist_ok=True)
    if archive_path.exists():
        archive_path.unlink()
    build_archive(STAGE_ROOT, archive_path)

    print(f"Packaged AgentCodex plugin at {archive_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
