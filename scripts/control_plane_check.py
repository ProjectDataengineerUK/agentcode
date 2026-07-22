#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import check_bootstrapped_project as checker
import project_readiness_report as readiness


ROOT = Path(__file__).resolve().parent.parent

ALIASES = {
    "multi-agent-readiness": "multi-agent",
    "token-budget-check": "token",
    "cost-risk-check": "cost",
    "security-compliance-check": "security",
    "control-plane-check": "all",
}


def usage() -> int:
    print(
        "Usage: python3 scripts/agentcodex.py control-plane-check <target-project-dir> "
        "[all|multi-agent|token|cost|security] [--json]"
    )
    return 1


def artifact_status(feature_root: Path, artifact: str | dict) -> tuple[str, list[str]]:
    status, _, issues = readiness.artifact_status(feature_root, artifact)
    return status, issues


def block_lookup(project_standard: dict) -> dict[str, dict]:
    return {block["id"]: block for block in project_standard["blocks"]}


def classify_issues(issues: list[str]) -> dict[str, int]:
    counts = {"missing": 0, "placeholder": 0, "markers": 0, "other": 0}
    for issue in issues:
        text = issue.casefold()
        if "missing" in text:
            counts["missing"] += 1
        elif "placeholder" in text:
            counts["placeholder"] += 1
        elif "marker" in text:
            counts["markers"] += 1
        else:
            counts["other"] += 1
    return counts


def score_from_issues(issues: list[str]) -> int:
    score = 100
    for issue in issues:
        text = issue.casefold()
        if "missing" in text:
            score -= 12
        elif "placeholder" in text:
            score -= 8
        elif "marker" in text:
            score -= 5
        else:
            score -= 4
    return max(score, 0)


def finalize_check(name: str, issues: list[str], evidences: list[str]) -> dict:
    score = score_from_issues(issues)
    issue_counts = classify_issues(issues)
    if issue_counts["missing"] > 0:
        status = "fail"
    elif issues:
        status = "warn"
    else:
        status = "pass"
    return {
        "check": name,
        "status": status,
        "score": score,
        "issue_counts": issue_counts,
        "issues": issues,
        "evidences": evidences,
    }


def run_multi_agent(feature_root: Path, blocks: dict[str, dict]) -> dict:
    issues: list[str] = []
    evidences: list[str] = []
    agents_block = blocks.get("agentes definidos (se houver)")
    sentinel_block = blocks.get("monitoramento sentinela")

    for label, block in [("agents", agents_block), ("sentinel", sentinel_block)]:
        if block is None:
            issues.append(f"missing project-standard block: {label}")
            continue
        status, evidences_block, issues_block = readiness.block_status(feature_root, block)
        evidences.extend(evidences_block)
        issues.extend(issues_block)
        if label == "sentinel" and status in {"missing", "partial"}:
            issues.append("sentinel layer is not ready for supervised multi-agent operation")

    routing_path = feature_root / "agents" / "routing.md"
    if routing_path.exists():
        evidences.append(f"present: {routing_path}")
    else:
        issues.append(f"missing: {routing_path}")

    return finalize_check("multi-agent", issues, evidences)


def run_token(feature_root: Path) -> dict:
    issues: list[str] = []
    evidences: list[str] = []
    targets = [
        feature_root / "operations/cost/optimization.md",
        feature_root / "operations/observability/logs.md",
        feature_root / "operations/sentinel/knowledge-feed.md",
    ]
    for path in targets:
        if path.exists():
            evidences.append(f"present: {path}")
        else:
            issues.append(f"missing: {path}")
    text_checks = [
        (
            feature_root / "operations/cost/optimization.md",
            ["alert thresholds", "tradeoffs", "model routing policy", "automatic selection evidence"],
        ),
        (feature_root / "operations/observability/logs.md", ["knowledge extraction path", "memory candidate flow"]),
    ]
    model_policy = feature_root / "operations/agentic-llm/model-policy.md"
    if model_policy.exists():
        evidences.append(f"present: {model_policy}")
        text_checks.append((model_policy, ["Allowed Models", "Activity Routing", "Token Budget", "Governance"]))
    for path, markers in text_checks:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                issues.append(f"missing marker '{marker}' in {path}")
    return finalize_check("token", issues, evidences)


