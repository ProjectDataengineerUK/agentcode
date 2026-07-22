from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from agentcodex_cli.dispatcher import dispatch


def installed_runtime_roots() -> list[Path]:
    module_path = Path(__file__).resolve()
    prefixes = {
        Path(sys.prefix),
        Path(sys.base_prefix),
        module_path.parents[3] if len(module_path.parents) > 3 else module_path.parent,
    }
    candidates: list[Path] = []
    for prefix in prefixes:
        candidates.append(prefix / "share" / "agentcodex")
    return candidates


def resolve_repo_root() -> Path:
    current = Path(__file__).resolve()
    for candidate in [current, *current.parents]:
        if (candidate / "pyproject.toml").exists() and (candidate / ".agentcodex").exists() and (candidate / "scripts").exists():
            return candidate
    for candidate in installed_runtime_roots():
        if (candidate / ".agentcodex").exists() and (candidate / "scripts").exists():
            return candidate
    raise RuntimeError("Could not resolve AgentCodex runtime root")


def run(script_name: str, args: list[str]) -> int:
    root = resolve_repo_root()
    script_path = root / "scripts" / script_name
    if not script_path.exists():
        print(f"Missing script: {script_path}", file=sys.stderr)
        return 1
    current_dir = Path.cwd()
    run_cwd = current_dir if (current_dir / ".agentcodex").exists() else root
    result = subprocess.run(
        [sys.executable, str(script_path), *args],
        cwd=str(run_cwd),
    )
    return int(result.returncode)


def main() -> int:
    return dispatch(sys.argv[1:], run, "agentcodex")


if __name__ == "__main__":
    raise SystemExit(main())
