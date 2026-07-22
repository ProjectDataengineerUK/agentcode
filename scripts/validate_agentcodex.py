#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from kb_domains import KB_DOMAIN_PATHS, KB_MANAGED_DOMAINS, parse_simple_yaml_domains


ROOT = Path(__file__).resolve().parent.parent
IS_SOURCE_CHECKOUT = (ROOT / "pyproject.toml").exists()
ROUTING_PATH = ROOT / ".agentcodex" / "routing" / "routing.json"
KB_INDEX_PATH = ROOT / ".agentcodex" / "kb" / "index.yaml"
KB_ROOT = ROOT / ".agentcodex" / "kb"
ROLES_PATH = ROOT / ".agentcodex" / "roles" / "roles.yaml"
COMMANDS_DIR = ROOT / "docs" / "commands"
WORKFLOW_DIR = ROOT / "docs" / "workflow"
TEMPLATES_DIR = ROOT / ".agentcodex" / "templates"
COMMANDS_INDEX_PATH = ROOT / "docs" / "COMMANDS.md"
IMPORTS_MANIFEST_PATH = ROOT / ".agentcodex" / "imports" / "manifest.json"
MATURITY5_BASELINE_PATH = ROOT / ".agentcodex" / "maturity" / "maturity5-baseline.json"
WORKFLOW_FIDELITY_PATH = ROOT / ".agentcodex" / "workflow-fidelity.json"
ECC_FIDELITY_PATH = ROOT / ".agentcodex" / "ecc-fidelity.json"
ECC_EXTENSION_PATH = ROOT / ".agentcodex" / "ecc-extension.json"
DATA_AGENTS_EXTENSION_PATH = ROOT / ".agentcodex" / "data-agents-extension.json"
MODEL_ROUTING_PATH = ROOT / ".agentcodex" / "model-routing.json"
HOOKS_PATH = ROOT / ".agentcodex" / "imports" / "agentspec" / "plugin_hooks" / "hooks.json"
GITHUB_WORKFLOWS_DIR = ROOT / ".github" / "workflows"
ECC_IMPORT_ROOT = ROOT / ".agentcodex" / "imports" / "ecc"
DATA_AGENTS_IMPORT_ROOT = ROOT / ".agentcodex" / "imports" / "data-agents"
PERSONAL_PATH_PATTERNS = [
    re.compile(r"/Users/[^/\s]+"),
    re.compile(r"C:\\Users\\[^\\\s]+", re.IGNORECASE),
]
ALLOWED_BUILTIN_ROLES = {"reviewer", "explorer", "domain-researcher"}
COMMAND_REQUIRED_SECTIONS = [
    "## Purpose",
    "## Primary Role",
    "## Inputs",
    "## Procedure",
    "## Outputs",
]
RE_TEXT_FILE = re.compile(r"\.(md|json|yaml|yml|toml|py)$", re.IGNORECASE)
WORKFLOW_PHASES = {"brainstorm", "define", "design", "build", "ship", "iterate"}
WORKFLOW_TEMPLATE_MAP = {
    "brainstorm": "BRAINSTORM_TEMPLATE.md",
    "define": "DEFINE_TEMPLATE.md",
    "design": "DESIGN_TEMPLATE.md",
    "build": "BUILD_REPORT_TEMPLATE.md",
    "ship": "SHIPPED_TEMPLATE.md",
}
WORKFLOW_TEMPLATE_REQUIRED_MARKERS = {
    "BRAINSTORM_TEMPLATE.md": [
        "## Discovery Questions & Answers",
        "## Sample Data Inventory",
        "## Candidate Approaches",
        "## Selected Approach",
        "## Recommendation",
        "## Features Removed (YAGNI)",
        "## Incremental Validations",
        "## Suggested Requirements for Define",
        "## Exit Check",
    ],
    "DEFINE_TEMPLATE.md": [
        "## Input Classification",
        "## Target Users",
        "## Goals",
        "## Success Criteria",
        "## Acceptance Tests",
        "## Technical Context",
        "## Data Contract (if applicable)",
        "## Assumptions",
        "## Clarity Score Breakdown",
        "## Exit Check",
    ],
    "DESIGN_TEMPLATE.md": [
        "## KB Patterns Loaded",
        "## Architecture Overview",
        "## Components",
        "## Key Decisions",
        "## File Manifest",
        "## Agent Assignment Rationale",
        "## Code Patterns",
        "## Testing Strategy",
        "## Error Handling",
        "## Configuration",
        "## Security Considerations",
        "## Observability",
        "## Pipeline Architecture (if applicable)",
        "## Exit Check",
    ],
    "BUILD_REPORT_TEMPLATE.md": [
        "## Build Order",
        "## Task Execution with Agent Attribution",
        "## Agent Contributions",
        "## Files Created",
        "## Files Modified",
        "## Verification Commands",
        "## Verification Results",
        "## Issues Encountered",
        "## Deviations from Design",
        "## Acceptance Test Verification",
        "## Security Review",
        "## Data Quality Results (if applicable)",
        "## Residual Risks",
        "## Final Status",
        "## Exit Check",
    ],
    "SHIPPED_TEMPLATE.md": [
        "## Ship Readiness",
        "## Summary",
        "## Timeline",
        "## Metrics",
        "## What Was Built",
        "## Success Criteria Verification",
        "## Acceptance Review",
        "## Deviations From Design",
        "## Lessons Learned",
        "## Recommendations for Future Work",
        "## Follow-up Work",
        "## Final Risk Notes",
        "## Project Standard Gate",
        "## Archived Artifacts",
        "## Exit Check",
    ],
}
PHASE_REFERENCE_RE = re.compile(r"`(brainstorm|define|design|build|ship|iterate)`")
ROLE_REFERENCE_RE = re.compile(r"`([a-z][a-z0-9-]+)`")
ARTIFACT_TEMPLATE_RE = re.compile(r"([A-Z_]+\{FEATURE\}(?:_\{DATE\})?\.md)")
HYGIENE_ROOTS = [
    ROOT / "README.md",
    ROOT / "AGENTS.md",
    ROOT / "docs",
    ROOT / "scripts",
    ROOT / ".agentcodex",
]
ECC_STYLE_TEXT_ROOTS = [
    ROOT / "README.md",
    ROOT / "AGENTS.md",
    ROOT / "docs",
    ROOT / "scripts",
    ROOT / ".agentcodex" / "commands",
    ROOT / ".agentcodex" / "templates",
    ROOT / "plugins" / "agentcodex" / "skills",
]
ECC_TEXT_EXTENSIONS = re.compile(r"\.(md|json|js|ts|sh|toml|yml|yaml|py)$", re.IGNORECASE)
ECC_COMMAND_REF_RE = re.compile(r"`/([a-z][-a-z0-9]*)`")
ECC_AGENT_PATH_REF_RE = re.compile(r"agents/([a-z][-a-z0-9]*)\.md")
ECC_SKILL_REF_RE = re.compile(r"skills/([a-z][-a-z0-9]*)/")
ECC_WORKFLOW_LINE_RE = re.compile(r"^([a-z][-a-z0-9]*(?:\s*->\s*[a-z][-a-z0-9]*)+)$", re.MULTILINE)
WORKFLOW_SECURITY_RULES = [
    (
        "workflow_run",
        re.compile(r"\bworkflow_run\s*:", re.MULTILINE),
        "workflow_run must not checkout an untrusted workflow_run head ref/repository",
        re.compile(
            r"\$\{\{\s*github\.event\.workflow_run\.(?:head_branch|head_sha|head_repository(?:\.[A-Za-z0-9_.]+)?)\s*\}\}"
            r"|\$\{\{\s*github\.event\.workflow_run\.pull_requests\[\d+\]\.head\.(?:ref|sha|repo\.full_name)\s*\}\}"
        ),
    ),
    (
        "pull_request_target",
        re.compile(r"\bpull_request_target\s*:", re.MULTILINE),
        "pull_request_target must not checkout an untrusted pull_request head ref/repository",
        re.compile(r"\$\{\{\s*github\.event\.pull_request\.head\.(?:ref|sha|repo\.full_name)\s*\}\}"),
    ),
]
def parse_roles_yaml(path: Path) -> dict[str, dict]:
    roles: dict[str, dict] = {}
    current: dict | None = None
    current_id: str | None = None
    current_list_key: str | None = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("version:") or stripped == "roles:":
            continue
        if stripped.startswith("- id:"):
            current_id = stripped.split(":", 1)[1].strip()
            current = {"id": current_id, "kb_domains": [], "owns": [], "escalates_to": []}
            roles[current_id] = current
            current_list_key = None
            continue
        if current is None or current_id is None:
            continue
        if stripped.endswith(":") and stripped[:-1] in {"kb_domains", "owns", "escalates_to"}:
            current_list_key = stripped[:-1]
            continue
        if stripped.startswith("- ") and current_list_key:
            current[current_list_key].append(stripped[2:].strip())
            continue
        if ":" in stripped:
            key, value = stripped.split(":", 1)
            normalized_key = key.strip()
            normalized_value = value.strip()
            if normalized_key in {"kb_domains", "owns", "escalates_to"} and normalized_value == "[]":
                current[normalized_key] = []
            else:
                current[normalized_key] = normalized_value
            current_list_key = None

    return roles


