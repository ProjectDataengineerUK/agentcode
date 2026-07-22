#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
IMPORTS_ROOT = ROOT / ".agentcodex" / "imports"

AGENTSPEC_ROOT = Path("/home/user/Projetos/agentspec")
ECC_ROOT = Path("/home/user/Projetos/everything-claude-code")
DATA_AGENTS_ROOT = Path("/home/user/Projetos/data-agents")


AGENTSPEC_IMPORTS = {
    "agents": "plugin/agents",
    "commands": "plugin/commands",
    "skills": "plugin/skills",
    "kb": "plugin/kb",
    "sdd": "plugin/sdd",
    "claude": ".claude",
    "scripts": "scripts",
    "plugin_metadata": "plugin/.claude-plugin",
    "plugin_extras_skills": "plugin-extras/skills",
    "plugin_hooks": "plugin/hooks",
    "docs": "docs",
    "readme": "README.md",
    "claude_md": "CLAUDE.md",
}

ECC_IMPORTS = {
    "agents_md": "AGENTS.md",
    "agents": "agents",
    "commands": "commands",
    "skills": "skills",
    "rules": "rules",
    "contexts": "contexts",
    "codex": ".codex",
    "docs": "docs",
    "docs_pt_br": "docs/pt-BR",
    "scripts_ci": "scripts/ci",
    "schemas": "schemas",
    "manifests": "manifests",
    "readme": "README.md",
    "commands_quick_ref": "COMMANDS-QUICK-REF.md",
}

DATA_AGENTS_IMPORTS = {
    "agents": "agents",
    "commands": "commands",
    "compression": "compression",
    "config": "config",
    "evals": "evals",
    "hooks": "hooks",
    "kb": "kb",
    "mcp_servers": "mcp_servers",
    "memory": "memory",
    "monitoring": "monitoring",
    "scripts": "scripts",
    "skills": "skills",
    "templates": "templates",
    "tests": "tests",
    "tools": "tools",
    "ui": "ui",
    "utils": "utils",
    "wiki": "wiki",
    "workflow": "workflow",
    "github_workflows": ".github/workflows",
    "claude_commands": ".claude/commands",
    "chainlit": ".chainlit",
    "readme": "README.md",
    "product": "PRODUCT.md",
    "changelog": "CHANGELOG.md",
    "manual_report": "Manual_Relatorio_Tecnico_Projeto_Data_Agents.md",
    "license": "LICENSE",
    "pyproject": "pyproject.toml",
    "makefile": "Makefile",
    "mcp_config": ".mcp.json",
    "env_example": ".env.example",
}


def safe_remove(path: Path) -> None:
    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()


def copy_path(source_root: Path, rel_source: str, dest_root: Path, name: str) -> dict:
    source = source_root / rel_source
    destination = dest_root / name
    if not source.exists():
        return {"name": name, "status": "missing", "source": str(source)}

    safe_remove(destination)
    if source.is_dir():
        ignore = shutil.ignore_patterns(
            "__pycache__",
            "*.pyc",
            "*.pyo",
            ".pytest_cache",
            ".mypy_cache",
            ".ruff_cache",
            "*.pid",
        )
        shutil.copytree(source, destination, ignore=ignore)
        file_count = sum(1 for p in destination.rglob("*") if p.is_file())
        return {
            "name": name,
            "status": "copied",
            "type": "directory",
            "source": str(source),
            "destination": str(destination.relative_to(ROOT)),
            "files": file_count,
        }

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
    return {
        "name": name,
        "status": "copied",
        "type": "file",
        "source": str(source),
        "destination": str(destination.relative_to(ROOT)),
        "files": 1,
    }


def import_source(source_name: str, source_root: Path, mapping: dict[str, str]) -> dict:
    target_root = IMPORTS_ROOT / source_name
    target_root.mkdir(parents=True, exist_ok=True)
    results = []
    total_files = 0

    for name, rel_source in mapping.items():
        result = copy_path(source_root, rel_source, target_root, name)
        results.append(result)
        total_files += result.get("files", 0)

    return {
        "source": source_name,
        "root": str(source_root),
        "target_root": str(target_root.relative_to(ROOT)),
        "total_files": total_files,
        "imports": results,
    }


def load_existing_manifest(manifest_path: Path) -> dict[str, object]:
    if not manifest_path.exists():
        return {"version": "0.1.0", "imports": []}
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"version": "0.1.0", "imports": []}
    if not isinstance(data, dict):
        return {"version": "0.1.0", "imports": []}
    imports = data.get("imports")
    if not isinstance(imports, list):
        data["imports"] = []
    data.setdefault("version", "0.1.0")
    return data


def upsert_import(manifest: dict[str, object], imported: dict[str, object]) -> None:
    imports = manifest.setdefault("imports", [])
    if not isinstance(imports, list):
        imports = []
        manifest["imports"] = imports

    source = imported.get("source")
    for index, item in enumerate(imports):
        if isinstance(item, dict) and item.get("source") == source:
            imports[index] = imported
            return
    imports.append(imported)


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"all", "agentspec", "ecc", "data-agents"}:
        print("Usage: python3 scripts/import_upstreams.py [all|agentspec|ecc|data-agents]")
        return 1

    IMPORTS_ROOT.mkdir(parents=True, exist_ok=True)
    mode = sys.argv[1]
    manifest_path = IMPORTS_ROOT / "manifest.json"
    manifest = (
        {"version": "0.1.0", "imports": []}
        if mode == "all"
        else load_existing_manifest(manifest_path)
    )
    imported_sources: list[dict[str, object]] = []

    if mode in {"all", "agentspec"}:
        imported = import_source("agentspec", AGENTSPEC_ROOT, AGENTSPEC_IMPORTS)
        upsert_import(manifest, imported)
        imported_sources.append(imported)
    if mode in {"all", "ecc"}:
        imported = import_source("ecc", ECC_ROOT, ECC_IMPORTS)
        upsert_import(manifest, imported)
        imported_sources.append(imported)
    if mode in {"all", "data-agents"}:
        imported = import_source("data-agents", DATA_AGENTS_ROOT, DATA_AGENTS_IMPORTS)
        upsert_import(manifest, imported)
        imported_sources.append(imported)

    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote import manifest: {manifest_path}")
    for item in imported_sources:
        print(f"Imported {item['source']} -> {item['target_root']} ({item['total_files']} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
