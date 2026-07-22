#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import check_bootstrapped_project as checker


def artifact_status(root: Path, artifact: str | dict) -> tuple[str, Path, list[str]]:
    rel, required_markers = checker.normalize_project_standard_artifact(artifact)
    path = root / rel
    issues: list[str] = []
    if not path.exists():
        return "missing", path, issues
    if path.is_file() and path.suffix == ".md":
        text = path.read_text(encoding="utf-8")
        if checker.has_explicit_not_applicable(text):
            return "not_applicable", path, issues
        if not checker.has_meaningful_content(path):
            issues.append("placeholder")
        for marker in required_markers:
            if marker not in text:
                issues.append(f"missing marker: {marker}")
    return ("partial" if issues else "complete"), path, issues


def block_status(root: Path, block: dict) -> tuple[str, list[str], list[str]]:
    issues: list[str] = []
    evidences: list[str] = []
    statuses: list[str] = []
    for artifact in block.get("artifacts", []):
        status, path, artifact_issues = artifact_status(root, artifact)
        statuses.append(status)
        evidences.append(f"{status}: {path}")
        for issue in artifact_issues:
            issues.append(f"{path}: {issue}")
    if not block.get("required", True):
        if any(status == "complete" for status in statuses):
            return "complete", evidences, issues
        if any(status == "partial" for status in statuses):
            return "partial", evidences, issues
        return "not_applicable", evidences, issues
    if any(status == "missing" for status in statuses):
        return "missing", evidences, issues
    if any(status == "partial" for status in statuses):
        return "partial", evidences, issues
    if all(status == "not_applicable" for status in statuses):
        return "not_applicable", evidences, issues
    return "complete", evidences, issues


def write_report(target: Path, project_standard: dict, block_reports: list[dict]) -> Path:
    reports_dir = target / ".agentcodex" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_path = reports_dir / "project-readiness-report.md"
    total = len(block_reports)
    complete = sum(1 for item in block_reports if item["status"] == "complete")
    partial = sum(1 for item in block_reports if item["status"] == "partial")
    missing = sum(1 for item in block_reports if item["status"] == "missing")
    not_applicable = sum(1 for item in block_reports if item["status"] == "not_applicable")
    readiness = round((complete / total) * 100, 2) if total else 0.0

    lines = [
        "# Project Readiness Report",
        "",
        f"- generated_at: {datetime.now(UTC).isoformat()}",
        f"- target: {target}",
        f"- standard_version: {project_standard['version']}",
        f"- scaffold_root: {project_standard['feature_scaffold_root']}",
        f"- readiness_score: {readiness}",
        f"- complete_blocks: {complete}",
        f"- partial_blocks: {partial}",
        f"- missing_blocks: {missing}",
        f"- not_applicable_blocks: {not_applicable}",
        "",
    ]

    for item in block_reports:
        lines.extend(
            [
                f"## {item['block_id']}",
                "",
                f"- phase: {item['phase']}",
                f"- role: {item['role']}",
                f"- required: {str(item['required']).lower()}",
                f"- status: {item['status']}",
                "",
                "### Evidence",
                "",
            ]
        )
        for evidence in item["evidences"]:
            lines.append(f"- {evidence}")
        if item["issues"]:
            lines.extend(["", "### Issues", ""])
            for issue in item["issues"]:
                lines.append(f"- {issue}")
        lines.append("")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/project_readiness_report.py <target-project-dir>")
        return 1

    target = Path(sys.argv[1]).resolve()
    if not target.exists():
        print(f"Target does not exist: {target}")
        return 1

    project_standard = checker.load_project_standard_manifest()
    root = target / ".agentcodex" / "features" / project_standard["feature_scaffold_root"]
    if not root.exists():
        print(f"Missing project standard scaffold root: {root}")
        return 1

    block_reports: list[dict] = []
    for block in project_standard["blocks"]:
        status, evidences, issues = block_status(root, block)
        block_reports.append(
            {
                "block_id": block["id"],
                "phase": block["phase"],
                "role": block["role"],
                "required": block.get("required", True),
                "status": status,
                "evidences": evidences,
                "issues": issues,
            }
        )

    report_path = write_report(target, project_standard, block_reports)
    print(f"Wrote readiness report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
