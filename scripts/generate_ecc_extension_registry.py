#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ECC_ROOT = ROOT / ".agentcodex" / "imports" / "ecc"
REGISTRY_PATH = ROOT / ".agentcodex" / "ecc-extension.json"
DOC_PATH = ROOT / "docs" / "ECC-EXTENSION.md"


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def collect_markdown(root: Path, *, exclude_readme: bool = False) -> list[str]:
    if not root.exists():
        return []
    paths = []
    for path in sorted(root.rglob("*.md")):
        if exclude_readme and path.name == "README.md":
            continue
        paths.append(rel(path))
    return paths


def collect_direct_markdown(root: Path) -> list[str]:
    if not root.exists():
        return []
    return [rel(path) for path in sorted(root.glob("*.md")) if path.is_file()]


def collect_skills(root: Path) -> list[dict[str, str]]:
    if not root.exists():
        return []
    skills = []
    for skill_path in sorted(root.glob("*/SKILL.md")):
        skills.append({"id": skill_path.parent.name, "path": rel(skill_path)})
    return skills


def collect_rules(root: Path) -> list[dict[str, str]]:
    if not root.exists():
        return []
    rules = []
    for rule_path in sorted(root.rglob("*.md")):
        if rule_path.name == "README.md":
            continue
        rules.append(
            {
                "ruleset": rule_path.parent.name,
                "name": rule_path.name,
                "path": rel(rule_path),
            }
        )
    return rules


def collect_codex_runtime() -> list[str]:
    codex_root = ECC_ROOT / "codex"
    if not codex_root.exists():
        return []
    return [rel(path) for path in sorted(codex_root.rglob("*")) if path.is_file()]


def load_modules() -> list[dict]:
    path = ECC_ROOT / "manifests" / "install-modules.json"
    if not path.exists():
        return []
    modules = read_json(path).get("modules", [])
    return sorted(modules, key=lambda item: item["id"])


def load_components() -> list[dict]:
    path = ECC_ROOT / "manifests" / "install-components.json"
    if not path.exists():
        return []
    components = read_json(path).get("components", [])
    return sorted(components, key=lambda item: item["id"])


def load_profiles() -> dict:
    path = ECC_ROOT / "manifests" / "install-profiles.json"
    if not path.exists():
        return {}
    return read_json(path).get("profiles", {})


def build_registry() -> dict:
    active_commands = {path.name for path in (ROOT / "docs" / "commands").glob("*.md")}
    active_roles = {path.name for path in (ROOT / "docs" / "roles").glob("*.md")}
    active_codex_agents = {path.name for path in (ROOT / ".codex" / "agents").glob("*.toml")}

    commands = []
    for command_path in sorted((ECC_ROOT / "commands").glob("*.md")):
        commands.append(
            {
                "id": command_path.stem,
                "source_path": rel(command_path),
                "active_agentcodex_command": command_path.name in active_commands,
                "activation": "reference-only" if command_path.name not in active_commands else "already-active",
            }
        )

    agents = []
    for agent_path in sorted((ECC_ROOT / "agents").glob("*.md")):
        agents.append(
            {
                "id": agent_path.stem,
                "source_path": rel(agent_path),
                "active_agentcodex_role": agent_path.name in active_roles,
                "activation": "already-active" if agent_path.name in active_roles else "extension-role",
            }
        )

    modules = load_modules()
    codex_modules = [
        module
        for module in modules
        if "codex" in module.get("targets", []) or "opencode" in module.get("targets", [])
    ]

    registry = {
        "version": "0.1.0",
        "source": {
            "name": "Everything-Claude-Code",
            "root": ".agentcodex/imports/ecc",
            "policy": "Reference the imported ECC source from AgentCodex extension manifests; do not duplicate files into active command or role directories unless explicitly ported.",
        },
        "counts": {
            "commands": len(commands),
            "agents": len(agents),
            "skills": len(collect_skills(ECC_ROOT / "skills")),
            "rules": len(collect_rules(ECC_ROOT / "rules")),
            "docs": len(collect_markdown(ECC_ROOT / "docs")),
            "docs_pt_br": len(collect_markdown(ECC_ROOT / "docs_pt_br")),
            "schemas": len(list((ECC_ROOT / "schemas").glob("*.json"))),
            "ci_validators": len(list((ECC_ROOT / "scripts_ci").glob("*"))),
            "components": len(load_components()),
            "modules": len(modules),
            "profiles": len(load_profiles()),
            "codex_runtime_files": len(collect_codex_runtime()),
            "active_command_name_matches": sum(1 for item in commands if item["active_agentcodex_command"]),
            "active_role_name_matches": sum(1 for item in agents if item["active_agentcodex_role"]),
            "active_codex_agents": len(active_codex_agents),
        },
        "codex_runtime_reference": collect_codex_runtime(),
        "profiles": load_profiles(),
        "components": load_components(),
        "modules": modules,
        "codex_or_opencode_modules": codex_modules,
        "commands": commands,
        "agents": agents,
        "skills": collect_skills(ECC_ROOT / "skills"),
        "rules": collect_rules(ECC_ROOT / "rules"),
        "schemas": [rel(path) for path in sorted((ECC_ROOT / "schemas").glob("*.json"))],
        "ci_validators": [rel(path) for path in sorted((ECC_ROOT / "scripts_ci").glob("*")) if path.is_file()],
        "docs": {
            "english": collect_markdown(ECC_ROOT / "docs"),
            "portuguese_brazil": collect_markdown(ECC_ROOT / "docs_pt_br"),
        },
        "activation_policy": {
            "default": "reference-only",
            "no_duplicate_rule": "Do not duplicate active surfaces: if AgentCodex already has an active command or role with the same filename, keep the ECC source as upstream reference and do not copy it into docs/commands or docs/roles.",
            "porting_rule": "Port only through an explicit AgentCodex procedure, role, profile, or validator change with tests.",
            "runtime_rule": "Keep Claude/OpenCode hook or slash-command assumptions in the imported layer unless they are normalized to Codex file-based behavior.",
        },
    }
    return registry


