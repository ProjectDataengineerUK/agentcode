#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

from new_context_history import resolve_project_root, slugify


PHASE_ORDER = ["brainstorm", "define", "design", "build", "ship"]
FEATURE_PHASE_PREFIX = {
    "brainstorm": "BRAINSTORM",
    "define": "DEFINE",
    "design": "DESIGN",
}
REPORT_PHASE_PREFIX = {
    "build": "BUILD_REPORT",
    "ship": "SHIPPED",
}


def print_usage() -> int:
    print("Usage: python3 scripts/agentcodex.py sync-context <feature> [--owner <owner>]")
    return 1


def extract_section(text: str, heading: str) -> str:
    pattern = rf"## {re.escape(heading)}\n(.*?)(?:\n## |\Z)"
    match = re.search(pattern, text, re.DOTALL)
    if not match:
        return ""
    return match.group(1).strip()


def collect_bullets(section_body: str) -> list[str]:
    values: list[str] = []
    for raw_line in section_body.splitlines():
        line = raw_line.strip()
        if line.startswith("- "):
            value = line[2:].strip()
            if value:
                values.append(value)
    return values


def read_text(path: Path | None) -> str:
    if path is None or not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def find_feature_artifact(project_root: Path, feature: str, phase: str) -> Path | None:
    prefix = FEATURE_PHASE_PREFIX.get(phase)
    if prefix is None:
        return None
    path = project_root / ".agentcodex" / "features" / f"{prefix}_{feature}.md"
    return path if path.exists() else None


def find_report_artifact(project_root: Path, feature: str, phase: str) -> Path | None:
    prefix = REPORT_PHASE_PREFIX.get(phase)
    if prefix is None:
        return None
    path = project_root / ".agentcodex" / "reports" / f"{prefix}_{feature}.md"
    return path if path.exists() else None


def determine_current_phase(project_root: Path, feature: str) -> str:
    current = "brainstorm"
    for phase in PHASE_ORDER:
        feature_path = find_feature_artifact(project_root, feature, phase)
        report_path = find_report_artifact(project_root, feature, phase)
        if feature_path or report_path:
            current = phase
    return current


