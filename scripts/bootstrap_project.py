#!/usr/bin/env python3
from __future__ import annotations

import shutil
import sys
from pathlib import Path

from kb_domains import KB_DOMAIN_PATHS, KB_MANAGED_DOMAINS


ROOT = Path(__file__).resolve().parent.parent
BOOTSTRAP_TEMPLATE = ROOT / ".agentcodex" / "bootstrap" / "PROJECT_AGENTSCODEX_TEMPLATE.md"
PROJECT_AGENTS_TEMPLATE = ROOT / ".agentcodex" / "bootstrap" / "PROJECT_AGENTS_TEMPLATE.md"
EXAMPLE_DEFINE_TEMPLATE = ROOT / ".agentcodex" / "bootstrap" / "EXAMPLE_DEFINE_TEMPLATE.md"
ROUTING_SOURCE = ROOT / ".agentcodex" / "routing" / "routing.json"
KB_SOURCE = ROOT / ".agentcodex" / "kb"
TEMPLATES_SOURCE = ROOT / ".agentcodex" / "templates"
COMMANDS_SOURCE = ROOT / "docs" / "commands"
CODEX_SOURCE = ROOT / ".agentcodex" / "bootstrap" / "codex"
PROJECT_STANDARD_SOURCE = ROOT / ".agentcodex" / "bootstrap" / "PROJECT_STANDARD_FEATURE"
PROJECT_STANDARD_MANIFEST = ROOT / ".agentcodex" / "project-standard.json"
MATURITY_SOURCE = ROOT / ".agentcodex" / "maturity"
MATURITY_PROFILE_OVERLAYS = ROOT / ".agentcodex" / "bootstrap" / "MATURITY_PROFILE_OVERLAYS"


def resolve_profile(args: list[str]) -> tuple[Path, bool, str | None, str] | None:
    with_codex = False
    profile: str | None = None
    install_mode = "light"
    positional: list[str] = []
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--with-codex":
            with_codex = True
            i += 1
            continue
        if arg == "--full":
            install_mode = "full"
            i += 1
            continue
        if arg == "--light":
            install_mode = "light"
            i += 1
            continue
        if arg == "--mode":
            if i + 1 >= len(args):
                return None
            install_mode = args[i + 1]
            i += 2
            continue
        if arg == "--profile":
            if i + 1 >= len(args):
                return None
            profile = args[i + 1]
            i += 2
            continue
        positional.append(arg)
        i += 1
    if len(positional) != 1 or install_mode not in {"light", "full"}:
        return None
    if profile:
        install_mode = "full"
    return Path(positional[0]).resolve(), with_codex, profile, install_mode


def copy_profile_overlay(target: Path, profile: str) -> None:
    overlay_root = MATURITY_PROFILE_OVERLAYS / profile
    if not overlay_root.exists():
        raise ValueError(profile)
    active_profile_dir = target / ".agentcodex" / "maturity"
    active_profile_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(overlay_root / "PROFILE.md", active_profile_dir / "ACTIVE_PROFILE.md")
    ops_target = target / ".agentcodex" / "ops"
    if ops_target.exists():
        for path in sorted((overlay_root / "ops").rglob("*")):
            if path.is_dir():
                continue
            rel = path.relative_to(overlay_root)
            dest = target / ".agentcodex" / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, dest)
    else:
        shutil.copytree(overlay_root / "ops", ops_target)


