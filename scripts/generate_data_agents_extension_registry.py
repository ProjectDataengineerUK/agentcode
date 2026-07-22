#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DATA_AGENTS_ROOT = ROOT / ".agentcodex" / "imports" / "data-agents"
REGISTRY_PATH = ROOT / ".agentcodex" / "data-agents-extension.json"
DOC_PATH = ROOT / "docs" / "DATA-AGENTS-EXTENSION.md"

ROLE_ALIASES = {
    "business-analyst": "planner",
    "business-monitor": "business-monitor",
    "data-quality-steward": "data-quality-analyst",
    "dbt-expert": "dbt-specialist",
    "geral": "codebase-explorer",
    "governance-auditor": "data-governance-architect",
    "migration-expert": "lakehouse-architect",
    "pipeline-architect": "pipeline-architect",
    "python-expert": "python-developer",
    "semantic-modeler": "semantic-modeler",
    "spark-expert": "spark-specialist",
    "sql-expert": "sql-optimizer",
}

COMMAND_ALIASES = {
    "geral": "status",
    "monitor": "platform-health",
    "sessions": "session-controls",
    "workflow": "orchestrate-workflow",
}


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_frontmatter(path: Path) -> dict[str, object]:
    text = read_text(path)
    if not text.startswith("---"):
        return {"name": path.stem, "description": ""}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {"name": path.stem, "description": ""}
    frontmatter = parts[1]
    result: dict[str, object] = {"name": path.stem, "description": ""}
    for line in frontmatter.splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().strip('"')
        if value.startswith("[") and value.endswith("]"):
            items = [item.strip().strip('"').strip("'") for item in value[1:-1].split(",") if item.strip()]
            result[key] = items
        else:
            result[key] = value
    return result


def collect_files(root: Path, pattern: str) -> list[str]:
    if not root.exists():
        return []
    return [rel(path) for path in sorted(root.glob(pattern)) if path.is_file()]


def collect_recursive_files(root: Path, pattern: str) -> list[str]:
    if not root.exists():
        return []
    return [rel(path) for path in sorted(root.rglob(pattern)) if path.is_file()]


def collect_mcp_servers(root: Path) -> list[str]:
    if not root.exists():
        return []
    return sorted(
        path.name
        for path in root.iterdir()
        if path.is_dir() and path.name != "_template"
    )


def active_role_ids() -> set[str]:
    return {path.stem for path in (ROOT / "docs" / "roles").glob("*.md")}


def active_command_ids() -> set[str]:
    return {path.stem for path in (ROOT / "docs" / "commands").glob("*.md")}


def build_agents(active_roles: set[str]) -> list[dict[str, object]]:
    agents = []
    registry_root = DATA_AGENTS_ROOT / "agents" / "registry"
    for path in sorted(registry_root.glob("*.md")):
        if path.stem == "_template":
            continue
        meta = parse_frontmatter(path)
        source_id = str(meta.get("name") or path.stem)
        target_role = ROLE_ALIASES.get(source_id)
        activation = "extension-role"
        if target_role and target_role in active_roles:
            activation = "mapped-to-native-role"
        elif path.stem in active_roles:
            target_role = path.stem
            activation = "already-active"
        elif target_role:
            activation = "missing-target-role"
        else:
            activation = "reference-only"
        agents.append(
            {
                "id": source_id,
                "source_path": rel(path),
                "description": meta.get("description", ""),
                "kb_domains": meta.get("kb_domains", []),
                "mcp_servers": meta.get("mcp_servers", []),
                "target_agentcodex_role": target_role,
                "activation": activation,
            }
        )
    return agents


def build_commands(active_commands: set[str]) -> list[dict[str, object]]:
    commands = []
    for path in sorted((DATA_AGENTS_ROOT / "commands").glob("*.py")):
        if path.name == "__init__.py":
            continue
        command_id = path.stem
        target_command = COMMAND_ALIASES.get(command_id)
        activation = "reference-only"
        if command_id in active_commands:
            target_command = command_id
            activation = "already-active"
        elif target_command in active_commands:
            activation = "mapped-to-native-command"
        commands.append(
            {
                "id": command_id,
                "source_path": rel(path),
                "target_agentcodex_command": target_command,
                "activation": activation,
            }
        )
    return commands