def collect_bullets(section_body: str) -> list[str]:
    values: list[str] = []
    for raw_line in section_body.splitlines():
        line = raw_line.strip()
        if line.startswith("- "):
            values.append(line[2:].strip().strip("`"))
    return values


def parse_section_bullets(text: str, heading: str) -> list[str]:
    pattern = rf"{re.escape(heading)}\n(.*?)(?:\n## |\Z)"
    match = re.search(pattern, text, re.DOTALL)
    if not match:
        return []
    return collect_bullets(match.group(1))


def validate_command_docs(
    errors: list[str],
    domains: list[str],
    roles: dict[str, dict],
) -> list[str]:
    command_names: list[str] = []
    if not COMMANDS_DIR.exists():
        errors.append(f"Missing commands directory: {COMMANDS_DIR}")
        return command_names

    known_roles = set(roles) | ALLOWED_BUILTIN_ROLES
    for command_path in sorted(COMMANDS_DIR.glob("*.md")):
        command_names.append(command_path.name)
        text = command_path.read_text(encoding="utf-8")
        if not text.strip():
            errors.append(f"Command procedure is empty: {command_path}")
            continue

        for section in COMMAND_REQUIRED_SECTIONS:
            if section not in text:
                errors.append(f"Command procedure missing section {section}: {command_path}")

        primary_roles = parse_section_bullets(text, "## Primary Role")
        escalation_roles = parse_section_bullets(text, "## Escalation Roles")
        kb_domains = parse_section_bullets(text, "## KB Domains")

        if not primary_roles:
            errors.append(f"Command procedure missing primary role bullet: {command_path}")
        for role_id in primary_roles + escalation_roles:
            if role_id not in known_roles:
                errors.append(f"Command procedure references unknown role {role_id}: {command_path}")
        for kb_domain in kb_domains:
            if kb_domain not in domains:
                errors.append(f"Command procedure references unknown KB domain {kb_domain}: {command_path}")

    return command_names


def validate_commands_index(errors: list[str], command_names: list[str]) -> None:
    if not COMMANDS_INDEX_PATH.exists():
        errors.append(f"Missing commands index doc: {COMMANDS_INDEX_PATH}")
        return
    text = COMMANDS_INDEX_PATH.read_text(encoding="utf-8")
    indexed = sorted(set(re.findall(r"`docs/commands/([^`]+\.md)`", text)))
    expected = sorted(command_names)
    if indexed != expected:
        missing = sorted(set(expected) - set(indexed))
        extra = sorted(set(indexed) - set(expected))
        if missing:
            errors.append(f"Commands index missing entries: {', '.join(missing)}")
        if extra:
            errors.append(f"Commands index references non-existent procedures: {', '.join(extra)}")


