#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PLUGIN_NAME = "agentcodex"
PLUGIN_SOURCE = ROOT / "plugins" / PLUGIN_NAME
BUILD_SCRIPT = ROOT / "scripts" / "build_plugin_runtime.py"


def usage() -> str:
    return (
        "Usage: python3 scripts/install_codex_plugin.py "
        "[--mode symlink|copy] [--home <home-dir>] [--plugins-dir <plugins-dir>] "
        "[--marketplace-path <marketplace.json>] [--force]\n"
        "   or: python3 scripts/install_codex_plugin.py --uninstall "
        "[--home <home-dir>] [--plugins-dir <plugins-dir>] [--marketplace-path <marketplace.json>] [--force]\n"
        "\n"
        "Installs or removes AgentCodex as a home-local Codex plugin.\n"
    )


def resolve_args(args: list[str]) -> tuple[str, str, Path, Path | None, Path | None, bool] | None:
    action = "install"
    mode = "symlink"
    home = Path.home()
    plugins_dir: Path | None = None
    marketplace_path: Path | None = None
    force = False
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--uninstall":
            action = "uninstall"
            i += 1
            continue
        if arg == "--mode":
            if i + 1 >= len(args) or args[i + 1] not in {"symlink", "copy"}:
                return None
            mode = args[i + 1]
            i += 2
            continue
        if arg == "--home":
            if i + 1 >= len(args):
                return None
            home = Path(args[i + 1]).expanduser().resolve()
            i += 2
            continue
        if arg == "--plugins-dir":
            if i + 1 >= len(args):
                return None
            plugins_dir = Path(args[i + 1]).expanduser().resolve()
            i += 2
            continue
        if arg == "--marketplace-path":
            if i + 1 >= len(args):
                return None
            marketplace_path = Path(args[i + 1]).expanduser().resolve()
            i += 2
            continue
        if arg == "--force":
            force = True
            i += 1
            continue
        return None
    return action, mode, home, plugins_dir, marketplace_path, force


def build_runtime_bundle() -> None:
    subprocess.run([sys.executable, str(BUILD_SCRIPT)], cwd=str(ROOT), check=True)


def ensure_clean_target(path: Path, force: bool) -> None:
    if not path.exists() and not path.is_symlink():
        return
    if not force:
        raise RuntimeError(f"Target already exists: {path}. Re-run with --force to replace it.")
    if path.is_symlink() or path.is_file():
        path.unlink()
        return
    shutil.rmtree(path)


def install_plugin_tree(mode: str, source: Path, target: Path, force: bool) -> None:
    ensure_clean_target(target, force)
    target.parent.mkdir(parents=True, exist_ok=True)
    if mode == "symlink":
        target.symlink_to(source, target_is_directory=True)
        return
    shutil.copytree(source, target)


def load_marketplace(path: Path) -> dict:
    if not path.exists():
        return {
            "name": "codex-local-plugins",
            "interface": {"displayName": "Codex Local Plugins"},
            "plugins": [],
        }
    return json.loads(path.read_text(encoding="utf-8"))


def upsert_marketplace_plugin(data: dict, plugin_path: str) -> None:
    plugins = data.setdefault("plugins", [])
    for plugin in plugins:
        if plugin.get("name") != PLUGIN_NAME:
            continue
        plugin["source"] = {"source": "local", "path": plugin_path}
        plugin["policy"] = {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}
        plugin["category"] = "Productivity"
        return
    plugins.append(
        {
            "name": PLUGIN_NAME,
            "source": {"source": "local", "path": plugin_path},
            "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
            "category": "Productivity",
        }
    )


def write_marketplace(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def remove_marketplace_plugin(data: dict) -> bool:
    plugins = data.get("plugins", [])
    kept = [plugin for plugin in plugins if plugin.get("name") != PLUGIN_NAME]
    changed = len(kept) != len(plugins)
    data["plugins"] = kept
    return changed


def main() -> int:
    resolved = resolve_args(sys.argv[1:])
    if resolved is None:
        print(usage(), file=sys.stderr)
        return 1

    action, mode, home, plugins_dir_override, marketplace_override, force = resolved
    plugins_dir = plugins_dir_override or (home / "plugins")
    marketplace_path = marketplace_override or (home / ".agents" / "plugins" / "marketplace.json")
    plugin_target = plugins_dir / PLUGIN_NAME

    if action == "uninstall":
        if plugin_target.exists() or plugin_target.is_symlink():
            ensure_clean_target(plugin_target, True if force else True)
        marketplace = load_marketplace(marketplace_path)
        changed = remove_marketplace_plugin(marketplace)
        if changed or marketplace_path.exists():
            write_marketplace(marketplace_path, marketplace)
        print(f"Removed Codex plugin '{PLUGIN_NAME}' from {plugin_target}")
        print(f"Updated marketplace: {marketplace_path}")
        return 0

    if not PLUGIN_SOURCE.exists():
        print(f"Missing plugin source: {PLUGIN_SOURCE}", file=sys.stderr)
        return 1

    build_runtime_bundle()
    install_plugin_tree(mode, PLUGIN_SOURCE, plugin_target, force)

    marketplace = load_marketplace(marketplace_path)
    relative_plugin_path = f"./plugins/{PLUGIN_NAME}"
    upsert_marketplace_plugin(marketplace, relative_plugin_path)
    write_marketplace(marketplace_path, marketplace)

    print(f"Installed Codex plugin '{PLUGIN_NAME}' at {plugin_target}")
    print(f"Updated marketplace: {marketplace_path}")
    print("Next step in Codex:")
    print("1. Open the Plugins library.")
    print("2. Install or enable AgentCodex.")
    print("3. Open your repository.")
    print("4. Ask Codex: Install AgentCodex in this repository.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
