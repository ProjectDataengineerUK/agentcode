#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterable
import subprocess
import sys


ROOT = Path.cwd()
REPORTS_ROOT = ROOT / ".agentcodex" / "reports"
FEATURES_ROOT = ROOT / ".agentcodex" / "features"
CONTEXT_PATH = ROOT / "context.md"
IGNORED_DIRS = {
    ".git",
    ".agentcodex",
    ".codex",
    "dist",
    "build",
    "node_modules",
    "__pycache__",
    ".venv",
    ".venv-packaging",
    ".venv-start",
    "venv",
}
BASE_MARKERS = {
    "README.md",
    "AGENTS.md",
    "pyproject.toml",
    "package.json",
    "go.mod",
    "Cargo.toml",
    "pom.xml",
    "Makefile",
    "requirements.txt",
    "docker-compose.yml",
}
AGENTCODEX_LIGHT_INSTALL_BASE_FILES = {"AGENTS.md"}
MARKDOWN_SUFFIX = ".md"
PDF_SUFFIX = ".pdf"
VIDEO_SUFFIXES = {".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v"}
TEXT_SIDEcars = {".txt", ".md", ".srt", ".vtt"}
PDF_MULTIMODAL_NOTE = (
    "PDFs must be reviewed as multimodal evidence: extract text, then render pages "
    "for visual inspection/OCR when diagrams, screenshots, architecture drawings, "
    "tables, or low text yield are present."
)


@dataclass(frozen=True)
class ProjectEvidence:
    all_files: list[str]
    base_files: list[str]
    markdown_files: list[str]
    pdf_files: list[str]
    video_files: list[str]
    top_level_entries: list[str]


@dataclass(frozen=True)
class MaturityCheck:
    label: str
    required_paths: tuple[str, ...]
    note: str


def now_iso() -> str:
    return datetime.now(UTC).isoformat()


def slugify(value: str) -> str:
    cleaned = "".join(ch if ch.isalnum() else "_" for ch in value.strip().lower())
    cleaned = "_".join(part for part in cleaned.split("_") if part)
    return cleaned or "start"


def prompt_yes_no(question: str, default: bool = False) -> bool:
    suffix = "[Y/n]" if default else "[y/N]"
    while True:
        answer = input(f"{question} {suffix} ").strip().lower()
        if not answer:
            return default
        if answer in {"y", "yes", "sim", "s"}:
            return True
        if answer in {"n", "no", "nao", "não"}:
            return False
        print("Enter yes or no.")


def prompt_choice(question: str, options: list[tuple[str, str]]) -> tuple[str, str]:
    print(question)
    for key, label in options:
        print(f"{key}. {label}")
    while True:
        answer = input("Choose one option: ").strip().lower()
        for key, label in options:
            if answer == key:
                return key, label
        print("Invalid choice.")


def prompt_nonempty(label: str) -> str:
    while True:
        value = input(f"{label}: ").strip()
        if value:
            return value
        print("This field is required.")


def ensure_dirs() -> None:
    REPORTS_ROOT.mkdir(parents=True, exist_ok=True)
    FEATURES_ROOT.mkdir(parents=True, exist_ok=True)


def collect_top_level_entries(root: Path) -> list[str]:
    items: list[str] = []
    for entry in sorted(root.iterdir()):
        if entry.name in IGNORED_DIRS:
            continue
        if entry.is_file() and is_generated_start_context(entry):
            continue
        if entry.is_dir():
            items.append(f"{entry.name}/")
        else:
            items.append(entry.name)
    return items


def first_non_empty_line(path: Path, limit: int = 240) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line and not line.startswith("#"):
            return line[:limit]
    return ""


def sidecar_text(path: Path) -> str | None:
    for suffix in TEXT_SIDEcars:
        candidate = path.with_suffix(suffix)
        if candidate.exists() and candidate.is_file():
            try:
                text = candidate.read_text(encoding="utf-8", errors="replace").strip()
            except OSError:
                continue
            if text:
                return text[:800]
    return None


def is_generated_start_context(path: Path) -> bool:
    if path.name != "context.md" or not path.is_file():
        return False
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    return text.startswith("# Context\n") and "- generated_at:" in text and "## Directory Scan" in text