def validate_workflow_docs(errors: list[str], roles: dict[str, dict]) -> None:
    if not WORKFLOW_DIR.exists():
        errors.append(f"Missing workflow docs directory: {WORKFLOW_DIR}")
        return

    known_roles = set(roles) | ALLOWED_BUILTIN_ROLES
    for phase in WORKFLOW_PHASES:
        path = WORKFLOW_DIR / f"{phase}.md"
        if not path.exists():
            errors.append(f"Missing workflow doc for phase {phase}: {path}")
            continue
        text = path.read_text(encoding="utf-8")
        if not text.strip():
            errors.append(f"Workflow doc is empty: {path}")
            continue

        for referenced_phase in PHASE_REFERENCE_RE.findall(text):
            if referenced_phase not in WORKFLOW_PHASES:
                errors.append(f"Workflow doc references unknown phase {referenced_phase}: {path}")

        for role_id in ROLE_REFERENCE_RE.findall(text):
            if role_id in WORKFLOW_PHASES:
                continue
            if role_id.isupper():
                continue
            if role_id not in known_roles:
                errors.append(f"Workflow doc references unknown role {role_id}: {path}")

        for artifact_name in ARTIFACT_TEMPLATE_RE.findall(text):
            expected_template = artifact_name.replace("{FEATURE}", "TEMPLATE").replace("_{DATE}", "")
            if expected_template not in {
                "BRAINSTORM_TEMPLATE.md",
                "DEFINE_TEMPLATE.md",
                "DESIGN_TEMPLATE.md",
                "BUILD_REPORT_TEMPLATE.md",
                "SHIPPED_TEMPLATE.md",
            }:
                continue
            template_path = TEMPLATES_DIR / expected_template
            if not template_path.exists():
                errors.append(f"Workflow doc references missing template {expected_template}: {path}")

    for phase, template_name in WORKFLOW_TEMPLATE_MAP.items():
        template_path = TEMPLATES_DIR / template_name
        if not template_path.exists():
            errors.append(f"Missing workflow template for {phase}: {template_path}")
            continue
        for marker in WORKFLOW_TEMPLATE_REQUIRED_MARKERS.get(template_name, []):
            if marker not in template_path.read_text(encoding="utf-8"):
                errors.append(f"Workflow template {template_name} missing required marker {marker}: {template_path}")


def validate_routing_to_workflows(errors: list[str]) -> None:
    if not ROUTING_PATH.exists():
        return
    routing = json.loads(ROUTING_PATH.read_text(encoding="utf-8"))
    workflow_roles = {
        "workflow-brainstormer",
        "workflow-definer",
        "workflow-designer",
        "workflow-builder",
        "workflow-shipper",
        "workflow-iterator",
    }
    routed = {
        item["preferred_role"]
        for item in routing.get("workflow_phase_routing", [])
    }
    missing = sorted(workflow_roles - routed)
    if missing:
        errors.append(f"Workflow phase routing missing workflow roles: {', '.join(missing)}")


def validate_workflow_fidelity(errors: list[str]) -> None:
    if not WORKFLOW_FIDELITY_PATH.exists():
        errors.append(f"Missing workflow fidelity contract: {WORKFLOW_FIDELITY_PATH}")
        return

    try:
        fidelity = json.loads(WORKFLOW_FIDELITY_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"Invalid workflow fidelity JSON: {exc}")
        return

    source_contract = ROOT / fidelity.get("source", {}).get("contract", "")
    if not source_contract.exists():
        errors.append(f"Workflow fidelity source contract missing: {source_contract}")

    phases = fidelity.get("phases")
    if not isinstance(phases, dict):
        errors.append("Workflow fidelity contract must declare a phases object")
        return

    declared = set(phases)
    missing_phases = WORKFLOW_PHASES - declared
    extra_phases = declared - WORKFLOW_PHASES
    if missing_phases:
        errors.append(f"Workflow fidelity contract missing phases: {', '.join(sorted(missing_phases))}")
    if extra_phases:
        errors.append(f"Workflow fidelity contract declares unknown phases: {', '.join(sorted(extra_phases))}")

    for phase, phase_spec in sorted(phases.items()):
        for source_ref in phase_spec.get("source_refs", []):
            source_path = ROOT / source_ref
            if not source_path.exists():
                errors.append(f"Workflow fidelity source reference missing for {phase}: {source_path}")

        surfaces = phase_spec.get("surfaces", [])
        if not surfaces:
            errors.append(f"Workflow fidelity phase has no active surfaces: {phase}")
            continue

        for surface in surfaces:
            rel_path = surface.get("path")
            if not rel_path:
                errors.append(f"Workflow fidelity surface missing path for phase {phase}")
                continue
            path = ROOT / rel_path
            if not path.exists():
                errors.append(f"Workflow fidelity surface missing for {phase}: {path}")
                continue
            text = path.read_text(encoding="utf-8")
            markers = surface.get("required_markers", [])
            if not markers:
                errors.append(f"Workflow fidelity surface has no required markers for {phase}: {path}")
            for marker in markers:
                if marker not in text:
                    errors.append(
                        f"Workflow fidelity marker missing for {phase}: {marker} in {path}"
                    )


def _count_matching_files(path: Path, pattern: str, exclude_names: list[str] | None = None) -> int:
    excluded = set(exclude_names or [])
    return sum(
        1
        for candidate in path.rglob(pattern)
        if candidate.is_file() and candidate.name not in excluded
    )


def _validate_required_files(
    errors: list[str],
    files: list[str],
    label: str,
    markers: list[str] | None = None,
) -> None:
    for rel_path in files:
        path = ROOT / rel_path
        if not path.exists():
            errors.append(f"ECC fidelity required file missing for {label}: {path}")
            continue
        if markers:
            text = path.read_text(encoding="utf-8")
            for marker in markers:
                if marker not in text:
                    errors.append(f"ECC fidelity marker missing for {label}: {marker} in {path}")


