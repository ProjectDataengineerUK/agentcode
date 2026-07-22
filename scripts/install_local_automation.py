#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
HOOKS_DIR = ROOT / ".githooks"


def print_usage() -> int:
    print("Usage: python3 scripts/agentcodex.py install-local-automation")
    return 1


def main() -> int:
    if len(sys.argv) != 1:
        return print_usage()

    git_dir = ROOT / ".git"
    if not git_dir.exists():
        print("Cannot install git hooks: repository root does not contain .git")
        print(f"Hooks are prepared at: {HOOKS_DIR}")
        print("When this directory is inside a git clone, run:")
        print("  git config core.hooksPath .githooks")
        return 1

    for hook in HOOKS_DIR.iterdir():
        if hook.is_file():
            hook.chmod(0o755)

    subprocess.run(
        ["git", "config", "core.hooksPath", ".githooks"],
        cwd=str(ROOT),
        check=True,
    )

    print("Installed local automation hooks.")
    print("Configured: git config core.hooksPath .githooks")
    print("Active hooks:")
    print("- pre-commit -> agentcodex refresh-all --skip-import-catalog")
    print("- post-commit -> agentcodex refresh-all")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
