#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
IMPORTS_ROOT = ROOT / ".agentcodex" / "imports"
MANIFEST_PATH = IMPORTS_ROOT / "manifest.json"
CATALOG_PATH = IMPORTS_ROOT / "catalog.json"
DOC_PATH = ROOT / "docs" / "UPSTREAM-CATALOG.md"


def relpath_list(base: Path, pattern: str) -> list[str]:
    if not base.exists():
        return []
    return sorted(str(path.relative_to(base)) for path in base.glob(pattern))


def child_dirs(base: Path) -> list[str]:
    if not base.exists():
        return []
    return sorted(path.name for path in base.iterdir() if path.is_dir())


def collect_source_catalog(source_root: Path, source_name: str) -> dict:
    if source_name == "agentspec":
        agents = relpath_list(source_root / "agents", "*/*.md")
        skills = relpath_list(source_root / "skills", "*/SKILL.md")
        kb_domains = child_dirs(source_root / "kb")
        commands = sorted(
            str(path.relative_to(source_root / "commands"))
            for path in (source_root / "commands").rglob("*.md")
        )
        workflows = sorted(
            str(path.relative_to(source_root / "sdd"))
            for path in (source_root / "sdd").rglob("*.md")
        )
        claude_agents = relpath_list(source_root / "claude" / "agents", "*/*.md")
        claude_commands = relpath_list(source_root / "claude" / "commands", "*/*.md")
        extra_skills = relpath_list(source_root / "plugin_extras_skills", "*/SKILL.md")
        return {
            "agents": agents,
            "commands": commands,
            "skills": skills,
            "kb_domains": kb_domains,
            "workflows": workflows,
            "claude_agents": claude_agents,
            "claude_commands": claude_commands,
            "extra_skills": extra_skills,
        }

    if source_name == "data-agents":
        agents = relpath_list(source_root / "agents" / "registry", "*.md")
        commands = relpath_list(source_root / "commands", "*.py")
        skills = relpath_list(source_root / "skills", "**/SKILL.md")
        kb_domains = child_dirs(source_root / "kb")
        mcp_servers = child_dirs(source_root / "mcp_servers")
        hooks = relpath_list(source_root / "hooks", "*.py")
        tests = relpath_list(source_root / "tests", "test_*.py")
        scripts = relpath_list(source_root / "scripts", "*.py")
        templates = relpath_list(source_root / "templates", "*.md")
        return {
            "agents": agents,
            "commands": commands,
            "skills": skills,
            "kb_domains": kb_domains,
            "mcp_servers": mcp_servers,
            "hooks": hooks,
            "tests": tests,
            "scripts": scripts,
            "templates": templates,
        }

    agents = relpath_list(source_root / "agents", "*.md")
    skills = relpath_list(source_root / "skills", "*/SKILL.md")
    rulesets = child_dirs(source_root / "rules")
    commands = relpath_list(source_root / "commands", "*.md")
    codex_agents = relpath_list(source_root / "codex" / "agents", "*.toml")
    docs = relpath_list(source_root / "docs", "**/*.md")
    schemas = relpath_list(source_root / "schemas", "*.json")
    scripts_ci = relpath_list(source_root / "scripts_ci", "*.js")
    kb_domains = child_dirs(source_root / "kb")
    mcp_servers = child_dirs(source_root / "mcp_servers")
    hooks = relpath_list(source_root / "hooks", "*.py")
    tests = relpath_list(source_root / "tests", "test_*.py")
    return {
        "agents": agents,
        "commands": commands,
        "skills": skills,
        "rulesets": rulesets,
        "kb_domains": kb_domains,
        "mcp_servers": mcp_servers,
        "hooks": hooks,
        "tests": tests,
        "codex_agents": codex_agents,
        "docs": docs,
        "schemas": schemas,
        "scripts_ci": scripts_ci,
    }


def top(items: list[str], limit: int = 12) -> list[str]:
    return items[:limit]