def validate_ecc_fidelity(errors: list[str]) -> None:
    if not ECC_FIDELITY_PATH.exists():
        errors.append(f"Missing ECC fidelity contract: {ECC_FIDELITY_PATH}")
        return

    try:
        fidelity = json.loads(ECC_FIDELITY_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"Invalid ECC fidelity JSON: {exc}")
        return

    source = fidelity.get("source", {})
    source_root = ROOT / source.get("root", "")
    source_manifest = ROOT / source.get("manifest", "")
    if not source_root.exists():
        errors.append(f"ECC fidelity source root missing: {source_root}")
    if not source_manifest.exists():
        errors.append(f"ECC fidelity source manifest missing: {source_manifest}")

    preserved = fidelity.get("preserved_surfaces")
    if not isinstance(preserved, dict) or not preserved:
        errors.append("ECC fidelity contract must declare preserved_surfaces")
        return

    for surface_name, surface in sorted(preserved.items()):
        required_files = surface.get("required_files", [])
        if required_files:
            _validate_required_files(
                errors,
                required_files,
                surface_name,
                surface.get("required_markers"),
            )

        rel_path = surface.get("path")
        if rel_path:
            path = ROOT / rel_path
            if not path.exists():
                errors.append(f"ECC fidelity surface path missing for {surface_name}: {path}")
                continue
            pattern = surface.get("pattern")
            if pattern:
                count = _count_matching_files(path, pattern, surface.get("exclude_names"))
                min_files = surface.get("min_files")
                if min_files is not None and count < min_files:
                    errors.append(
                        f"ECC fidelity surface {surface_name} has {count} files, expected at least {min_files}: {path}"
                    )
            skill_entrypoint = surface.get("skill_entrypoint")
            if skill_entrypoint:
                count = _count_matching_files(path, skill_entrypoint)
                min_entrypoints = surface.get("min_skill_entrypoints")
                if min_entrypoints is not None and count < min_entrypoints:
                    errors.append(
                        f"ECC fidelity surface {surface_name} has {count} skill entrypoints, expected at least {min_entrypoints}: {path}"
                    )

    active = fidelity.get("active_adaptations")
    if not isinstance(active, dict) or not active:
        errors.append("ECC fidelity contract must declare active_adaptations")
        return

    for surface in active.get("codex_runtime", []):
        rel_path = surface.get("path")
        if not rel_path:
            errors.append("ECC fidelity codex_runtime entry missing path")
            continue
        _validate_required_files(
            errors,
            [rel_path],
            "codex_runtime",
            surface.get("required_markers", []),
        )

    direct_roles = active.get("direct_role_matches", {})
    role_names = direct_roles.get("roles", [])
    matches = 0
    for role_name in role_names:
        ecc_role = ROOT / ".agentcodex" / "imports" / "ecc" / "agents" / role_name
        agentcodex_role = ROOT / "docs" / "roles" / role_name
        if not ecc_role.exists():
            errors.append(f"ECC fidelity imported role missing: {ecc_role}")
            continue
        if not agentcodex_role.exists():
            errors.append(f"ECC fidelity active role missing: {agentcodex_role}")
            continue
        matches += 1
    min_matches = direct_roles.get("min_matches")
    if min_matches is not None and matches < min_matches:
        errors.append(f"ECC fidelity role matches below minimum: {matches}/{min_matches}")

    validation_stack = active.get("agentcodex_validation_stack", {})
    _validate_required_files(
        errors,
        validation_stack.get("required_files", []),
        "agentcodex_validation_stack",
    )

    if not fidelity.get("intentional_differences"):
        errors.append("ECC fidelity contract must document intentional_differences")


def validate_ecc_extension_registry(errors: list[str]) -> None:
    if not ECC_EXTENSION_PATH.exists():
        errors.append(f"Missing ECC extension registry: {ECC_EXTENSION_PATH}")
        return
    try:
        registry = json.loads(ECC_EXTENSION_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"Invalid ECC extension registry JSON: {exc}")
        return

    source_root = ROOT / registry.get("source", {}).get("root", "")
    if source_root != ECC_IMPORT_ROOT:
        errors.append(f"ECC extension registry source root mismatch: {source_root}")
    if not source_root.exists():
        errors.append(f"ECC extension registry source root missing: {source_root}")
        return

    counts = registry.get("counts", {})
    actual_counts = {
        "commands": len(list((ECC_IMPORT_ROOT / "commands").glob("*.md"))),
        "agents": len(list((ECC_IMPORT_ROOT / "agents").glob("*.md"))),
        "skills": len(list((ECC_IMPORT_ROOT / "skills").glob("*/SKILL.md"))),
        "rules": len([path for path in (ECC_IMPORT_ROOT / "rules").rglob("*.md") if path.name != "README.md"]),
        "schemas": len(list((ECC_IMPORT_ROOT / "schemas").glob("*.json"))),
        "ci_validators": len([path for path in (ECC_IMPORT_ROOT / "scripts_ci").glob("*") if path.is_file()]),
    }
    for key, actual in actual_counts.items():
        if counts.get(key) != actual:
            errors.append(f"ECC extension registry count mismatch for {key}: registry={counts.get(key)} actual={actual}")

    commands = registry.get("commands", [])
    agents = registry.get("agents", [])
    skills = registry.get("skills", [])
    rules = registry.get("rules", [])
    if len(commands) != actual_counts["commands"]:
        errors.append("ECC extension registry commands list does not match imported command count")
    if len(agents) != actual_counts["agents"]:
        errors.append("ECC extension registry agents list does not match imported agent count")
    if len(skills) != actual_counts["skills"]:
        errors.append("ECC extension registry skills list does not match imported skill count")
    if len(rules) != actual_counts["rules"]:
        errors.append("ECC extension registry rules list does not match imported rule count")

    active_command_names = {path.name for path in COMMANDS_DIR.glob("*.md")}
    active_role_names = {path.name for path in (ROOT / "docs" / "roles").glob("*.md")}
    command_matches = 0
    for command in commands:
        source_path = ROOT / command.get("source_path", "")
        if not source_path.exists():
            errors.append(f"ECC extension registry command source missing: {source_path}")
        command_filename = f"{command.get('id')}.md"
        should_be_active = command_filename in active_command_names
        if command.get("active_agentcodex_command") != should_be_active:
            errors.append(f"ECC extension registry active command flag stale: {command_filename}")
        if should_be_active:
            command_matches += 1
            if command.get("activation") != "already-active":
                errors.append(f"ECC extension registry active command must be marked already-active: {command_filename}")
        elif command.get("activation") != "reference-only":
            errors.append(f"ECC extension registry extension command must be reference-only: {command_filename}")

    role_matches = 0
    for agent in agents:
        source_path = ROOT / agent.get("source_path", "")
        if not source_path.exists():
            errors.append(f"ECC extension registry agent source missing: {source_path}")
        role_filename = f"{agent.get('id')}.md"
        should_be_active = role_filename in active_role_names
        if agent.get("active_agentcodex_role") != should_be_active:
            errors.append(f"ECC extension registry active role flag stale: {role_filename}")
        if should_be_active:
            role_matches += 1
            if agent.get("activation") != "already-active":
                errors.append(f"ECC extension registry active role must be marked already-active: {role_filename}")
        elif agent.get("activation") != "extension-role":
            errors.append(f"ECC extension registry extension role must be extension-role: {role_filename}")

    if counts.get("active_command_name_matches") != command_matches:
        errors.append(
            f"ECC extension registry command match count stale: registry={counts.get('active_command_name_matches')} actual={command_matches}"
        )
    if counts.get("active_role_name_matches") != role_matches:
        errors.append(
            f"ECC extension registry role match count stale: registry={counts.get('active_role_name_matches')} actual={role_matches}"
        )

    policy = registry.get("activation_policy", {})
    if "do not duplicate" not in policy.get("no_duplicate_rule", "").lower():
        errors.append("ECC extension registry must document a no-duplicate rule")


