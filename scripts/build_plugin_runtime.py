#!/usr/bin/env python3
from __future__ import annotations

import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PLUGIN_RUNTIME = ROOT / "plugins" / "agentcodex" / "runtime" / "agentcodex-runtime"


def copy_tree(src: Path, dest: Path) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest)


def main() -> int:
    if PLUGIN_RUNTIME.exists():
        shutil.rmtree(PLUGIN_RUNTIME)

    (PLUGIN_RUNTIME / ".agentcodex").mkdir(parents=True, exist_ok=True)
    (PLUGIN_RUNTIME / "docs").mkdir(parents=True, exist_ok=True)

    copy_tree(ROOT / ".agentcodex" / "bootstrap", PLUGIN_RUNTIME / ".agentcodex" / "bootstrap")
    copy_tree(ROOT / ".agentcodex" / "templates", PLUGIN_RUNTIME / ".agentcodex" / "templates")
    copy_tree(ROOT / ".agentcodex" / "kb", PLUGIN_RUNTIME / ".agentcodex" / "kb")
    copy_tree(ROOT / ".agentcodex" / "maturity", PLUGIN_RUNTIME / ".agentcodex" / "maturity")
    copy_tree(ROOT / "docs" / "commands", PLUGIN_RUNTIME / "docs" / "commands")

    shutil.copyfile(ROOT / ".agentcodex" / "project-standard.json", PLUGIN_RUNTIME / ".agentcodex" / "project-standard.json")
    routing_dest = PLUGIN_RUNTIME / ".agentcodex" / "routing"
    routing_dest.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / ".agentcodex" / "routing" / "routing.json", routing_dest / "routing.json")

    print(f"Built AgentCodex runtime bundle at {PLUGIN_RUNTIME}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