def write_doc(registry: dict) -> None:
    counts = registry["counts"]
    lines = [
        "# ECC Extension Registry",
        "",
        "This document exposes the complete imported Everything-Claude-Code surface as an AgentCodex extension layer.",
        "",
        "The registry does not duplicate ECC files into active AgentCodex command or role directories. It references the raw import under `.agentcodex/imports/ecc/` and records what is already active, what is extension-only, and what can be ported later.",
        "",
        "## Counts",
        "",
        f"- commands: {counts['commands']}",
        f"- agents: {counts['agents']}",
        f"- skills: {counts['skills']}",
        f"- rules: {counts['rules']}",
        f"- docs: {counts['docs']}",
        f"- docs pt-BR: {counts['docs_pt_br']}",
        f"- schemas: {counts['schemas']}",
        f"- CI validators: {counts['ci_validators']}",
        f"- install components: {counts['components']}",
        f"- install modules: {counts['modules']}",
        f"- install profiles: {counts['profiles']}",
        f"- Codex runtime reference files: {counts['codex_runtime_files']}",
        f"- active command name matches: {counts['active_command_name_matches']}",
        f"- active role name matches: {counts['active_role_name_matches']}",
        "",
        "## Codex And OpenCode Coverage",
        "",
        "ECC modules that explicitly target Codex or OpenCode:",
        "",
    ]
    for module in registry["codex_or_opencode_modules"]:
        targets = ", ".join(module.get("targets", []))
        lines.append(f"- `{module['id']}` ({module['kind']}): {targets}")

    lines.extend(
        [
            "",
            "## Activation Policy",
            "",
            f"- default: `{registry['activation_policy']['default']}`",
            f"- no duplicate rule: {registry['activation_policy']['no_duplicate_rule']}",
            f"- porting rule: {registry['activation_policy']['porting_rule']}",
            f"- runtime rule: {registry['activation_policy']['runtime_rule']}",
            "",
            "## Registry",
            "",
            "Machine-readable registry:",
            "",
            "- `.agentcodex/ecc-extension.json`",
            "",
            "Use that file when selecting ECC material to port into AgentCodex profiles, commands, roles, validators, or runtime docs.",
            "",
        ]
    )
    DOC_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    registry = build_registry()
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    write_doc(registry)
    print(f"Wrote ECC extension registry: {REGISTRY_PATH}")
    print(f"Wrote ECC extension doc: {DOC_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