def validate_data_agents_extension_registry(errors: list[str]) -> None:
    if not DATA_AGENTS_EXTENSION_PATH.exists():
        errors.append(f"Missing Data Agents extension registry: {DATA_AGENTS_EXTENSION_PATH}")
        return
    try:
        registry = json.loads(DATA_AGENTS_EXTENSION_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"Invalid Data Agents extension registry JSON: {exc}")
        return

    source_root = ROOT / registry.get("source", {}).get("root", "")
    if source_root != DATA_AGENTS_IMPORT_ROOT:
        errors.append(f"Data Agents extension registry source root mismatch: {source_root}")
    if not source_root.exists():
        errors.append(f"Data Agents extension registry source root missing: {source_root}")
        return

    actual_counts = {
        "agents": len([path for path in (DATA_AGENTS_IMPORT_ROOT / "agents" / "registry").glob("*.md") if path.stem != "_template"]),
        "commands": len([path for path in (DATA_AGENTS_IMPORT_ROOT / "commands").glob("*.py") if path.name != "__init__.py"]),
        "skills": len(list((DATA_AGENTS_IMPORT_ROOT / "skills").rglob("SKILL.md"))),
        "kb_files": len(list((DATA_AGENTS_IMPORT_ROOT / "kb").rglob("*.md"))),
        "mcp_servers": len([path for path in (DATA_AGENTS_IMPORT_ROOT / "mcp_servers").iterdir() if path.is_dir() and path.name != "_template"]),
        "hooks": len(list((DATA_AGENTS_IMPORT_ROOT / "hooks").glob("*.py"))),
        "tests": len(list((DATA_AGENTS_IMPORT_ROOT / "tests").glob("test_*.py"))),
        "templates": len(list((DATA_AGENTS_IMPORT_ROOT / "templates").glob("*.md"))),
    }
    counts = registry.get("counts", {})
    for key, actual in actual_counts.items():
        if counts.get(key) != actual:
            errors.append(f"Data Agents extension registry count mismatch for {key}: registry={counts.get(key)} actual={actual}")

    agents = registry.get("agents", [])
    commands = registry.get("commands", [])
    skills = registry.get("skills", [])
    kb_files = registry.get("kb_files", [])
    mcp_servers = registry.get("mcp_servers", [])
    hooks = registry.get("hooks", [])
    tests = registry.get("tests", [])
    templates = registry.get("templates", [])
    if len(agents) != actual_counts["agents"]:
        errors.append("Data Agents extension registry agents list does not match imported agent count")
    if len(commands) != actual_counts["commands"]:
        errors.append("Data Agents extension registry commands list does not match imported command count")
    if len(skills) != actual_counts["skills"]:
        errors.append("Data Agents extension registry skills list does not match imported skill count")
    if len(kb_files) != actual_counts["kb_files"]:
        errors.append("Data Agents extension registry KB file list does not match imported KB file count")
    if len(mcp_servers) != actual_counts["mcp_servers"]:
        errors.append("Data Agents extension registry MCP server list does not match imported MCP server count")
    if len(hooks) != actual_counts["hooks"]:
        errors.append("Data Agents extension registry hook list does not match imported hook count")
    if len(tests) != actual_counts["tests"]:
        errors.append("Data Agents extension registry test list does not match imported test count")
    if len(templates) != actual_counts["templates"]:
        errors.append("Data Agents extension registry template list does not match imported template count")

    active_role_names = {path.stem for path in (ROOT / "docs" / "roles").glob("*.md")}
    active_command_names = {path.stem for path in COMMANDS_DIR.glob("*.md")}
    mapped_agents = 0
    mapped_commands = 0
    for agent in agents:
        source_path = ROOT / agent.get("source_path", "")
        if not source_path.exists():
            errors.append(f"Data Agents extension registry agent source missing: {source_path}")
        target_role = agent.get("target_agentcodex_role")
        activation = agent.get("activation")
        if activation in {"mapped-to-native-role", "already-active"}:
            mapped_agents += 1
            if not target_role or target_role not in active_role_names:
                errors.append(f"Data Agents extension registry mapped agent target missing: {agent.get('id')} -> {target_role}")
        elif activation not in {"extension-role", "missing-target-role", "reference-only"}:
            errors.append(f"Data Agents extension registry invalid agent activation: {agent.get('id')} -> {activation}")

    for command in commands:
        source_path = ROOT / command.get("source_path", "")
        if not source_path.exists():
            errors.append(f"Data Agents extension registry command source missing: {source_path}")
        target_command = command.get("target_agentcodex_command")
        activation = command.get("activation")
        if activation in {"mapped-to-native-command", "already-active"}:
            mapped_commands += 1
            if not target_command or target_command not in active_command_names:
                errors.append(f"Data Agents extension registry mapped command target missing: {command.get('id')} -> {target_command}")
        elif activation != "reference-only":
            errors.append(f"Data Agents extension registry invalid command activation: {command.get('id')} -> {activation}")

    for path_value in kb_files + hooks + tests + templates:
        source_path = ROOT / path_value
        if not source_path.exists():
            errors.append(f"Data Agents extension registry source missing: {source_path}")

    for skill in skills:
        source_path = ROOT / skill.get("source_path", "")
        if not source_path.exists():
            errors.append(f"Data Agents extension registry skill source missing: {source_path}")

    if counts.get("mapped_agents") != mapped_agents:
        errors.append(f"Data Agents extension registry mapped agent count stale: registry={counts.get('mapped_agents')} actual={mapped_agents}")
    if counts.get("mapped_commands") != mapped_commands:
        errors.append(
            f"Data Agents extension registry mapped command count stale: registry={counts.get('mapped_commands')} actual={mapped_commands}"
        )

    policy = registry.get("activation_policy", {})
    if "do not create" not in policy.get("no_duplicate_rule", "").lower():
        errors.append("Data Agents extension registry must document a no-duplicate rule")
    if "codex" not in policy.get("native_codex_rule", "").lower():
        errors.append("Data Agents extension registry must document a native Codex rule")


def _iter_files(root_path: Path) -> list[Path]:
    if not root_path.exists():
        return []
    if root_path.is_file():
        return [root_path]
    return [
        path
        for path in root_path.rglob("*")
        if path.is_file() and not any(part in {".git", "__pycache__", "node_modules"} for part in path.parts)
    ]


def _strip_fenced_code_blocks(text: str) -> str:
    return re.sub(r"```[\s\S]*?```", "", text)


