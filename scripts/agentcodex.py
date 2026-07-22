#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from agentcodex_cli.dispatcher import dispatch  # noqa: E402


def run(script_name: str, args: list[str]) -> int:
    script_path = SCRIPTS / script_name
    if not script_path.exists():
        print(f"Missing script: {script_path}", file=sys.stderr)
        return 1
    current_dir = Path.cwd()
    run_cwd = current_dir if (current_dir / ".agentcodex").exists() else ROOT
    result = subprocess.run(
        [sys.executable, str(script_path), *args],
        cwd=str(run_cwd),
    )
    return int(result.returncode)


def main() -> int:
    return dispatch(sys.argv[1:], run, "python3 scripts/agentcodex.py")


if __name__ == "__main__":
    raise SystemExit(main())
