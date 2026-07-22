#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import control_plane_check as control_plane
import project_readiness_report as readiness


ROOT = Path(__file__).resolve().parent.parent
BASELINE_PATH = ROOT / ".agentcodex" / "maturity" / "maturity5-baseline.json"
PROJECT_STANDARD_PATH = ROOT / ".agentcodex" / "project-standard.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_args(argv: list[str]) -> tuple[Path, str | None, bool] | None:
    args = list(argv)
    as_json = False
    profile: str | None = None
    if "--json" in args:
        as_json = True
        args = [arg for arg in args if arg != "--json"]
    if "--profile" in args:
        idx = args.index("--profile")
        if idx + 1 >= len(args):
            return None
        profile = args[idx + 1]
        del args[idx : idx + 2]
    if len(args) != 1:
        return None
    return Path(args[0]).resolve(), profile, as_json


def score_statuses(statuses: list[str]) -> int:
    score = 100
    for status in statuses:
        if status == "fail":
            score -= 20
        elif status == "warn":
            score -= 8
    return max(score, 0)


def path_status(path: Path, relative_to: Path) -> tuple[str, str]:
    if not path.exists():
        return "fail", f"missing: {path.relative_to(relative_to)}"
    if path.is_file() and path.suffix == ".md":
        if readiness.checker.has_meaningful_content(path):
            return "pass", f"present: {path.relative_to(relative_to)}"
        return "warn", f"placeholder: {path.relative_to(relative_to)}"
    return "pass", f"present: {path.relative_to(relative_to)}"


def evaluate_dimension(
    dimension: dict,
    feature_root: Path,
    target: Path,
    block_lookup: dict[str, dict],
    control_checks: dict[str, dict],
) -> dict:
    evidences: list[str] = []
    issues: list[str] = []
    statuses: list[str] = []

    for block_id in dimension.get("required_blocks", []):
        block = block_lookup.get(block_id)
        if block is None:
            statuses.append("fail")
            issues.append(f"missing project-standard block: {block_id}")
            continue
        status, block_evidences, block_issues = readiness.block_status(feature_root, block)
        normalized = "pass" if status in {"complete", "not_applicable"} else ("warn" if status == "partial" else "fail")
        statuses.append(normalized)
        evidences.append(f"block {block_id}: {status}")
        evidences.extend(f"  {item}" for item in block_evidences[:4])
        issues.extend(f"{block_id}: {item}" for item in block_issues)

    for block_id in dimension.get("conditional_blocks", []):
        block = block_lookup.get(block_id)
        if block is None:
            continue
        status, _, block_issues = readiness.block_status(feature_root, block)
        evidences.append(f"conditional block {block_id}: {status}")
        if status == "partial":
            statuses.append("warn")
            issues.extend(f"{block_id}: {item}" for item in block_issues)
        elif status == "missing":
            statuses.append("fail")
            issues.append(f"{block_id}: conditional surface exists in baseline but artifacts are missing")

    for check_name in dimension.get("required_control_checks", []):
        result = control_checks.get(check_name)
        if result is None:
            statuses.append("fail")
            issues.append(f"missing control-plane check: {check_name}")
            continue
        status = result["status"]
        evidences.append(f"control {check_name}: {status} ({result['score']})")
        if status == "pass":
            statuses.append("pass")
        elif status == "warn":
            statuses.append("warn")
            issues.extend(f"{check_name}: {item}" for item in result["issues"][:5])
        else:
            statuses.append("fail")
            issues.extend(f"{check_name}: {item}" for item in result["issues"][:5])

    for rel in dimension.get("required_feature_paths", []):
        status, evidence = path_status(feature_root / rel, feature_root)
        statuses.append(status)
        evidences.append(f"feature path {evidence}")

    for rel in dimension.get("required_repo_paths", []):
        status, evidence = path_status(target / rel, target)
        statuses.append(status)
        evidences.append(f"repo path {evidence}")

    if "fail" in statuses:
        status = "fail"
    elif "warn" in statuses:
        status = "warn"
    else:
        status = "pass"

    return {
        "dimension": dimension["id"],
        "status": status,
        "score": score_statuses(statuses),
        "evidences": evidences,
        "issues": issues,
    }