def _validate_simple_frontmatter(file_label: str, text: str) -> list[str]:
    if not text.startswith("---\n"):
        return []
    end_index = text.find("\n---\n", 4)
    if end_index == -1:
        return [f"{file_label} - frontmatter block is missing a closing --- delimiter"]

    errors: list[str] = []
    block = text[4:end_index]
    for raw_line in block.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not match:
            errors.append(f"{file_label} - invalid frontmatter line: {raw_line}")
            continue
        value = match.group(2).strip()
        is_quoted = (
            (value.startswith('"') and value.endswith('"'))
            or (value.startswith("'") and value.endswith("'"))
        )
        if not is_quoted and value.startswith("[") and not value.endswith("]"):
            errors.append(
                f'{file_label} - frontmatter value for "{match.group(1)}" starts with "[" but is not a closed YAML sequence'
            )
        if not is_quoted and value.startswith("{") and not value.endswith("}"):
            errors.append(
                f'{file_label} - frontmatter value for "{match.group(1)}" starts with "{{" but is not a closed YAML mapping'
            )
    return errors


def validate_ecc_style_no_personal_paths(errors: list[str]) -> None:
    for root_path in ECC_STYLE_TEXT_ROOTS:
        for path in _iter_files(root_path):
            if path == ROOT / "scripts" / "validate_agentcodex.py":
                continue
            if not ECC_TEXT_EXTENSIONS.search(path.name):
                continue
            text = path.read_text(encoding="utf-8")
            for pattern in PERSONAL_PATH_PATTERNS:
                if pattern.search(text):
                    errors.append(f"ECC no-personal-paths violation in {path}")
                    break


def validate_ecc_style_workflow_security(errors: list[str]) -> None:
    if not GITHUB_WORKFLOWS_DIR.exists():
        return
    workflow_files = sorted(
        path
        for path in GITHUB_WORKFLOWS_DIR.iterdir()
        if path.is_file() and path.suffix.lower() in {".yml", ".yaml"}
    )
    for path in workflow_files:
        text = path.read_text(encoding="utf-8")
        checkout_blocks: list[tuple[int, str]] = []
        current_start: int | None = None
        current_lines: list[str] = []
        for line_number, line in enumerate(text.splitlines(), start=1):
            if re.match(r"^\s*-\s+", line):
                if current_start is not None:
                    block_text = "\n".join(current_lines)
                    if re.search(r"uses:\s*actions/checkout@", block_text):
                        checkout_blocks.append((current_start, block_text))
                current_start = line_number
                current_lines = [line]
                continue
            if current_start is not None:
                current_lines.append(line)
        if current_start is not None:
            block_text = "\n".join(current_lines)
            if re.search(r"uses:\s*actions/checkout@", block_text):
                checkout_blocks.append((current_start, block_text))

        for _event, event_pattern, description, expression_pattern in WORKFLOW_SECURITY_RULES:
            if not event_pattern.search(text):
                continue
            for start_line, block_text in checkout_blocks:
                for match in expression_pattern.finditer(block_text):
                    rel_line = block_text[: match.start()].count("\n")
                    errors.append(
                        f"ECC workflow-security violation in {path}:{start_line + rel_line}: {description}"
                    )


def validate_ecc_style_rules(errors: list[str]) -> None:
    rules_dir = ECC_IMPORT_ROOT / "rules"
    if not rules_dir.exists():
        errors.append(f"ECC rules directory missing: {rules_dir}")
        return
    for path in sorted(rules_dir.rglob("*.md")):
        if not path.read_text(encoding="utf-8").strip():
            errors.append(f"ECC rules validation failed: empty rule file {path}")


def validate_ecc_style_skills(errors: list[str]) -> None:
    skills_dir = ECC_IMPORT_ROOT / "skills"
    if not skills_dir.exists():
        errors.append(f"ECC skills directory missing: {skills_dir}")
        return
    for skill_dir in sorted(path for path in skills_dir.iterdir() if path.is_dir()):
        skill_path = skill_dir / "SKILL.md"
        if not skill_path.exists():
            errors.append(f"ECC skills validation failed: missing SKILL.md in {skill_dir}")
            continue
        if not skill_path.read_text(encoding="utf-8").strip():
            errors.append(f"ECC skills validation failed: empty skill file {skill_path}")


def validate_ecc_style_commands(errors: list[str]) -> None:
    commands_dir = ECC_IMPORT_ROOT / "commands"
    agents_dir = ECC_IMPORT_ROOT / "agents"
    skills_dir = ECC_IMPORT_ROOT / "skills"
    if not commands_dir.exists():
        errors.append(f"ECC commands directory missing: {commands_dir}")
        return

    command_files = sorted(path for path in commands_dir.glob("*.md") if path.is_file())
    valid_commands = {path.stem for path in command_files}
    valid_agents = {path.stem for path in agents_dir.glob("*.md")} if agents_dir.exists() else set()
    valid_skills = {path.name for path in skills_dir.iterdir() if path.is_dir()} if skills_dir.exists() else set()
    reserved_skill_roots = {"learned", "imported"}

    for path in command_files:
        text = path.read_text(encoding="utf-8")
        if not text.strip():
            errors.append(f"ECC commands validation failed: empty command file {path}")
            continue
        for error in _validate_simple_frontmatter(path.name, text):
            errors.append(f"ECC commands validation failed: {error}")

        text_without_code = _strip_fenced_code_blocks(text)
        for line in text_without_code.splitlines():
            if re.search(r"creates:|would create:", line, re.IGNORECASE):
                continue
            for match in ECC_COMMAND_REF_RE.finditer(line):
                command_name = match.group(1)
                if command_name not in valid_commands:
                    errors.append(
                        f"ECC commands validation failed: {path.name} references non-existent command /{command_name}"
                    )

        for match in ECC_AGENT_PATH_REF_RE.finditer(text_without_code):
            agent_name = match.group(1)
            if agent_name not in valid_agents:
                errors.append(
                    f"ECC commands validation failed: {path.name} references non-existent agent agents/{agent_name}.md"
                )

        for match in ECC_SKILL_REF_RE.finditer(text_without_code):
            skill_name = match.group(1)
            if skill_name in reserved_skill_roots or skill_name in valid_skills:
                continue
            errors.append(
                f"ECC commands validation failed: {path.name} references non-existent skill skills/{skill_name}/"
            )

        for match in ECC_WORKFLOW_LINE_RE.finditer(text_without_code):
            for agent_name in re.split(r"\s*->\s*", match.group(1)):
                if agent_name not in valid_agents:
                    errors.append(
                        f'ECC commands validation failed: {path.name} workflow references non-existent agent "{agent_name}"'
                    )