def pdf_text(path: Path, limit: int = 1600) -> str | None:
    try:
        result = subprocess.run(
            ["pdftotext", "-layout", str(path), "-"],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    text = "\n".join(line.strip() for line in result.stdout.splitlines() if line.strip())
    return text[:limit] if text else None


def document_text(path: Path, limit: int = 1600) -> str | None:
    transcript = sidecar_text(path)
    if transcript:
        return transcript[:limit]
    if path.suffix.lower() == PDF_SUFFIX:
        return pdf_text(path, limit=limit)
    return None


def collect_project_evidence(root: Path) -> ProjectEvidence:
    all_files: list[str] = []
    base_files: list[str] = []
    markdown_files: list[str] = []
    pdf_files: list[str] = []
    video_files: list[str] = []

    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        if is_generated_start_context(path):
            continue
        rel = str(path.relative_to(root))
        all_files.append(rel)
        if path.name in BASE_MARKERS or path.suffix.lower() in {".toml", ".yaml", ".yml"} and path.name in {"pyproject.toml", "package.json"}:
            base_files.append(rel)
        if path.suffix.lower() == MARKDOWN_SUFFIX:
            markdown_files.append(rel)
        elif path.suffix.lower() == PDF_SUFFIX:
            pdf_files.append(rel)
        elif path.suffix.lower() in VIDEO_SUFFIXES:
            video_files.append(rel)

    return ProjectEvidence(
        all_files=sorted(all_files),
        base_files=sorted(base_files),
        markdown_files=sorted(markdown_files),
        pdf_files=sorted(pdf_files),
        video_files=sorted(video_files),
        top_level_entries=collect_top_level_entries(root),
    )


def has_base_project(evidence: ProjectEvidence) -> bool:
    project_owned_base_files = [
        path for path in evidence.base_files if path not in AGENTCODEX_LIGHT_INSTALL_BASE_FILES
    ]
    return bool(project_owned_base_files)


def build_base_project_report(evidence: ProjectEvidence, answers: dict[str, str]) -> str:
    lines = [
        "# Start Report",
        "",
        f"- generated_at: `{now_iso()}`",
        f"- root: `{ROOT}`",
        f"- selected_option: `{answers['selected_option']}`",
        f"- delivered_report: `{answers['delivered_report']}`",
        "",
        "## Scan",
        "",
        f"- total files detected: {len(evidence.all_files)}",
        f"- base files detected: {len(evidence.base_files)}",
        f"- markdown files detected: {len(evidence.markdown_files)}",
        f"- pdf files detected: {len(evidence.pdf_files)}",
        f"- video files detected: {len(evidence.video_files)}",
        "",
        "## Selected Reports",
        "",
        f"- detailed project report: {answers.get('detailed_report', 'no')}",
        f"- maturity report: {answers.get('maturity_report', 'no')}",
        f"- vulnerability report: {answers.get('vulnerability_report', 'no')}",
        f"- improvement report: {answers.get('improvement_report', 'no')}",
        "",
        "## Base Files",
        "",
    ]
    lines.extend(f"- `{item}`" for item in evidence.base_files or ["[none]"])
    lines.extend(
        [
            "",
            "## Next Action",
            "",
            "- Review the selected outputs and continue with the most relevant report or workflow phase.",
        ]
    )
    return "\n".join(lines) + "\n"


def limited_items(items: list[str], limit: int = 80) -> list[str]:
    if len(items) <= limit:
        return items
    return items[:limit] + [f"... {len(items) - limit} more"]


def build_detailed_project_report(evidence: ProjectEvidence) -> str:
    lines = [
        "# Detailed Project Report",
        "",
        f"- generated_at: `{now_iso()}`",
        f"- root: `{ROOT}`",
        "",
        "## Inventory",
        "",
        f"- total files detected: {len(evidence.all_files)}",
        f"- top-level entries detected: {len(evidence.top_level_entries)}",
        f"- base files detected: {len(evidence.base_files)}",
        f"- markdown files detected: {len(evidence.markdown_files)}",
        f"- pdf files detected: {len(evidence.pdf_files)}",
        f"- video files detected: {len(evidence.video_files)}",
        "",
        "## Top-Level Entries",
        "",
    ]
    lines.extend(f"- `{item}`" for item in evidence.top_level_entries or ["[none]"])
    lines.extend(["", "## Base Files", ""])
    lines.extend(f"- `{item}`" for item in evidence.base_files or ["[none]"])
    lines.extend(["", "## Markdown Evidence", ""])
    for rel_path in limited_items(evidence.markdown_files):
        if rel_path.startswith("... "):
            lines.append(f"- {rel_path}")
            continue
        excerpt = first_non_empty_line(ROOT / rel_path) or "[empty or unreadable]"
        lines.append(f"- `{rel_path}`")
        lines.append(f"  - excerpt: {excerpt}")
    lines.extend(
        [
            "",
            "## Recommended Next Step",
            "",
            "- Use `agentcodex project-intake` for a new/refactor definition, or run `/ship` only after real build evidence exists.",
        ]
    )
    return "\n".join(lines) + "\n"


MATURITY_TRACKS: dict[str, dict[str, object]] = {
    "DATAOPS": {
        "title": "DataOps",
        "baseline": "data-platform",
        "description": "Pipeline, data quality, lineage, contracts, deployment, and governed operations.",
        "checks": (
            MaturityCheck(
                "project-standard scaffold",
                (".agentcodex/features/example-project-standard/CHECKLIST.md",),
                "Feature work is anchored to the AgentCodex Project Standard.",
            ),
            MaturityCheck(
                "pipeline orchestration",
                (
                    ".agentcodex/features/example-project-standard/execution/orchestration.md",
                    ".agentcodex/features/example-project-standard/execution/pipelines/README.md",
                    ".agentcodex/features/example-project-standard/execution/schedules.md",
                ),
                "Pipeline execution, ownership, and schedules are explicit.",
            ),
            MaturityCheck(
                "data quality gates",
                (
                    ".agentcodex/features/example-project-standard/validation/data-quality.md",
                    ".agentcodex/features/example-project-standard/validation/rules.md",
                    ".agentcodex/features/example-project-standard/validation/tests/README.md",
                ),
                "Data quality checks can block release.",
            ),
            MaturityCheck(
                "lineage and contracts",
                (
                    ".agentcodex/features/example-project-standard/metadata/lineage.md",
                    ".agentcodex/features/example-project-standard/contracts/schema-contracts/README.md",
                    ".agentcodex/features/example-project-standard/contracts/compatibility.md",
                ),
                "Lineage and schema/data contract expectations are visible.",
            ),
            MaturityCheck(
                "deployment and rollback",
                (
                    ".agentcodex/features/example-project-standard/deploy/ci-cd.md",
                    ".agentcodex/features/example-project-standard/deploy/environments.md",
                ),
                "Promotion, environment, and rollback paths are documented.",
            ),
        ),
    },
    "MLOPS": {
        "title": "MLOps",
        "baseline": "start-mlops-track",
        "description": "Model lifecycle, validation, deployment, monitoring, governance, and cost controls.",
        "checks": (
            MaturityCheck(
                "model registry and experiment tracking",
                (
                    ".agentcodex/ops/mlops/model-registry.md",
                    ".agentcodex/ops/mlops/experiments.md",
                ),
                "Model versions, training runs, metrics, and approval history are traceable.",
            ),
            MaturityCheck(
                "model validation gates",
                (
                    ".agentcodex/features/example-project-standard/validation/rules.md",
                    ".agentcodex/features/example-project-standard/validation/tests/README.md",
                ),
                "Model validation has explicit checks before release.",
            ),
            MaturityCheck(
                "model deployment and rollback",
                (
                    ".agentcodex/features/example-project-standard/deploy/ci-cd.md",
                    ".agentcodex/features/example-project-standard/deploy/environments.md",
                ),
                "Model promotion and rollback are treated as release operations.",
            ),
            MaturityCheck(
                "model monitoring",
                (
                    ".agentcodex/features/example-project-standard/operations/observability/metrics.md",
                    ".agentcodex/features/example-project-standard/operations/observability/alerts.md",
                ),
                "Runtime quality, drift, and incident signals have monitoring surfaces.",
            ),
            MaturityCheck(
                "model governance and access",
                (
                    ".agentcodex/features/example-project-standard/controls/governance.md",
                    ".agentcodex/features/example-project-standard/security/access-control.md",
                    ".agentcodex/features/example-project-standard/operations/cost/cost-model.md",
                ),
                "Ownership, access, and cost controls are part of the model operating surface.",
            ),
        ),
    },
    "LLMOPS": {
        "title": "LLMOps",
        "baseline": "agentic-llm",
        "description": "LLM model policy, prompt/eval governance, token control, supervision, and quarantine.",
        "checks": (
            MaturityCheck(
                "LLM model policy",
                (".agentcodex/ops/agentic-llm/model-policy.md",),
                "Allowed models, routing, token budgets, and governance are explicit.",
            ),
            MaturityCheck(
                "prompt and eval governance",
                (
                    ".agentcodex/ops/agentic-llm/prompt-registry.md",
                    ".agentcodex/ops/agentic-llm/evals.md",
                    ".agentcodex/ops/agentic-llm/guardrails.md",
                ),
                "Prompts, evals, and guardrails are versioned and auditable.",
            ),
            MaturityCheck(
                "token and cost controls",
                (
                    ".agentcodex/model-routing.json",
                    ".agentcodex/features/example-project-standard/operations/cost/optimization.md",
                ),
                "Model routing and optimization evidence exist before autonomous expansion.",
            ),
            MaturityCheck(
                "supervision and quarantine",
                (
                    ".agentcodex/features/example-project-standard/operations/sentinel/supervision.md",
                    ".agentcodex/features/example-project-standard/operations/sentinel/quarantine.md",
                ),
                "Human approval, blocked actions, and quarantine paths are documented.",
            ),
            MaturityCheck(
                "API contracts and access",
                (
                    ".agentcodex/features/example-project-standard/contracts/api-contracts/README.md",
                    ".agentcodex/features/example-project-standard/security/access-control.md",
                ),
                "LLM-facing APIs and access boundaries are governed.",
            ),
        ),
    },
}


def score_maturity_check(check: MaturityCheck) -> tuple[str, int, list[str], list[str]]:
    present: list[str] = []
    missing: list[str] = []
    for rel_path in check.required_paths:
        path = ROOT / rel_path
        if path.exists():
            present.append(rel_path)
        else:
            missing.append(rel_path)

    total = len(check.required_paths)
    score = round((len(present) / total) * 100) if total else 0
    if not missing:
        status = "pass"
    elif present:
        status = "warn"
    else:
        status = "fail"
    return status, score, present, missing


def maturity_status(score: float) -> str:
    if score >= 85:
        return "pass"
    if score >= 55:
        return "warn"
    return "fail"


def build_maturity_track_report(track_id: str, track: dict[str, object]) -> dict[str, object]:
    checks = track["checks"]
    assert isinstance(checks, tuple)
    check_reports: list[dict[str, object]] = []
    for check in checks:
        assert isinstance(check, MaturityCheck)
        status, score, present, missing = score_maturity_check(check)
        check_reports.append(
            {
                "label": check.label,
                "status": status,
                "score": score,
                "present": present,
                "missing": missing,
                "note": check.note,
            }
        )
    track_score = round(sum(item["score"] for item in check_reports) / len(check_reports), 1) if check_reports else 0.0
    return {
        "id": track_id,
        "title": track["title"],
        "baseline": track["baseline"],
        "description": track["description"],
        "status": maturity_status(track_score),
        "score": track_score,
        "checks": check_reports,
    }


def build_maturity_report(evidence: ProjectEvidence) -> str:
    track_reports = [build_maturity_track_report(track_id, track) for track_id, track in MATURITY_TRACKS.items()]
    overall_score = round(sum(float(track["score"]) for track in track_reports) / len(track_reports), 1)
    overall_status = maturity_status(overall_score)
    lines = [
        "# DataOps MLOps LLMOps Maturity Report",
        "",
        f"- generated_at: `{now_iso()}`",
        f"- root: `{ROOT}`",
        f"- maturity_model: `DataOps + MLOps + LLMOps`",
        f"- status: `{overall_status}`",
        f"- maturity_score: {overall_score}",
        "",
        "## Track Summary",
        "",
    ]
    for track in track_reports:
        lines.append(
            f"- {track['id']}: {track['status']} ({track['score']}) "
            f"- baseline: `{track['baseline']}`"
        )
    lines.extend(["", "## Tracks", ""])
    for track in track_reports:
        lines.extend(
            [
                f"### {track['title']}",
                "",
                f"- id: `{track['id']}`",
                f"- status: `{track['status']}`",
                f"- score: {track['score']}",
                f"- baseline: `{track['baseline']}`",
                f"- scope: {track['description']}",
                "",
                "#### Checks",
                "",
            ]
        )
        for check in track["checks"]:
            assert isinstance(check, dict)
            lines.extend(
                [
                    f"- {check['label']}: {check['status']} ({check['score']})",
                    f"  - note: {check['note']}",
                ]
            )
            present = check["present"]
            missing = check["missing"]
            assert isinstance(present, list)
            assert isinstance(missing, list)
            if present:
                lines.append(f"  - present: {', '.join(f'`{item}`' for item in present)}")
            if missing:
                lines.append(f"  - missing: {', '.join(f'`{item}`' for item in missing)}")
        lines.append("")

    lines.extend(["## Interpretation", ""])
    if overall_status == "pass":
        lines.append("- The repository has strong DataOps, MLOps, and LLMOps operating evidence.")
    elif overall_status == "warn":
        lines.append("- The repository has usable operating structure but should close the weaker maturity tracks before ship.")
    else:
        lines.append("- The repository needs explicit DataOps, MLOps, and LLMOps operating artifacts before ship.")
    lines.extend(
        [
            "- Use `agentcodex maturity5-check <target-project-dir> --profile data-platform` for the executable DataOps gate.",
            "- Use `agentcodex maturity5-check <target-project-dir> --profile agentic-llm` for the executable LLMOps gate.",
            "- MLOps is reported here as a start-time operating track until a dedicated executable profile is added.",
        ]
    )
    return "\n".join(lines) + "\n"


def build_vulnerability_report(evidence: ProjectEvidence) -> str:
    risky_names = {"env", ".env", "id_rsa", "credentials", "secret", "token", "password"}
    findings: list[str] = []
    for rel_path in evidence.all_files:
        lowered = rel_path.lower()
        if any(name in lowered for name in risky_names):
            findings.append(rel_path)
    lines = [
        "# Vulnerability Report",
        "",
        f"- generated_at: `{now_iso()}`",
        f"- root: `{ROOT}`",
        "- scope: filename and repository-structure scan only",
        "",
        "## Findings",
        "",
    ]
    if findings:
        lines.extend(f"- review potentially sensitive path: `{item}`" for item in limited_items(sorted(findings), 80))
    else:
        lines.append("- no obviously sensitive filenames detected in the scanned file inventory")
    lines.extend(
        [
            "",
            "## Required Follow-up",
            "",
            "- Run a deeper code/path-handling security review before treating this as a full vulnerability assessment.",
        ]
    )
    return "\n".join(lines) + "\n"


def build_improvement_report(evidence: ProjectEvidence) -> str:
    recommendations = [
        "Keep command behavior documented in both `docs/commands/` and `.agentcodex/commands/` when the runtime surface changes.",
        "Keep generated reports under `.agentcodex/reports/` so later sessions can resume from files.",
        "Run `python3 scripts/validate_agentcodex.py` after workflow, role, routing, or command-surface changes.",
    ]
    if not any(path.startswith(".agentcodex/tests/") for path in evidence.all_files):
        recommendations.append("Add AgentCodex regression tests for the updated workflow behavior.")
    lines = [
        "# Project Improvement Report",
        "",
        f"- generated_at: `{now_iso()}`",
        f"- root: `{ROOT}`",
        "",
        "## Recommendations",
        "",
    ]
    lines.extend(f"- {item}" for item in recommendations)
    return "\n".join(lines) + "\n"


REPORT_OPTIONS = [
    ("1", "Detailed project report", "start-detailed-project-report.md", "detailed_report", build_detailed_project_report),
    ("2", "DataOps / MLOps / LLMOps maturity", "start-maturity-report.md", "maturity_report", build_maturity_report),
    ("3", "Vulnerability report", "start-vulnerability-report.md", "vulnerability_report", build_vulnerability_report),
    ("4", "Project improvement report", "start-improvement-report.md", "improvement_report", build_improvement_report),
    ("5", "All reports", "", "all_reports", None),
]


def deliver_selected_reports(evidence: ProjectEvidence, selected_key: str) -> tuple[dict[str, str], list[Path]]:
    answers = {
        "selected_option": selected_key,
        "detailed_report": "no",
        "maturity_report": "no",
        "vulnerability_report": "no",
        "improvement_report": "no",
        "delivered_report": "",
    }
    selected_options = REPORT_OPTIONS[:-1] if selected_key == "5" else [option for option in REPORT_OPTIONS if option[0] == selected_key]
    written: list[Path] = []
    for _, label, filename, answer_key, builder in selected_options:
        if builder is None:
            continue
        path = REPORTS_ROOT / filename
        write_text(path, builder(evidence))
        answers[answer_key] = "yes"
        written.append(path)
        print(f"Created {label.lower()}: {path.relative_to(ROOT)}")
    answers["delivered_report"] = ", ".join(str(path.relative_to(ROOT)) for path in written)
    return answers, written


def build_context_markdown(evidence: ProjectEvidence) -> str:
    lines = [
        "# Context",
        "",
        f"- generated_at: `{now_iso()}`",
        f"- root: `{ROOT}`",
        "",
        "## Directory Scan",
        "",
        f"- top_level_entries: {', '.join(evidence.top_level_entries) if evidence.top_level_entries else '[none]'}",
        f"- base_files: {len(evidence.base_files)}",
        f"- markdown_files: {len(evidence.markdown_files)}",
        f"- pdf_files: {len(evidence.pdf_files)}",
        f"- video_files: {len(evidence.video_files)}",
        "",
        "## Markdown Evidence",
        "",
    ]
    if evidence.markdown_files:
        for rel_path in evidence.markdown_files:
            path = ROOT / rel_path
            excerpt = first_non_empty_line(path)
            if not excerpt:
                excerpt = "[empty or unreadable]"
            lines.append(f"- `{rel_path}`")
            lines.append(f"  - excerpt: {excerpt}")
    else:
        lines.append("- [none]")

    lines.extend(["", "## PDF Evidence", ""])
    if evidence.pdf_files:
        lines.append(f"- multimodal review rule: {PDF_MULTIMODAL_NOTE}")
        for rel_path in evidence.pdf_files:
            path = ROOT / rel_path
            transcript = document_text(path)
            lines.append(f"- `{rel_path}`")
            if transcript:
                lines.append(f"  - extracted text: {transcript}")
            else:
                lines.append("  - extracted text: unavailable in this environment")
            lines.append("  - visual inspection: render pages and inspect images, diagrams, tables, and architecture flows before treating the PDF as complete")
    else:
        lines.append("- [none]")

    lines.extend(["", "## Video Evidence", ""])
    if evidence.video_files:
        for rel_path in evidence.video_files:
            path = ROOT / rel_path
            transcript = sidecar_text(path)
            lines.append(f"- `{rel_path}`")
            if transcript:
                lines.append(f"  - transcript: {transcript}")
            else:
                lines.append("  - transcript: unavailable in this environment")
    else:
        lines.append("- [none]")

    lines.extend(
        [
            "",
            "## Brainstorm Prompt",
            "",
            "You are the AgentCodex workflow-brainstormer.",
            "Use the context in this file to start a structured brainstorm in English.",
            "Ask one question at a time, prefer multiple-choice prompts when possible, and keep the first phase focused on problem framing, users, constraints, samples, and candidate approaches.",
        ]
    )
    return "\n".join(lines) + "\n"


def build_evidence_brief(evidence: ProjectEvidence, limit: int = 4) -> list[str]:
    lines: list[str] = []
    if evidence.markdown_files:
        lines.append("Markdown evidence:")
        for rel_path in evidence.markdown_files[:limit]:
            excerpt = first_non_empty_line(ROOT / rel_path) or "[empty or unreadable]"
            lines.append(f"- `{rel_path}`: {excerpt}")
    if evidence.pdf_files:
        lines.append("PDF evidence:")
        lines.append(f"- Review rule: {PDF_MULTIMODAL_NOTE}")
        for rel_path in evidence.pdf_files[:limit]:
            transcript = document_text(ROOT / rel_path, limit=900)
            if transcript:
                lines.append(f"- `{rel_path}`: {transcript}")
            else:
                lines.append(f"- `{rel_path}`: detected, but text extraction was unavailable")
            lines.append("  - visual follow-up: inspect rendered pages for images, diagrams, tables, screenshots, and architecture flows")
    if evidence.video_files:
        lines.append("Video evidence:")
        for rel_path in evidence.video_files[:limit]:
            transcript = sidecar_text(ROOT / rel_path)
            if transcript:
                lines.append(f"- `{rel_path}`: {transcript}")
            else:
                lines.append(f"- `{rel_path}`: detected, but transcript was unavailable")
    if not lines:
        lines.append("- No project evidence found beyond the AgentCodex bootstrap files.")
    return lines


def build_brainstorm_prompt(evidence: ProjectEvidence) -> str:
    lines = [
        "# Start Brainstorm Prompt",
        "",
        "You are the AgentCodex workflow-brainstormer.",
        "",
        "## Current Context",
        "",
        f"- repository_root: `{ROOT}`",
        f"- detected_base_files: {len(evidence.base_files)}",
        f"- detected_markdown_files: {len(evidence.markdown_files)}",
        f"- detected_pdf_files: {len(evidence.pdf_files)}",
        f"- detected_video_files: {len(evidence.video_files)}",
        "- source_of_truth: `context.md`",
        "",
        "## Evidence Brief",
        "",
    ]
    lines.extend(build_evidence_brief(evidence))
    lines.extend(
        [
            "",
            "## Sequential Brainstorm Flow",
            "",
            "Follow this sequence. Ask one question at a time and wait for the operator answer before moving to the next question.",
            "",
            "1. Grounding: confirm the project objective from the detected files, especially PDFs or requirement notes.",
            "2. Outcome: ask what final deliverable the project must produce.",
            "3. Users: ask who will use or approve the result.",
            "4. Data and platforms: ask which sources, targets, Databricks workspaces, cloud accounts, and tools are in scope.",
            "5. Constraints: ask about security, compliance, deadlines, budget, access, and operational restrictions.",
            "6. Candidate approaches: propose 2 or 3 possible solution paths and ask the operator to choose one.",
            "7. YAGNI: identify what should stay out of scope for the first version.",
            "8. Validation: ask how success will be tested, monitored, and accepted.",
            "9. Define handoff: summarize answers into suggested requirements for the `define` phase.",
            "",
            "## First Message To Operator",
            "",
            "Start now with only Question 1. Use the available evidence to avoid a blank generic question.",
            "If PDF text was extracted, summarize it briefly before asking Question 1.",
            "Do not treat extracted PDF text as complete until pages with images, diagrams, tables, screenshots, or architecture drawings were rendered and inspected.",
            "If PDF text was not extracted, say which file was detected and ask the operator to provide or confirm its main objective.",
            "Prefer A/B/C options when there are clear alternatives.",
            "",
            "## Artifact Update",
            "",
            "Update `.agentcodex/features/BRAINSTORM_{PROJECT}.md` after the operator answers enough discovery questions.",
            "Do not proceed to `define` until the brainstorm has a selected approach, YAGNI cuts, and validation checkpoints.",
            "",
            "Read context.md before asking anything else.",
            "Continue the brainstorm flow sequentially.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> int:
    if not (ROOT / ".agentcodex").exists():
        print("AgentCodex is not installed in this directory. Install it before running start.", file=sys.stderr)
        return 1

    ensure_dirs()
    evidence = collect_project_evidence(ROOT)

    if has_base_project(evidence):
        selected_key, _ = prompt_choice(
            "What do you want AgentCodex to deliver now?",
            [(key, label) for key, label, *_ in REPORT_OPTIONS],
        )
        answers, _ = deliver_selected_reports(evidence, selected_key)
        report_path = REPORTS_ROOT / "start-report.md"
        write_text(report_path, build_base_project_report(evidence, answers))
        print(f"Created start report: {report_path.relative_to(ROOT)}")
        return 0

    context_path = CONTEXT_PATH
    write_text(context_path, build_context_markdown(evidence))
    print(f"Created context file: {context_path.relative_to(ROOT)}")

    prompt_path = REPORTS_ROOT / "start-brainstorm-prompt.md"
    write_text(prompt_path, build_brainstorm_prompt(evidence))
    print(f"Created brainstorm prompt: {prompt_path.relative_to(ROOT)}")

    feature_slug = slugify(ROOT.name)
    brainstorm_path = FEATURES_ROOT / f"BRAINSTORM_{feature_slug}.md"
    write_text(
        brainstorm_path,
        "\n".join(
            [
                f"# BRAINSTORM_{feature_slug.upper()}",
                "",
                "## Metadata",
                "",
                f"- feature: `{feature_slug}`",
                "- phase: `brainstorm`",
                "- status: `draft`",
                "- owner: `operator`",
                f"- updated_at: `{now_iso()}`",
                "",
                "## Prompt",
                "",
                "Use `context.md` as the source of truth and follow the brainstorm prompt stored in `.agentcodex/reports/start-brainstorm-prompt.md`.",
                "",
                "## Exit Check",
                "",
                "- [x] context.md created",
                "- [x] brainstorm prompt created",
                "- [x] next step ready for workflow-brainstormer",
            ]
        )
        + "\n",
    )
    print(f"Created brainstorm artifact: {brainstorm_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