def write_report(
    target: Path,
    baseline: dict,
    profile: dict,
    dimensions: list[dict],
    overall_status: str,
    average_score: float,
) -> Path:
    reports_dir = target / ".agentcodex" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_path = reports_dir / "maturity5-readiness-report.md"
    lines = [
        "# Maturity 5 Readiness Report",
        "",
        f"- generated_at: {datetime.now(UTC).isoformat()}",
        f"- target: {target}",
        f"- baseline: {baseline['name']}",
        f"- baseline_version: {baseline['version']}",
        f"- profile: {profile['id']}",
        f"- profile_name: {profile['name']}",
        f"- status: {overall_status}",
        f"- average_score: {average_score}",
        "",
    ]
    for item in dimensions:
        lines.extend(
            [
                f"## {item['dimension']}",
                "",
                f"- status: {item['status']}",
                f"- score: {item['score']}",
                "",
                "### Evidence",
                "",
            ]
        )
        if item["evidences"]:
            for evidence in item["evidences"]:
                lines.append(f"- {evidence}")
        else:
            lines.append("- none")
        lines.extend(["", "### Issues", ""])
        if item["issues"]:
            for issue in item["issues"]:
                lines.append(f"- {issue}")
        else:
            lines.append("- none")
        lines.append("")
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def main() -> int:
    parsed = parse_args(sys.argv[1:])
    if parsed is None:
        print(
            "Usage: python3 scripts/agentcodex.py maturity5-check <target-project-dir> "
            "[--profile <data-platform|agentic-llm|regulated-enterprise>] [--json]"
        )
        return 1
    target, requested_profile, as_json = parsed

    if not target.exists():
        print(f"Target does not exist: {target}")
        return 1

    baseline = load_json(BASELINE_PATH)
    project_standard = load_json(PROJECT_STANDARD_PATH)
    feature_root = target / ".agentcodex" / "features" / baseline["scaffold_root"]
    if not feature_root.exists():
        print(f"Missing project standard scaffold root: {feature_root}")
        return 1
    profiles = {profile["id"]: profile for profile in baseline.get("profiles", [])}
    active_profile_id = requested_profile or baseline.get("default_profile")
    if active_profile_id not in profiles:
        print(f"Unknown maturity profile: {active_profile_id}")
        print(f"Available profiles: {', '.join(sorted(profiles))}")
        return 1
    active_profile = profiles[active_profile_id]

    blocks = control_plane.block_lookup(project_standard)
    control_checks = {
        "multi-agent": control_plane.run_multi_agent(feature_root, blocks),
        "token": control_plane.run_token(feature_root),
        "cost": control_plane.run_cost(feature_root, blocks),
        "security": control_plane.run_security(feature_root, blocks),
    }
    dimensions = [
        evaluate_dimension(dimension, feature_root, target, blocks, control_checks)
        for dimension in active_profile["dimensions"]
    ]
    failed = [item["dimension"] for item in dimensions if item["status"] == "fail"]
    warned = [item["dimension"] for item in dimensions if item["status"] == "warn"]
    overall_status = "fail" if failed else ("warn" if warned else "pass")
    average_score = round(sum(item["score"] for item in dimensions) / len(dimensions), 2) if dimensions else 0.0
    report_path = write_report(target, baseline, active_profile, dimensions, overall_status, average_score)
    result = {
        "target": str(target),
        "baseline": baseline["name"],
        "baseline_version": baseline["version"],
        "profile": active_profile["id"],
        "profile_name": active_profile["name"],
        "status": overall_status,
        "average_score": average_score,
        "report_path": str(report_path),
        "dimensions": dimensions,
        "failed_dimensions": failed,
        "warned_dimensions": warned,
    }
    if as_json:
        print(json.dumps(result, indent=2))
    else:
        print("# Maturity 5 Check")
        print()
        print(f"- target: {target}")
        print(f"- profile: {active_profile['id']}")
        print(f"- status: {overall_status}")
        print(f"- average_score: {average_score}")
        print(f"- report_path: {report_path}")
        for item in dimensions:
            print(f"- {item['dimension']}: {item['status']} ({item['score']})")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