def build_registry() -> dict[str, object]:
    active_roles = active_role_ids()
    active_commands = active_command_ids()
    agents = build_agents(active_roles)
    commands = build_commands(active_commands)
    skills = [
        {
            "id": str(path.relative_to(DATA_AGENTS_ROOT / "skills").parent),
            "source_path": rel(path),
            "activation": "reference-only",
        }
        for path in sorted((DATA_AGENTS_ROOT / "skills").rglob("SKILL.md"))
    ]
    kb_files = collect_recursive_files(DATA_AGENTS_ROOT / "kb", "*.md")
    mcp_servers = collect_mcp_servers(DATA_AGENTS_ROOT / "mcp_servers")
    hooks = collect_files(DATA_AGENTS_ROOT / "hooks", "*.py")
    tests = collect_files(DATA_AGENTS_ROOT / "tests", "test_*.py")
    templates = collect_files(DATA_AGENTS_ROOT / "templates", "*.md")

    return {
        "version": "0.1.0",
        "source": {
            "name": "data-agents",
            "root": ".agentcodex/imports/data-agents",
            "policy": "Expose Data Agents as a native AgentCodex extension registry. Do not duplicate active roles, commands, or KB pages; map to existing Codex-native surfaces when equivalent.",
        },
        "counts": {
            "agents": len(agents),
            "commands": len(commands),
            "skills": len(skills),
            "kb_files": len(kb_files),
            "mcp_servers": len(mcp_servers),
            "hooks": len(hooks),
            "tests": len(tests),
            "templates": len(templates),
            "mapped_agents": sum(1 for item in agents if item["activation"] in {"mapped-to-native-role", "already-active"}),
            "mapped_commands": sum(1 for item in commands if item["activation"] in {"mapped-to-native-command", "already-active"}),
        },
        "agents": agents,
        "commands": commands,
        "skills": skills,
        "kb_files": kb_files,
        "mcp_servers": mcp_servers,
        "hooks": hooks,
        "tests": tests,
        "templates": templates,
        "activation_policy": {
            "default": "reference-only",
            "no_duplicate_rule": "Do not create a new AgentCodex role, command, or KB page when an equivalent native surface already exists. Record the mapping instead.",
            "native_codex_rule": "Claude hooks, MCP tool names, and runtime-specific scripts remain raw source unless translated into file-based AgentCodex procedures, roles, reports, or validators.",
            "porting_rule": "Promote only missing behavior that adds distinct operational value, with validation coverage when code changes are involved.",
        },
    }


def write_doc(registry: dict[str, object]) -> None:
    counts = registry["counts"]
    lines = [
        "# Data Agents Extension Registry",
        "",
        "This document exposes the imported Data Agents surface as a native AgentCodex extension layer without duplicating active AgentCodex roles, commands, or KB pages.",
        "",
        "## Counts",
        "",
        f"- agents: {counts['agents']}",
        f"- commands: {counts['commands']}",
        f"- skills: {counts['skills']}",
        f"- KB files: {counts['kb_files']}",
        f"- MCP servers: {counts['mcp_servers']}",
        f"- hooks: {counts['hooks']}",
        f"- tests: {counts['tests']}",
        f"- templates: {counts['templates']}",
        f"- mapped agents: {counts['mapped_agents']}",
        f"- mapped commands: {counts['mapped_commands']}",
        "",
        "## Agent Mapping",
        "",
        "| Data Agents agent | AgentCodex role | Activation |",
        "|---|---|---|",
    ]
    for agent in registry["agents"]:
        target = agent.get("target_agentcodex_role") or ""
        lines.append(f"| `{agent['id']}` | `{target}` | `{agent['activation']}` |")

    lines.extend([
        "",
        "## Command Mapping",
        "",
        "| Data Agents command module | AgentCodex command | Activation |",
        "|---|---|---|",
    ])
    for command in registry["commands"]:
        target = command.get("target_agentcodex_command") or ""
        lines.append(f"| `{command['id']}` | `{target}` | `{command['activation']}` |")

    lines.extend([
        "",
        "## MCP Servers",
        "",
    ])
    lines.extend(f"- `{item}`" for item in registry["mcp_servers"])
    lines.extend([
        "",
        "## Activation Policy",
        "",
        f"- default: `{registry['activation_policy']['default']}`",
        f"- no duplicate rule: {registry['activation_policy']['no_duplicate_rule']}",
        f"- native Codex rule: {registry['activation_policy']['native_codex_rule']}",
        f"- porting rule: {registry['activation_policy']['porting_rule']}",
    ])
    DOC_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    if not DATA_AGENTS_ROOT.exists():
        raise SystemExit(f"Missing Data Agents import: {DATA_AGENTS_ROOT}")
    registry = build_registry()
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    write_doc(registry)
    print(f"Wrote Data Agents extension registry: {REGISTRY_PATH}")
    print(f"Wrote Data Agents extension doc: {DOC_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