def main() -> int:
    if not MANIFEST_PATH.exists():
        raise SystemExit(f"Missing import manifest: {MANIFEST_PATH}")

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    catalog = {"version": manifest.get("version", "0.1.0"), "sources": {}}

    for item in manifest.get("imports", []):
        source_name = item["source"]
        source_root = IMPORTS_ROOT / source_name
        catalog["sources"][source_name] = collect_source_catalog(source_root, source_name)

    CATALOG_PATH.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")

    agentspec = catalog["sources"].get("agentspec", {})
    ecc = catalog["sources"].get("ecc", {})
    data_agents = catalog["sources"].get("data-agents", {})

    lines = [
        "# Upstream Catalog",
        "",
        "This file is generated from `.agentcodex/imports/manifest.json` and the imported source trees.",
        "",
        "Do not treat it as the primary runtime contract.",
        "Use it as a quick index into the raw upstream material copied into AgentCodex.",
        "",
        "## AgentSpec Snapshot",
        "",
        f"- agents: {len(agentspec.get('agents', []))}",
        f"- commands: {len(agentspec.get('commands', []))}",
        f"- skills: {len(agentspec.get('skills', []))}",
        f"- kb domains: {len(agentspec.get('kb_domains', []))}",
        f"- workflow docs: {len(agentspec.get('workflows', []))}",
        f"- Claude agents mirrored: {len(agentspec.get('claude_agents', []))}",
        f"- Claude commands mirrored: {len(agentspec.get('claude_commands', []))}",
        f"- plugin-extras skills mirrored: {len(agentspec.get('extra_skills', []))}",
        "",
        "Top AgentSpec agents:",
    ]
    lines.extend(f"- `{item}`" for item in top(agentspec.get("agents", [])))
    lines.extend([
        "",
        "AgentSpec KB domains:",
    ])
    lines.extend(f"- `{item}`" for item in top(agentspec.get("kb_domains", []), limit=25))
    lines.extend([
        "",
        "Top AgentSpec skills:",
    ])
    lines.extend(f"- `{item}`" for item in top(agentspec.get("skills", [])))
    lines.extend([
        "",
        "Top mirrored AgentSpec Claude commands:",
    ])
    lines.extend(f"- `{item}`" for item in top(agentspec.get("claude_commands", [])))
    lines.extend([
        "",
        "## ECC Snapshot",
        "",
        f"- agents: {len(ecc.get('agents', []))}",
        f"- commands: {len(ecc.get('commands', []))}",
        f"- skills: {len(ecc.get('skills', []))}",
        f"- rulesets: {len(ecc.get('rulesets', []))}",
        f"- codex agents: {len(ecc.get('codex_agents', []))}",
        f"- docs mirrored: {len(ecc.get('docs', []))}",
        f"- CI validators mirrored: {len(ecc.get('scripts_ci', []))}",
        f"- schemas mirrored: {len(ecc.get('schemas', []))}",
        "",
        "Top ECC agents:",
    ])
    lines.extend(f"- `{item}`" for item in top(ecc.get("agents", [])))
    lines.extend([
        "",
        "Top ECC skills:",
    ])
    lines.extend(f"- `{item}`" for item in top(ecc.get("skills", [])))
    lines.extend([
        "",
        "ECC rulesets:",
    ])
    lines.extend(f"- `{item}`" for item in ecc.get("rulesets", []))
    lines.extend([
        "",
        "ECC Codex agents:",
    ])
    lines.extend(f"- `{item}`" for item in ecc.get("codex_agents", []))
    lines.extend([
        "",
        "Top mirrored ECC docs:",
    ])
    lines.extend(f"- `{item}`" for item in top(ecc.get("docs", [])))
    if data_agents:
        lines.extend([
            "",
            "## Data Agents Snapshot",
            "",
            f"- agents: {len(data_agents.get('agents', []))}",
            f"- commands: {len(data_agents.get('commands', []))}",
            f"- skills: {len(data_agents.get('skills', []))}",
            f"- kb domains: {len(data_agents.get('kb_domains', []))}",
            f"- MCP servers: {len(data_agents.get('mcp_servers', []))}",
            f"- hooks: {len(data_agents.get('hooks', []))}",
            f"- tests mirrored: {len(data_agents.get('tests', []))}",
            "",
            "Data Agents KB domains:",
        ])
        lines.extend(f"- `{item}`" for item in top(data_agents.get("kb_domains", []), limit=25))
        lines.extend([
            "",
            "Data Agents MCP servers:",
        ])
        lines.extend(f"- `{item}`" for item in data_agents.get("mcp_servers", []))
        lines.extend([
            "",
            "Top Data Agents skills:",
        ])
        lines.extend(f"- `{item}`" for item in top(data_agents.get("skills", [])))
        lines.extend([
            "",
            "Top Data Agents hooks:",
        ])
        lines.extend(f"- `{item}`" for item in top(data_agents.get("hooks", [])))

    DOC_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote import catalog: {CATALOG_PATH}")
    print(f"Wrote import doc: {DOC_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
