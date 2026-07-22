#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
STATUS_DOC = ROOT / "docs" / "STATUS.md"
PROJECT_STANDARD = ROOT / ".agentcodex" / "project-standard.json"
MATURITY5_BASELINE = ROOT / ".agentcodex" / "maturity" / "maturity5-baseline.json"
WORKFLOW_FIDELITY = ROOT / ".agentcodex" / "workflow-fidelity.json"
ECC_FIDELITY = ROOT / ".agentcodex" / "ecc-fidelity.json"
ECC_EXTENSION = ROOT / ".agentcodex" / "ecc-extension.json"
DATA_AGENTS_EXTENSION = ROOT / ".agentcodex" / "data-agents-extension.json"
MODEL_ROUTING = ROOT / ".agentcodex" / "model-routing.json"
MODEL_ROUTING_LATEST = ROOT / ".agentcodex" / "reports" / "model-routing" / "latest-selection.json"
ROLES_DIR = ROOT / "docs" / "roles"
COMMANDS_DIR = ROOT / "docs" / "commands"
CODEX_AGENTS_DIR = ROOT / ".codex" / "agents"
HISTORY_DIR = ROOT / ".agentcodex" / "history"
ADR_DIR = ROOT / "docs" / "adr"
AGENTSPEC_AGENTS_DIR = ROOT / ".agentcodex" / "imports" / "agentspec" / "agents"
ECC_AGENTS_DIR = ROOT / ".agentcodex" / "imports" / "ecc" / "agents"


def count_files(path: Path, pattern: str) -> int:
    if not path.exists():
        return 0
    return len(list(path.glob(pattern)))