def validate_imports_manifest(errors: list[str]) -> None:
    if not IS_SOURCE_CHECKOUT and not IMPORTS_MANIFEST_PATH.exists():
        return
    if not IMPORTS_MANIFEST_PATH.exists():
        errors.append(f"Missing imports manifest: {IMPORTS_MANIFEST_PATH}")
        return

    try:
        manifest = json.loads(IMPORTS_MANIFEST_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"Invalid imports manifest JSON: {exc}")
        return

    imports = manifest.get("imports", [])
    if not imports:
        errors.append("Imports manifest does not declare any imported sources")
        return

    for source in imports:
        source_name = source.get("source", "<unknown>")
        target_root = Path(source.get("target_root", ""))
        if not target_root.exists():
            errors.append(f"Imported source target_root missing for {source_name}: {target_root}")
        for item in source.get("imports", []):
            destination = Path(item.get("destination", ""))
            status = item.get("status")
            if status != "copied":
                errors.append(
                    f"Import entry for {source_name}/{item.get('name', '<unknown>')} not copied: {status}"
                )
                continue
            if not destination.exists():
                errors.append(f"Imported destination missing for {source_name}: {destination}")


def validate_maturity5_baseline(errors: list[str]) -> None:
    if not MATURITY5_BASELINE_PATH.exists():
        errors.append(f"Missing maturity baseline manifest: {MATURITY5_BASELINE_PATH}")
        return
    try:
        baseline = json.loads(MATURITY5_BASELINE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"Invalid maturity baseline JSON: {exc}")
        return
    required_keys = {"version", "name", "scaffold_root", "default_profile", "profiles"}
    missing = sorted(required_keys - set(baseline))
    if missing:
        errors.append(f"Maturity baseline missing keys: {', '.join(missing)}")
        return
    if not baseline["profiles"]:
        errors.append("Maturity baseline does not declare any profiles")
        return
    profile_ids = {profile.get("id") for profile in baseline["profiles"]}
    if baseline["default_profile"] not in profile_ids:
        errors.append("Maturity baseline default_profile does not match any declared profile")
    for profile in baseline["profiles"]:
        if "id" not in profile:
            errors.append("Maturity baseline profile missing id")
            continue
        if not profile.get("dimensions"):
            errors.append(f"Maturity baseline profile has no dimensions: {profile['id']}")
            continue
        for dimension in profile["dimensions"]:
            if "id" not in dimension:
                errors.append(f"Maturity baseline profile {profile['id']} has a dimension without id")
                continue
            if not any(
                key in dimension
                for key in ("required_blocks", "required_control_checks", "required_feature_paths", "required_repo_paths")
            ):
                errors.append(f"Maturity baseline dimension has no evidence requirements: {profile['id']}/{dimension['id']}")


def validate_model_routing(errors: list[str], roles: dict[str, dict]) -> None:
    if not MODEL_ROUTING_PATH.exists():
        errors.append(f"Missing model routing policy: {MODEL_ROUTING_PATH}")
        return
    try:
        policy = json.loads(MODEL_ROUTING_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"Invalid model routing policy JSON: {exc}")
        return

    serialized = json.dumps(policy)
    for forbidden in ["${CLAUDE_PLUGIN_ROOT}", "sonnet", "opus", "haiku"]:
        if forbidden in serialized:
            errors.append(f"Model routing policy contains Claude-era model/path marker: {forbidden}")

    for key in [
        "model_tiers",
        "activities",
        "token_policy",
        "role_activity_overrides",
        "role_suffix_fallbacks",
        "audit",
    ]:
        if key not in policy:
            errors.append(f"Model routing policy missing key: {key}")

    model_tiers = policy.get("model_tiers", {})
    activities = policy.get("activities", {})
    if not model_tiers:
        errors.append("Model routing policy does not declare model tiers")
    if not activities:
        errors.append("Model routing policy does not declare activities")

    for tier_id, tier in model_tiers.items():
        for key in ["model", "reasoning_effort", "use_for"]:
            if key not in tier:
                errors.append(f"Model tier {tier_id} missing key: {key}")
    for activity_id, activity in activities.items():
        for key in ["tier", "low_budget_tier", "high_risk_tier", "keywords"]:
            if key not in activity:
                errors.append(f"Model routing activity {activity_id} missing key: {key}")
                continue
            if key.endswith("tier") and activity.get(key) not in model_tiers:
                errors.append(f"Model routing activity {activity_id} references unknown tier: {activity.get(key)}")

    valid_activities = set(activities)
    for role_id, activity_id in policy.get("role_activity_overrides", {}).items():
        if activity_id not in valid_activities:
            errors.append(f"Model routing role override references unknown activity: {role_id} -> {activity_id}")
    for suffix, activity_id in policy.get("role_suffix_fallbacks", {}).items():
        if activity_id not in valid_activities:
            errors.append(f"Model routing suffix fallback references unknown activity: {suffix} -> {activity_id}")

    default_role_activity = policy.get("default_role_activity")
    if default_role_activity and default_role_activity not in valid_activities:
        errors.append(f"Model routing default_role_activity references unknown activity: {default_role_activity}")

    unresolved_roles = []
    for role_id in roles:
        resolved = policy.get("role_activity_overrides", {}).get(role_id)
        if not resolved:
            for suffix, activity_id in policy.get("role_suffix_fallbacks", {}).items():
                if role_id.endswith(f"-{suffix}") or role_id == suffix:
                    resolved = activity_id
                    break
        if not resolved:
            resolved = default_role_activity
        if resolved not in valid_activities:
            unresolved_roles.append(role_id)
    if unresolved_roles:
        errors.append(f"Model routing policy does not cover roles: {', '.join(sorted(unresolved_roles))}")


def validate_imported_hook_reference(errors: list[str]) -> None:
    if not IS_SOURCE_CHECKOUT and not HOOKS_PATH.exists():
        return
    if not HOOKS_PATH.exists():
        errors.append(f"Missing imported AgentSpec hooks file: {HOOKS_PATH}")
        return

    try:
        hooks_data = json.loads(HOOKS_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"Invalid AgentSpec hooks JSON: {exc}")
        return

    session_hooks = hooks_data.get("hooks", {}).get("SessionStart", [])
    if not session_hooks:
        errors.append("Imported AgentSpec hooks do not declare SessionStart entries")