def run_cost(feature_root: Path, blocks: dict[str, dict]) -> dict:
    issues: list[str] = []
    evidences: list[str] = []
    cost_block = blocks.get("custo")
    if cost_block is None:
        issues.append("missing project-standard block: custo")
    else:
        status, evidences_block, issues_block = readiness.block_status(feature_root, cost_block)
        evidences.extend(evidences_block)
        issues.extend(issues_block)
        if status in {"missing", "partial"}:
            issues.append("cost model or optimization controls are incomplete")
    return finalize_check("cost", issues, evidences)


def run_security(feature_root: Path, blocks: dict[str, dict]) -> dict:
    issues: list[str] = []
    evidences: list[str] = []
    for block_id in ["governanca", "access control", "compliance", "monitoramento sentinela"]:
        block = blocks.get(block_id)
        if block is None:
            issues.append(f"missing project-standard block: {block_id}")
            continue
        status, evidences_block, issues_block = readiness.block_status(feature_root, block)
        evidences.extend(evidences_block)
        issues.extend(issues_block)
        if block_id in {"access control", "compliance"} and status in {"missing", "partial"}:
            issues.append(f"{block_id} controls are incomplete")

    quarantine_path = feature_root / "operations/sentinel/quarantine.md"
    supervision_path = feature_root / "operations/sentinel/supervision.md"
    for path, markers in [
        (quarantine_path, ["quarantine triggers", "containment actions", "release criteria"]),
        (supervision_path, ["human approval points", "blocked autonomous actions", "operator override"]),
    ]:
        if not path.exists():
            issues.append(f"missing: {path}")
            continue
        evidences.append(f"present: {path}")
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                issues.append(f"missing marker '{marker}' in {path}")
    return finalize_check("security", issues, evidences)


def write_report(target: Path, checks: list[dict]) -> Path:
    reports_dir = target / ".agentcodex" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    path = reports_dir / "control-plane-report.md"
    lines = [
        "# Control Plane Report",
        "",
        f"- generated_at: {datetime.now(UTC).isoformat()}",
        f"- target: {target}",
        "",
    ]
    for item in checks:
        lines.extend(
            [
                f"## {item['check']}",
                "",
                f"- status: {item['status']}",
                f"- score: {item['score']}",
                f"- missing: {item['issue_counts']['missing']}",
                f"- placeholder: {item['issue_counts']['placeholder']}",
                f"- markers: {item['issue_counts']['markers']}",
                f"- other: {item['issue_counts']['other']}",
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
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> int:
    args = sys.argv[1:]
    as_json = False
    if "--json" in args:
        as_json = True
        args = [arg for arg in args if arg != "--json"]
    if len(args) not in {1, 2}:
        return usage()

    target = Path(args[0]).resolve()
    if not target.exists():
        print(f"Target does not exist: {target}")
        return 1

    mode = "all"
    if len(args) == 2:
        mode = ALIASES.get(args[1], args[1])
    if mode not in {"all", "multi-agent", "token", "cost", "security"}:
        return usage()

    project_standard = checker.load_project_standard_manifest()
    feature_root = target / ".agentcodex" / "features" / project_standard["feature_scaffold_root"]
    if not feature_root.exists():
        print(f"Missing project standard scaffold root: {feature_root}")
        return 1

    blocks = block_lookup(project_standard)
    all_checks = {
        "multi-agent": run_multi_agent(feature_root, blocks),
        "token": run_token(feature_root),
        "cost": run_cost(feature_root, blocks),
        "security": run_security(feature_root, blocks),
    }
    checks = list(all_checks.values()) if mode == "all" else [all_checks[mode]]
    report_path = write_report(target, checks)
    failed = [item["check"] for item in checks if item["status"] == "fail"]
    warned = [item["check"] for item in checks if item["status"] == "warn"]
    average_score = round(sum(item["score"] for item in checks) / len(checks), 2) if checks else 0.0
    result = {
        "target": str(target),
        "mode": mode,
        "report_path": str(report_path),
        "checks": checks,
        "failed_checks": failed,
        "warned_checks": warned,
        "average_score": average_score,
        "status": "fail" if failed else ("warn" if warned else "pass"),
    }
    if as_json:
        print(json.dumps(result, indent=2))
    else:
        print("# Control Plane Check")
        print()
        print(f"- target: {target}")
        print(f"- mode: {mode}")
        print(f"- status: {result['status']}")
        print(f"- average_score: {result['average_score']}")
        print(f"- report_path: {report_path}")
        for item in checks:
            print(f"- {item['check']}: {item['status']} ({item['score']})")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
