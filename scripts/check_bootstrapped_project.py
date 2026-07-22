#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from kb_domains import KB_DOMAIN_PATHS, KB_MANAGED_DOMAINS, parse_simple_yaml_domains


REQUIRED_DIRS = [
    ".agentcodex/features",
    ".agentcodex/reports",
    ".agentcodex/archive",
    ".agentcodex/history",
    ".agentcodex/templates",
    ".agentcodex/commands",
    ".agentcodex/kb",
    ".agentcodex/routing",
    ".agentcodex/maturity",
]
REQUIRED_FILES = [
    "AGENTS.md",
    ".agentcodex/PROJECT_AGENTSCODEX.md",
    ".agentcodex/features/DEFINE_EXAMPLE_PROJECT_FEATURE.md",
    ".agentcodex/features/example-project-standard/CHECKLIST.md",
    ".agentcodex/project-standard.json",
    ".agentcodex/maturity/maturity5-baseline.json",
    ".agentcodex/routing/routing.json",
    ".agentcodex/kb/index.yaml",
    ".agentcodex/kb/README.md",
]
REQUIRED_COMMANDS = [
    "brainstorm.md",
    "start.md",
    "daily-tasks.md",
    "model-route.md",
    "define.md",
    "design.md",
    "build.md",
    "ship.md",
    "iterate.md",
    "create-pr.md",
    "ai-pipeline.md",
    "create-kb.md",
    "data-contract.md",
    "data-quality.md",
    "diff-review.md",
    "fact-check.md",
    "generate-slides.md",
    "generate-visual-plan.md",
    "generate-web-diagram.md",
    "judge.md",
    "lakehouse.md",
    "meeting.md",
    "memory.md",
    "migrate.md",
    "pipeline.md",
    "plan-review.md",
    "project-recap.md",
    "readme-maker.md",
    "review.md",
    "schema.md",
    "share.md",
    "sql-review.md",
    "status.md",
    "sync-context.md",
]
REQUIRED_TEMPLATES = [
    "BRAINSTORM_TEMPLATE.md",
    "BUILD_REPORT_TEMPLATE.md",
    "CONTEXT_HISTORY_TEMPLATE.md",
    "DAILY_TASKS_TEMPLATE.md",
    "DEFINE_TEMPLATE.md",
    "DESIGN_TEMPLATE.md",
    "SHIPPED_TEMPLATE.md",
]
REQUIRED_ROUTING_KEYS = [
    "workflow_phase_routing",
    "data_engineering_routing",
    "file_pattern_hints",
    "escalations",
]
COMMAND_REQUIRED_SECTIONS = [
    "## Purpose",
    "## Primary Role",
    "## Inputs",
    "## Procedure",
    "## Outputs",
]
TEMPLATE_REQUIRED_MARKERS = {
    "BRAINSTORM_TEMPLATE.md": [
        "## Candidate Approaches",
        "## Discovery Questions & Answers",
        "## Sample Data Inventory",
        "## Incremental Validations",
        "## Suggested Requirements for Define",
        "## Recommendation",
        "## Exit Check",
    ],
    "BUILD_REPORT_TEMPLATE.md": [
        "## Build Order",
        "## Task Execution with Agent Attribution",
        "## Files Created",
        "## Files Modified",
        "## Verification Commands",
        "## Verification Results",
        "## Acceptance Test Verification",
        "## Security Review",
        "## Residual Risks",
        "## Exit Check",
    ],
    "CONTEXT_HISTORY_TEMPLATE.md": [
        "## Scope",
        "## Current State",
        "## Resume Prompt",
    ],
    "DEFINE_TEMPLATE.md": [
        "## Success Criteria",
        "## Acceptance Tests",
        "## Data Contract (if applicable)",
        "## Assumptions",
        "## Clarity Score Breakdown",
    ],
    "DESIGN_TEMPLATE.md": [
        "## KB Patterns Loaded",
        "## Components",
        "## Key Decisions",
        "## File Manifest",
        "## Agent Assignment Rationale",
        "## Code Patterns",
        "## Testing Strategy",
        "## Error Handling",
        "## Security Considerations",
        "## Observability",
        "## Exit Check",
    ],
    "SHIPPED_TEMPLATE.md": [
        "## Ship Readiness",
        "## Timeline",
        "## Metrics",
        "## What Was Built",
        "## Success Criteria Verification",
        "## Lessons Learned",
        "## Archived Artifacts",
        "## Project Standard Gate",
        "## Exit Check",
    ],
}
FEATURE_ARTIFACT_RE = re.compile(
    r"^(?:BRAINSTORM|DEFINE|DESIGN|BUILD_REPORT|SHIPPED)_(?P<feature>[A-Z0-9_]+)\.md$"
)
HISTORY_FILE_RE = re.compile(r"^CONTEXT_(?P<feature>[A-Z0-9_]+)_\d{4}-\d{2}-\d{2}\.md$")
PROJECT_STANDARD_MANIFEST = Path(__file__).resolve().parent.parent / ".agentcodex" / "project-standard.json"
PLACEHOLDER_PHRASES = {
    "Use textual diagram notation or Mermaid here.",
    "Store schema specs, examples, and evolution notes here.",
    "Store logical and analytical model notes here.",
    "Store transformation steps, rules, and incremental notes here.",
    "Store validation test cases, fixtures, and smoke test notes here.",
    "Store table, event, and payload contract definitions here.",
    "Store API, async, tool, or MCP contract definitions here.",
    "Document only the integrations actually used by the feature.",
    "If this feature does not define project-local agents, justify that here explicitly.",
    "Describe project-local agents only when the feature has agentic behavior.",
    "Document tools and capability boundaries for feature-local agents here.",
    "Document prompts, guardrails, and output contracts for feature-local agents here.",
    "Store feature-specific domain notes here.",
    "Store feature-specific reusable patterns here.",
    "Store feature-local decisions that do not need a global ADR here.",
    "Store infrastructure manifests or infra module references here.",
    "Record feature-local architecture decisions here.",
    "Store executable pipeline manifests, stage notes, or runbook links here.",
}