def validate_text_hygiene(errors: list[str]) -> None:
    for root_path in HYGIENE_ROOTS:
        if not root_path.exists():
            continue
        candidate_paths = [root_path] if root_path.is_file() else root_path.rglob("*")
        for path in candidate_paths:
            if not path.is_file():
                continue
            if any(part in {".git", "__pycache__", ".venv", ".venv-packaging"} for part in path.parts):
                continue
            if path == ROOT / "scripts" / "validate_agentcodex.py":
                continue
            if ".agentcodex" in path.parts and "imports" in path.parts:
                continue
            if not RE_TEXT_FILE.search(path.name):
                continue
            text = path.read_text(encoding="utf-8")
            if "\u200b" in text or "\ufeff" in text:
                errors.append(f"Text hygiene issue in {path}: contains zero-width or BOM characters")
            for pattern in PERSONAL_PATH_PATTERNS:
                if pattern.search(text):
                    errors.append(f"Text hygiene issue in {path}: contains personal absolute path")
                    break


def main() -> int:
    errors: list[str] = []

    if not ROUTING_PATH.exists():
        errors.append(f"Missing routing manifest: {ROUTING_PATH}")
    else:
        try:
            routing = json.loads(ROUTING_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"Invalid routing.json: {exc}")
            routing = None
        if routing:
            for key in [
                "workflow_phase_routing",
                "data_engineering_routing",
                "domain_routing",
                "platform_routing",
                "control_routing",
                "file_pattern_hints",
                "escalations",
            ]:
                if key not in routing:
                    errors.append(f"routing.json missing key: {key}")

    if not KB_INDEX_PATH.exists():
        errors.append(f"Missing KB index: {KB_INDEX_PATH}")
        domains = []
    else:
        domains = parse_simple_yaml_domains(KB_INDEX_PATH)
        if not domains:
            errors.append("KB index does not declare any domains")
        if sorted(domains) != sorted(KB_MANAGED_DOMAINS):
            errors.append(
                "KB index domains do not match managed scaffold domains: "
                f"index={domains} managed={KB_MANAGED_DOMAINS}"
            )

    for domain in domains:
        domain_dir = KB_ROOT / KB_DOMAIN_PATHS[domain]
        index_md = domain_dir / "index.md"
        index_md_alt = domain_dir / "INDEX.md"
        quick_ref = domain_dir / "quick-reference.md"
        if not domain_dir.exists():
            errors.append(f"KB domain directory missing: {domain_dir}")
            continue
        if not index_md.exists() and not index_md_alt.exists():
            errors.append(f"KB domain missing index.md: {index_md}")
        if domain not in {
            "governance",
            "lineage",
            "observability",
            "access-control",
            "data-contracts",
            "azure",
            "databricks",
            "snowflake",
            "mcp",
            "rag",
        } and not quick_ref.exists():
            errors.append(f"KB domain missing quick-reference.md: {quick_ref}")

    if not ROLES_PATH.exists():
        errors.append(f"Missing roles manifest: {ROLES_PATH}")
        roles = {}
    else:
        roles = parse_roles_yaml(ROLES_PATH)
        if not roles:
            errors.append("Roles manifest does not declare any roles")

    for role_id, role in roles.items():
        doc_path = ROOT / role.get("doc", "")
        if not doc_path.exists():
            errors.append(f"Role doc missing for {role_id}: {doc_path}")
        for kb_domain in role.get("kb_domains", []):
            if kb_domain not in domains:
                errors.append(f"Role {role_id} references unknown KB domain: {kb_domain}")
            if kb_domain not in KB_MANAGED_DOMAINS:
                errors.append(f"Role {role_id} references unmanaged KB domain: {kb_domain}")

    command_names = validate_command_docs(errors, domains, roles)
    validate_commands_index(errors, command_names)
    validate_workflow_docs(errors, roles)
    validate_workflow_fidelity(errors)
    validate_ecc_fidelity(errors)
    validate_ecc_extension_registry(errors)
    validate_data_agents_extension_registry(errors)
    validate_model_routing(errors, roles)
    validate_ecc_style_no_personal_paths(errors)
    validate_ecc_style_workflow_security(errors)
    validate_ecc_style_rules(errors)
    validate_ecc_style_skills(errors)
    validate_ecc_style_commands(errors)

    if ROUTING_PATH.exists() and roles:
        routing = json.loads(ROUTING_PATH.read_text(encoding="utf-8"))
        routed_roles = set()
        for section in [
            "workflow_phase_routing",
            "data_engineering_routing",
            "domain_routing",
            "platform_routing",
            "control_routing",
            "file_pattern_hints",
        ]:
            for item in routing.get(section, []):
                routed_roles.add(item["preferred_role"])
                for key in ("explore_first_with", "review_with", "research_with"):
                    if key in item:
                        routed_roles.add(item[key])
        for item in routing.get("escalations", []):
            routed_roles.add(item["from"])
            routed_roles.add(item["to"])
        for role_id in sorted(routed_roles):
            if role_id not in roles and role_id not in {"domain-researcher", "reviewer", "explorer"}:
                errors.append(f"Routing references unknown role: {role_id}")
    validate_routing_to_workflows(errors)

    validate_imports_manifest(errors)
    validate_maturity5_baseline(errors)
    validate_imported_hook_reference(errors)
    validate_text_hygiene(errors)

    if errors:
        print("AgentCodex validation failed:\n")
        for error in errors:
            print(f"- {error}")
        return 1

    print("AgentCodex validation passed.")
    print(f"Validated routing manifest: {ROUTING_PATH}")
    print(f"Validated KB domains: {', '.join(domains)}")
    print(f"Validated roles manifest: {ROLES_PATH}")
    print(f"Validated command procedures: {', '.join(command_names)}")
    if WORKFLOW_FIDELITY_PATH.exists():
        print(f"Validated workflow fidelity contract: {WORKFLOW_FIDELITY_PATH}")
    if ECC_FIDELITY_PATH.exists():
        print(f"Validated ECC fidelity contract: {ECC_FIDELITY_PATH}")
    if ECC_EXTENSION_PATH.exists():
        print(f"Validated ECC extension registry: {ECC_EXTENSION_PATH}")
    if DATA_AGENTS_EXTENSION_PATH.exists():
        print(f"Validated Data Agents extension registry: {DATA_AGENTS_EXTENSION_PATH}")
    if MODEL_ROUTING_PATH.exists():
        print(f"Validated model routing policy: {MODEL_ROUTING_PATH}")
    print("Validated ECC-style no-personal-paths, workflow-security, rules, skills, and commands checks.")
    if IMPORTS_MANIFEST_PATH.exists():
        print(f"Validated imports manifest: {IMPORTS_MANIFEST_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
