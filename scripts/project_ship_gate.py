#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

import check_bootstrapped_project as checker
import control_plane_check as control_plane
import project_readiness_report as readiness


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/project_ship_gate.py <target-project-dir>")
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
    blocking: list[dict] = []
    for block in project_standard["blocks"]:
        status, evidences, issues = readiness.block_status(root, block)
        item = {
            "block_id": block["id"],
            "phase": block["phase"],
            "role": block["role"],
            "required": block.get("required", True),
            "status": status,
            "evidences": evidences,
            "issues": issues,
        }
        block_reports.append(item)
        if block.get("required", True) and status in {"missing", "partial"}:
            blocking.append(item)

    report_path = readiness.write_report(target, project_standard, block_reports)
    control_checks = {
        "multi-agent": control_plane.run_multi_agent(root, {block["id"]: block for block in project_standard["blocks"]}),
        "token": control_plane.run_token(root),
        "cost": control_plane.run_cost(root, {block["id"]: block for block in project_standard["blocks"]}),
        "security": control_plane.run_security(root, {block["id"]: block for block in project_standard["blocks"]}),
    }
    control_failed = [name for name, item in control_checks.items() if item["status"] == "fail"]
    if blocking:
        print("Project ship gate failed.")
        print(f"Readiness report: {report_path}")
        print("Blocking blocks:")
        for item in blocking:
            print(f"- {item['block_id']}: {item['status']}")
        return 1
    if control_failed:
        print("Project ship gate failed.")
        print(f"Readiness report: {report_path}")
        print("Blocking control-plane checks:")
        for name in control_failed:
            print(f"- {name}: fail")
        return 1

    print("Project ship gate passed.")
    print(f"Readiness report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