def file_stems(path: Path, pattern: str) -> set[str]:
    if not path.exists():
        return set()
    return {item.stem for item in path.glob(pattern)}


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    standard = json.loads(PROJECT_STANDARD.read_text(encoding="utf-8"))
    maturity = json.loads(MATURITY5_BASELINE.read_text(encoding="utf-8"))
    workflow_fidelity = json.loads(WORKFLOW_FIDELITY.read_text(encoding="utf-8"))
    ecc_fidelity = json.loads(ECC_FIDELITY.read_text(encoding="utf-8"))
    ecc_extension = json.loads(ECC_EXTENSION.read_text(encoding="utf-8"))
    data_agents_extension = json.loads(DATA_AGENTS_EXTENSION.read_text(encoding="utf-8"))
    model_routing = load_json(MODEL_ROUTING)
    latest_model_selection = load_json(MODEL_ROUTING_LATEST)
    block_ids = [block["id"] for block in standard["blocks"]]
    maturity_profiles = maturity["profiles"]
    workflow_phases = sorted(workflow_fidelity["phases"])
    active_role_stems = file_stems(ROLES_DIR, "*.md")
    agentspec_stems = file_stems(AGENTSPEC_AGENTS_DIR, "**/*.md")
    ecc_stems = file_stems(ECC_AGENTS_DIR, "*.md")
    upstream_stems = agentspec_stems | ecc_stems
    exact_matches = active_role_stems & upstream_stems

    lines = [
        "# Status",
        "",
        "Generated status snapshot for AgentCodex.",
        "",
        "## Current Surface",
        "",
        f"- documented roles: {count_files(ROLES_DIR, '*.md')}",
        f"- command procedures: {count_files(COMMANDS_DIR, '*.md')}",
        f"- codex agents: {count_files(CODEX_AGENTS_DIR, '*.toml')}",
        f"- ADRs: {max(count_files(ADR_DIR, '*.md') - 1, 0)}",
        f"- history entries: {count_files(HISTORY_DIR, '*.md')}",
        "",
        "## Upstream Role Coverage",
        "",
        "- coverage report: `docs/ROLE-COVERAGE.md`",
        f"- imported AgentSpec files under `.agentcodex/imports/agentspec/agents/`: {len(agentspec_stems)}",
        f"- imported ECC agents under `.agentcodex/imports/ecc/agents/`: {len(ecc_stems)}",
        f"- gross imported AgentSpec + ECC files: {len(agentspec_stems) + len(ecc_stems)}",
        f"- unique imported filename stems: {len(upstream_stems)}",
        f"- exact upstream stems already active as AgentCodex roles: {len(exact_matches)}",
        f"- exact upstream stems not active as AgentCodex roles: {len(upstream_stems - active_role_stems)}",
        f"- AgentCodex-native role stems beyond exact upstream matches: {len(active_role_stems - upstream_stems)}",
        "",
        "## Project Standard",
        "",
        f"- manifest: `.agentcodex/project-standard.json`",
        f"- version: {standard['version']}",
        f"- scaffold root: `{standard['feature_scaffold_root']}`",
        f"- total blocks: {len(block_ids)}",
        "",
        "Blocks:",
    ]
    lines.extend(f"- `{block_id}`" for block_id in block_ids)
    lines.extend(
        [
            "",
            "## Maturity 5 Baseline",
            "",
            "- manifest: `.agentcodex/maturity/maturity5-baseline.json`",
            f"- version: {maturity['version']}",
            f"- default profile: `{maturity['default_profile']}`",
            f"- profiles: {len(maturity_profiles)}",
            "",
            "Profiles:",
        ]
    )
    for profile in maturity_profiles:
        lines.append(f"- `{profile['id']}`: {profile['name']}")
    lines.extend(
        [
            "",
            "## Workflow Fidelity",
            "",
            "- manifest: `.agentcodex/workflow-fidelity.json`",
            f"- version: {workflow_fidelity['version']}",
            f"- source contract: `{workflow_fidelity['source']['contract']}`",
            f"- phases: {len(workflow_phases)}",
            "",
            "Phases:",
        ]
    )
    lines.extend(f"- `{phase}`" for phase in workflow_phases)
    preserved_ecc = ecc_fidelity["preserved_surfaces"]
    active_ecc = ecc_fidelity["active_adaptations"]
    lines.extend(
        [
            "",
            "## ECC Fidelity",
            "",
            "- manifest: `.agentcodex/ecc-fidelity.json`",
            f"- version: {ecc_fidelity['version']}",
            f"- source root: `{ecc_fidelity['source']['root']}`",
            f"- preserved surfaces: {len(preserved_ecc)}",
            f"- codex runtime adaptations: {len(active_ecc.get('codex_runtime', []))}",
            f"- direct ECC role matches: {len(active_ecc.get('direct_role_matches', {}).get('roles', []))}",
            f"- validation stack files: {len(active_ecc.get('agentcodex_validation_stack', {}).get('required_files', []))}",
            f"- ported ECC validator checks: {len(active_ecc.get('ported_ecc_validator_checks', {}).get('checks', []))}",
            "",
            "## ECC Extension Registry",
            "",
            "- manifest: `.agentcodex/ecc-extension.json`",
            f"- commands: {ecc_extension['counts']['commands']}",
            f"- agents: {ecc_extension['counts']['agents']}",
            f"- skills: {ecc_extension['counts']['skills']}",
            f"- rules: {ecc_extension['counts']['rules']}",
            f"- install modules: {ecc_extension['counts']['modules']}",
            f"- Codex/OpenCode modules: {len(ecc_extension['codex_or_opencode_modules'])}",
            f"- active command name matches: {ecc_extension['counts']['active_command_name_matches']}",
            f"- active role name matches: {ecc_extension['counts']['active_role_name_matches']}",
            "",
            "## Data Agents Extension Registry",
            "",
            "- manifest: `.agentcodex/data-agents-extension.json`",
            f"- agents: {data_agents_extension['counts']['agents']}",
            f"- commands: {data_agents_extension['counts']['commands']}",
            f"- skills: {data_agents_extension['counts']['skills']}",
            f"- KB files: {data_agents_extension['counts']['kb_files']}",
            f"- MCP servers: {data_agents_extension['counts']['mcp_servers']}",
            f"- hooks: {data_agents_extension['counts']['hooks']}",
            f"- tests: {data_agents_extension['counts']['tests']}",
            f"- templates: {data_agents_extension['counts']['templates']}",
            f"- mapped agents: {data_agents_extension['counts']['mapped_agents']}",
            f"- mapped commands: {data_agents_extension['counts']['mapped_commands']}",
        ]
    )
    lines.extend(
        [
            "",
            "## Model Routing",
            "",
            "- manifest: `.agentcodex/model-routing.json`",
            f"- version: {model_routing.get('version', 'missing')}",
            f"- model tiers: {len(model_routing.get('model_tiers', {}))}",
            f"- activities: {len(model_routing.get('activities', {}))}",
            f"- role overrides: {len(model_routing.get('role_activity_overrides', {}))}",
            f"- latest selected model: `{latest_model_selection.get('model', 'none')}`",
            f"- latest activity: `{latest_model_selection.get('activity', 'none')}`",
            f"- latest tier: `{latest_model_selection.get('tier', 'none')}`",
            "",
            "## Automation",
            "",
            "- `agentcodex refresh-all` refreshes generated artifacts and validates the repo",
            "- `agentcodex model-route [task]` records automatic model selection for token and risk control",
            "- `agentcodex readiness-report <target-project-dir>` writes a project readiness report",
            "- `agentcodex ship-gate <target-project-dir>` enforces readiness before ship",
            "- `agentcodex control-plane-check <target-project-dir>` scores multi-agent, token, cost, and security/compliance readiness",
            "- `agentcodex maturity5-check <target-project-dir> [--profile <profile-id>]` evaluates the executable DataOps + LLMOps maturity baseline",
            "- `agentcodex install-local-automation` prepares repo-local git hooks when a `.git` root exists",
            "",
            "## Control Plane",
            "",
            "- `agentcodex control-plane-check <target-project-dir>` is the authoritative enterprise gate for `multi-agent`, `token`, `cost`, and `security`",
            "- `agentcodex enterprise-readiness <target-project-dir>` is a concise alias for the same control-plane evaluation",
            "- `fail` means a structural gap that blocks enterprise readiness",
            "- `warn` means the surface exists but still contains placeholder or incomplete operational content",
            "- `pass` means the evaluated control surface has no detected gaps in the current file-based checks",
            "",
        ]
    )

    STATUS_DOC.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote status doc: {STATUS_DOC}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