def build_history_content(
    feature: str,
    owner: str,
    today: str,
    current_phase: str,
    paths: list[Path],
    define_text: str,
    design_text: str,
    build_text: str,
    filename: str,
) -> str:
    problem_statement = extract_section(define_text, "Problem Statement")
    architecture = extract_section(design_text, "Architecture Overview")
    open_questions = collect_bullets(extract_section(define_text, "Open Questions"))
    open_decisions = collect_bullets(extract_section(design_text, "Open Decisions"))
    residual_risks = collect_bullets(extract_section(build_text, "Residual Risks"))
    files_changed = collect_bullets(extract_section(build_text, "Files Changed"))
    verification_commands = extract_section(build_text, "Verification Commands")

    current_state_lines = [f"- implementation state: current artifact phase is `{current_phase}`"]
    if architecture:
        current_state_lines.append(f"- current phase summary: {architecture}")
    elif problem_statement:
        current_state_lines.append(f"- current phase summary: {problem_statement}")
    if paths:
        current_state_lines.append(
            "- known stable artifacts: " + ", ".join(f"`{path.as_posix()}`" for path in paths)
        )

    decisions_lines: list[str] = []
    if architecture:
        decisions_lines.append(f"- decision: {architecture}")
    for item in open_decisions[:2]:
        decisions_lines.append(f"- rationale: unresolved design decision remains: {item}")
    if not decisions_lines:
        decisions_lines = ["- decision: no explicit design decision has been synchronized yet"]

    changed_artifacts_lines = [f"- path: `{path.as_posix()}`" for path in paths]
    for item in files_changed[:5]:
        changed_artifacts_lines.append(f"- path: `{item}`")
    if verification_commands:
        changed_artifacts_lines.append("- command: see verification commands captured in build artifacts")
    if not changed_artifacts_lines:
        changed_artifacts_lines = ["- path: no project-local workflow artifacts found yet"]

    open_gap_lines: list[str] = []
    for item in open_questions[:3]:
        open_gap_lines.append(f"- gap: {item}")
    for item in open_decisions[:3]:
        open_gap_lines.append(f"- blocker: {item}")
    for item in residual_risks[:3]:
        open_gap_lines.append(f"- assumption: {item}")
    if not open_gap_lines:
        open_gap_lines = ["- gap: no explicit unresolved gaps were found in synchronized artifacts"]

    next_phase = "build"
    next_owner = "workflow-builder"
    next_action = "implement the manifest defined in design and record verification in a build report"
    if current_phase == "brainstorm":
        next_phase = "define"
        next_owner = "workflow-definer"
        next_action = "convert the recommended direction into explicit goals and acceptance criteria"
    elif current_phase == "define":
        next_phase = "design"
        next_owner = "workflow-designer"
        next_action = "turn accepted requirements into a file manifest and explicit test strategy"
    elif current_phase == "design":
        next_phase = "build"
        next_owner = "workflow-builder"
        next_action = "implement the design manifest and capture verification results"
    elif current_phase == "build":
        next_phase = "ship"
        next_owner = "workflow-shipper"
        next_action = "review acceptance, residual risks, and publish a shipped artifact when ready"
    elif current_phase == "ship":
        next_phase = "iterate"
        next_owner = "workflow-iterator"
        next_action = "capture follow-up work and reconcile new drift against shipped scope"

    return "\n".join(
        [
            f"# CONTEXT_{feature}",
            "",
            "## Metadata",
            "",
            f"- scope: `{feature}`",
            "- kind: `feature`",
            f"- owner: `{owner}`",
            f"- updated_at: `{today}`",
            "",
            "## Scope",
            "",
            f"Synchronized context for feature `{feature}` based on current AgentCodex workflow artifacts.",
            "",
            "## Current State",
            "",
            *current_state_lines,
            "",
            "## Decisions",
            "",
            *decisions_lines,
            "",
            "## Changed Artifacts",
            "",
            *changed_artifacts_lines,
            "",
            "## Open Gaps",
            "",
            *open_gap_lines,
            "",
            "## Next Recommended Step",
            "",
            f"- next owner: {next_owner}",
            f"- next phase: {next_phase}",
            f"- next concrete action: {next_action}",
            "",
            "## Resume Prompt",
            "",
            f"Continue from `.agentcodex/history/{filename}` and reconcile it with the latest project artifacts.",
            "",
        ]
    )


def main() -> int:
    args = sys.argv[1:]
    if not args:
        return print_usage()

    owner = "agentcodex"
    scope_parts: list[str] = []
    i = 0
    while i < len(args):
        arg = args[i]
        if not arg.startswith("--"):
            scope_parts.append(arg)
            i += 1
            continue
        if arg == "--owner":
            if i + 1 >= len(args):
                return print_usage()
            owner = args[i + 1].strip()
            i += 2
            continue
        return print_usage()

    raw_scope = " ".join(scope_parts).strip()
    if not raw_scope:
        return print_usage()

    feature = slugify(raw_scope)
    project_root = resolve_project_root()
    history_dir = project_root / ".agentcodex" / "history"
    history_dir.mkdir(parents=True, exist_ok=True)

    today = date.today().isoformat()
    filename = f"CONTEXT_{feature}_{today}.md"
    destination = history_dir / filename

    paths: list[Path] = []
    define_path = find_feature_artifact(project_root, feature, "define")
    design_path = find_feature_artifact(project_root, feature, "design")
    brainstorm_path = find_feature_artifact(project_root, feature, "brainstorm")
    build_path = find_report_artifact(project_root, feature, "build")
    ship_path = find_report_artifact(project_root, feature, "ship")
    for path in [brainstorm_path, define_path, design_path, build_path, ship_path]:
        if path is not None:
            paths.append(path.relative_to(project_root))

    if not paths:
        print(f"No workflow artifacts found for feature '{feature}'.", file=sys.stderr)
        return 1

    current_phase = determine_current_phase(project_root, feature)
    content = build_history_content(
        feature=feature,
        owner=owner,
        today=today,
        current_phase=current_phase,
        paths=paths,
        define_text=read_text(define_path),
        design_text=read_text(design_path),
        build_text=read_text(build_path),
        filename=filename,
    )
    destination.write_text(content, encoding="utf-8")
    print(f"Synchronized context history: {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
