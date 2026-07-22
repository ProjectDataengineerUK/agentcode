#!/usr/bin/env python3
from __future__ import annotations

import stat
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REAL_CODEX = Path("/home/user/.npm-global/bin/codex")
SHIM_TARGET = Path.home() / ".local" / "bin" / "codex"


def usage() -> str:
    return (
        "Usage: python3 scripts/install_codex_command_shim.py [--force] [--real-codex <path>] [--target <path>]\n"
        "   or: python3 scripts/install_codex_command_shim.py --uninstall [--target <path>]\n"
    )


def resolve_args(args: list[str]) -> tuple[str, bool, Path, Path] | None:
    action = "install"
    force = False
    real_codex = DEFAULT_REAL_CODEX
    target = SHIM_TARGET
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--uninstall":
            action = "uninstall"
            i += 1
            continue
        if arg == "--force":
            force = True
            i += 1
            continue
        if arg == "--real-codex":
            if i + 1 >= len(args):
                return None
            real_codex = Path(args[i + 1]).expanduser().resolve()
            i += 2
            continue
        if arg == "--target":
            if i + 1 >= len(args):
                return None
            target = Path(args[i + 1]).expanduser().resolve()
            i += 2
            continue
        return None
    return action, force, real_codex, target


def remove_target(path: Path) -> None:
    if path.exists() or path.is_symlink():
        path.unlink()


def shim_script(real_codex: Path) -> str:
    return f"""#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REAL_CODEX = Path({str(real_codex)!r})
REPO_ROOT = Path({str(ROOT)!r})
PLUGIN_INSTALLER = REPO_ROOT / "scripts" / "install_codex_plugin.py"


def main() -> int:
    args = sys.argv[1:]
    if args == ["install", "agentcodex"]:
        return subprocess.run([sys.executable, str(PLUGIN_INSTALLER), "--force"], cwd=str(REPO_ROOT)).returncode
    if args == ["uninstall", "agentcodex"]:
        return subprocess.run([sys.executable, str(PLUGIN_INSTALLER), "--uninstall"], cwd=str(REPO_ROOT)).returncode
    os.execv(str(REAL_CODEX), [str(REAL_CODEX), *args])


if __name__ == "__main__":
    raise SystemExit(main())
"""


def install_shim(target: Path, real_codex: Path, force: bool) -> int:
    if not real_codex.exists():
        print(f"Real codex binary not found: {real_codex}", file=sys.stderr)
        return 1
    if (target.exists() or target.is_symlink()) and not force:
        print(f"Target already exists: {target}. Re-run with --force to replace it.", file=sys.stderr)
        return 1
    target.parent.mkdir(parents=True, exist_ok=True)
    remove_target(target)
    target.write_text(shim_script(real_codex), encoding="utf-8")
    target.chmod(target.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    print(f"Installed codex shim at {target}")
    print("Supported shortcuts:")
    print("  codex install agentcodex")
    print("  codex uninstall agentcodex")
    return 0


def uninstall_shim(target: Path) -> int:
    if target.exists() or target.is_symlink():
        remove_target(target)
        print(f"Removed codex shim from {target}")
        return 0
    print(f"No codex shim found at {target}")
    return 0


def main() -> int:
    resolved = resolve_args(sys.argv[1:])
    if resolved is None:
        print(usage(), file=sys.stderr)
        return 1
    action, force, real_codex, target = resolved
    if action == "uninstall":
        return uninstall_shim(target)
    return install_shim(target, real_codex, force)


if __name__ == "__main__":
    raise SystemExit(main())