def main() -> int:
    if not sys.argv[1:] or sys.argv[1] in {"help", "--help", "-h"}:
        print(
            "Usage: python3 scripts/bootstrap_project.py <target-project-dir> "
            "[--mode light|full] [--full] [--with-codex] [--profile <profile-id>]"
        )
        return 0

    resolved = resolve_profile(sys.argv[1:])
    if resolved is None:
        print(
            "Usage: python3 scripts/bootstrap_project.py <target-project-dir> "
            "[--mode light|full] [--full] [--with-codex] [--profile <profile-id>]"
        )
        return 1

    target, with_codex, profile, install_mode = resolved
    target.mkdir(parents=True, exist_ok=True)

    for relative in [
        ".agentcodex/features",
        ".agentcodex/reports",
        ".agentcodex/archive",
        ".agentcodex/history",
    ]:
        (target / relative).mkdir(parents=True, exist_ok=True)

    dest = target / ".agentcodex" / "PROJECT_AGENTSCODEX.md"
    shutil.copyfile(BOOTSTRAP_TEMPLATE, dest)
    agents_dest = target / "AGENTS.md"
    if not agents_dest.exists():
        shutil.copyfile(PROJECT_AGENTS_TEMPLATE, agents_dest)

    if install_mode == "light":
        print(f"Bootstrapped lightweight AgentCodex project state at {target}")
        print(f"Created: {dest}")
        print(f"Created: {agents_dest}")
        print(f"Created: {target / '.agentcodex' / 'features'}")
        print(f"Created: {target / '.agentcodex' / 'reports'}")
        print(f"Created: {target / '.agentcodex' / 'archive'}")
        print(f"Created: {target / '.agentcodex' / 'history'}")
        print("Runtime assets remain in the AgentCodex plugin/package. Use --mode full to vendor them into the project.")
        return 0

    for relative in [
        ".agentcodex/templates",
        ".agentcodex/commands",
        ".agentcodex/kb",
        ".agentcodex/routing",
        ".agentcodex/maturity",
        ".agentcodex/ops",
    ]:
        (target / relative).mkdir(parents=True, exist_ok=True)

    example_define_dest = target / ".agentcodex" / "features" / "DEFINE_EXAMPLE_PROJECT_FEATURE.md"
    shutil.copyfile(EXAMPLE_DEFINE_TEMPLATE, example_define_dest)
    project_standard_dest = target / ".agentcodex" / "features" / "example-project-standard"
    if project_standard_dest.exists():
        shutil.rmtree(project_standard_dest)
    shutil.copytree(PROJECT_STANDARD_SOURCE, project_standard_dest)
    shutil.copyfile(PROJECT_STANDARD_MANIFEST, target / ".agentcodex" / "project-standard.json")
    for maturity_file in MATURITY_SOURCE.glob("*.json"):
        shutil.copyfile(maturity_file, target / ".agentcodex" / "maturity" / maturity_file.name)
    if profile:
        try:
            copy_profile_overlay(target, profile)
        except ValueError:
            print(f"Unknown maturity profile: {profile}")
            available = ", ".join(sorted(path.name for path in MATURITY_PROFILE_OVERLAYS.iterdir() if path.is_dir()))
            print(f"Available profiles: {available}")
            return 1

    for template in TEMPLATES_SOURCE.glob("*.md"):
        shutil.copyfile(template, target / ".agentcodex" / "templates" / template.name)
    for command_doc in COMMANDS_SOURCE.glob("*.md"):
        shutil.copyfile(command_doc, target / ".agentcodex" / "commands" / command_doc.name)

    shutil.copyfile(ROUTING_SOURCE, target / ".agentcodex" / "routing" / "routing.json")

    shutil.copyfile(KB_SOURCE / "README.md", target / ".agentcodex" / "kb" / "README.md")
    shutil.copyfile(KB_SOURCE / "index.yaml", target / ".agentcodex" / "kb" / "index.yaml")
    for kb_target in KB_MANAGED_DOMAINS:
        source_dir = KB_SOURCE / KB_DOMAIN_PATHS[kb_target]
        dest_dir = target / ".agentcodex" / "kb" / KB_DOMAIN_PATHS[kb_target]
        if dest_dir.exists():
            shutil.rmtree(dest_dir)
        shutil.copytree(source_dir, dest_dir)

    if with_codex:
        codex_dir = target / ".codex"
        agents_dir = codex_dir / "agents"
        agents_dir.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(CODEX_SOURCE / "config.toml", codex_dir / "config.toml")
        for agent_file in (CODEX_SOURCE / "agents").glob("*.toml"):
            shutil.copyfile(agent_file, agents_dir / agent_file.name)

    print(f"Bootstrapped AgentCodex project scaffold at {target}")
    print(f"Created: {dest}")
    print(f"Created: {agents_dest}")
    print(f"Created: {example_define_dest}")
    print(f"Created: {project_standard_dest}")
    print(f"Created: {target / '.agentcodex' / 'project-standard.json'}")
    print(f"Created: {target / '.agentcodex' / 'maturity'}")
    if profile:
        print(f"Created: {target / '.agentcodex' / 'ops'}")
        print(f"Activated maturity profile: {profile}")
    print(f"Created: {target / '.agentcodex' / 'commands'}")
    if with_codex:
        print(f"Created: {target / '.codex' / 'config.toml'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