def require_text_marker(errors: list[str], path: Path, marker: str) -> None:
    if marker not in path.read_text(encoding="utf-8"):
        errors.append(f"Missing expected marker '{marker}' in {path}")


def collect_extra_files(directory: Path, expected_names: set[str], pattern: str = "*") -> list[Path]:
    extras: list[Path] = []
    if not directory.exists():
        return extras
    for path in sorted(directory.glob(pattern)):
        if path.is_file() and path.name not in expected_names:
            extras.append(path)
    return extras


def load_project_standard_manifest() -> dict:
    return json.loads(PROJECT_STANDARD_MANIFEST.read_text(encoding="utf-8"))


def has_explicit_not_applicable(text: str) -> bool:
    lowered = text.casefold()
    return "not applicable" in lowered or "não aplic" in lowered or "nao aplic" in lowered


def is_placeholder_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return True
    if stripped in PLACEHOLDER_PHRASES:
        return True
    if stripped in {"|---|---|", "| | |"}:
        return True
    if stripped.startswith("- ") and stripped.endswith(":"):
        return True
    if stripped.startswith("|") and stripped.endswith("|") and stripped.count("|") <= 3:
        return True
    return False


def has_meaningful_content(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if has_explicit_not_applicable(text):
        return True
    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if is_placeholder_line(stripped):
            continue
        if ":" in stripped:
            _, remainder = stripped.split(":", 1)
            if remainder.strip():
                return True
        elif len(stripped) >= 12:
            return True
    return False


def normalize_project_standard_artifact(artifact: str | dict) -> tuple[str, list[str]]:
    if isinstance(artifact, str):
        return artifact, []
    return artifact["path"], artifact.get("required_markers", [])


def validate_project_standard_feature(
    root: Path,
    project_standard: dict,
    errors: list[str],
    notes: list[str],
    strict: bool,
) -> None:
    checklist_path = root / "CHECKLIST.md"
    if not checklist_path.exists():
        if strict:
            errors.append(f"Missing project standard checklist: {checklist_path}")
        else:
            notes.append(f"Project standard example scaffold present without checklist validation target: {root}")
        return

    checklist_text = checklist_path.read_text(encoding="utf-8")
    for block in project_standard["blocks"]:
        if block["id"] not in checklist_text:
            target = errors if strict else notes
            target.append(f"Project standard checklist missing item '{block['id']}' in {checklist_path}")
        if not block.get("required", True):
            continue
        for artifact in block.get("artifacts", []):
            rel, required_markers = normalize_project_standard_artifact(artifact)
            path = root / rel
            if not path.exists():
                target = errors if strict else notes
                target.append(f"Missing project standard artifact: {path}")
                continue
            if path.is_file() and path.suffix == ".md" and not has_meaningful_content(path):
                target = errors if strict else notes
                target.append(f"Project standard artifact still looks like placeholder content: {path}")
                continue
            if path.is_file() and required_markers:
                text = path.read_text(encoding="utf-8")
                if not has_explicit_not_applicable(text):
                    for marker in required_markers:
                        if marker not in text:
                            target = errors if strict else notes
                            target.append(f"Project standard artifact missing marker '{marker}' in {path}")


def collect_extra_dirs(directory: Path, expected_names: set[str]) -> list[Path]:
    extras: list[Path] = []
    if not directory.exists():
        return extras
    for path in sorted(directory.iterdir()):
        if path.is_dir() and path.name not in expected_names:
            extras.append(path)
    return extras


def collect_feature_names(directory: Path) -> set[str]:
    features: set[str] = set()
    if not directory.exists():
        return features
    for path in directory.glob("*.md"):
        match = FEATURE_ARTIFACT_RE.match(path.name)
        if not match:
            continue
        feature = match.group("feature")
        if feature == "EXAMPLE_PROJECT_FEATURE":
            continue
        features.add(feature)
    return features


def collect_history_features(directory: Path) -> set[str]:
    features: set[str] = set()
    if not directory.exists():
        return features
    for path in directory.glob("*.md"):
        match = HISTORY_FILE_RE.match(path.name)
        if match:
            features.add(match.group("feature"))
    return features


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/check_bootstrapped_project.py <target-project-dir>")
        return 1

    target = Path(sys.argv[1]).resolve()
    errors: list[str] = []
    notes: list[str] = []

    if not target.exists():
        print(f"Target does not exist: {target}")
        return 1

    for rel in REQUIRED_DIRS:
        path = target / rel
        if not path.exists():
            errors.append(f"Missing required directory: {path}")
        elif not path.is_dir():
            errors.append(f"Expected directory but found something else: {path}")

    for rel in REQUIRED_FILES:
        path = target / rel
        if not path.exists():
            errors.append(f"Missing required file: {path}")
        elif not path.is_file():
            errors.append(f"Expected file but found something else: {path}")

    commands_dir = target / ".agentcodex" / "commands"
    for name in REQUIRED_COMMANDS:
        path = commands_dir / name
        if not path.exists():
            errors.append(f"Missing required command procedure: {path}")
            continue
        text = path.read_text(encoding="utf-8")
        for section in COMMAND_REQUIRED_SECTIONS:
            if section not in text:
                errors.append(f"Command procedure missing section '{section}' in {path}")
    for extra in collect_extra_files(commands_dir, set(REQUIRED_COMMANDS), "*.md"):
        notes.append(f"Extra command procedure present: {extra}")

    templates_dir = target / ".agentcodex" / "templates"
    for name in REQUIRED_TEMPLATES:
        path = templates_dir / name
        if not path.exists():
            errors.append(f"Missing required template: {path}")
            continue
        text = path.read_text(encoding="utf-8")
        for marker in TEMPLATE_REQUIRED_MARKERS.get(name, []):
            if marker not in text:
                errors.append(f"Template missing marker '{marker}' in {path}")
    for extra in collect_extra_files(templates_dir, set(REQUIRED_TEMPLATES), "*.md"):
        notes.append(f"Extra template present: {extra}")

    bootstrap_note = target / ".agentcodex" / "PROJECT_AGENTSCODEX.md"
    if bootstrap_note.exists():
        require_text_marker(errors, bootstrap_note, ".agentcodex/commands/")
        require_text_marker(errors, bootstrap_note, "Recommended starting set:")

    agents_md = target / "AGENTS.md"
    if agents_md.exists():
        require_text_marker(errors, agents_md, ".agentcodex/commands/")
        require_text_marker(errors, agents_md, ".agentcodex/routing/routing.json")
        require_text_marker(errors, agents_md, "AgentCodex Project Standard")

    routing_path = target / ".agentcodex" / "routing" / "routing.json"
    if routing_path.exists():
        try:
            routing = json.loads(routing_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"Invalid routing JSON in {routing_path}: {exc}")
        else:
            for key in REQUIRED_ROUTING_KEYS:
                if key not in routing:
                    errors.append(f"Routing manifest missing key '{key}' in {routing_path}")

    kb_index = target / ".agentcodex" / "kb" / "index.yaml"
    if kb_index.exists():
        project_domains = parse_simple_yaml_domains(kb_index)
        for domain in KB_MANAGED_DOMAINS:
            if domain not in project_domains:
                errors.append(f"KB index missing expected domain '{domain}' in {kb_index}")
        for domain in KB_MANAGED_DOMAINS:
            domain_dir = target / ".agentcodex" / "kb" / KB_DOMAIN_PATHS[domain]
            if not domain_dir.exists():
                errors.append(f"Missing required KB domain directory: {domain_dir}")
    kb_dir = target / ".agentcodex" / "kb"
    allowed_top_level = {
        path.split("/", 1)[0]
        for path in KB_DOMAIN_PATHS.values()
    } | {"README.md", "index.yaml", "INDEX.md"}
    for extra in collect_extra_dirs(kb_dir, allowed_top_level):
        notes.append(f"Extra KB top-level directory present: {extra}")

    project_standard = load_project_standard_manifest()
    features_root = target / ".agentcodex" / "features"
    project_standard_root = features_root / project_standard["feature_scaffold_root"]
    validate_project_standard_feature(project_standard_root, project_standard, errors, notes, strict=False)
    for feature_dir in sorted(features_root.iterdir() if features_root.exists() else []):
        if not feature_dir.is_dir():
            continue
        if feature_dir.name == project_standard["feature_scaffold_root"]:
            continue
        if (feature_dir / "CHECKLIST.md").exists():
            validate_project_standard_feature(feature_dir, project_standard, errors, notes, strict=True)

    feature_names = collect_feature_names(target / ".agentcodex" / "features")
    feature_names.update(collect_feature_names(target / ".agentcodex" / "reports"))
    history_features = collect_history_features(target / ".agentcodex" / "history")
    for feature in sorted(feature_names):
        if feature not in history_features:
            errors.append(
                f"Missing context history for in-progress feature '{feature}' in "
                f"{target / '.agentcodex' / 'history'}"
            )

    if errors:
        print("Bootstrapped project check failed:\n")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Bootstrapped project check passed.")
    print(f"Validated target: {target}")
    if notes:
        print("Notes:")
        for note in notes:
            print(f"- {note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
