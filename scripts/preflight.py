#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

import databricks_readiness
from state_utils import ensure_agentcodex_dirs, load_project_state, now_iso, resolve_root, save_project_state


KNOWN_STACKS = ("databricks", "terraform", "github-actions", "python", "node")


def print_usage() -> int:
    print("Usage: python3 scripts/agentcodex.py preflight [target-project-dir] [--stack <id>] [--json]")
    return 1


def parse_args(argv: list[str]) -> tuple[Path, str | None, bool] | None:
    target_arg: str | None = None
    stack: str | None = None
    as_json = False
    index = 0
    while index < len(argv):
        current = argv[index]
        if current == "--json":
            as_json = True
            index += 1
            continue
        if current == "--stack" and index + 1 < len(argv):
            stack = argv[index + 1].strip().casefold()
            index += 2
            continue
        if current.startswith("--"):
            return None
        if target_arg is None:
            target_arg = current
            index += 1
            continue
        return None
    return resolve_root(target_arg), stack, as_json


def detect_stacks(root: Path) -> list[str]:
    stacks: set[str] = set()
    if any(root.glob("*.tf")) or (root / "terraform").exists():
        stacks.add("terraform")
    if (root / ".github" / "workflows").exists():
        stacks.add("github-actions")
    if (root / "pyproject.toml").exists() or (root / "requirements.txt").exists():
        stacks.add("python")
    if (root / "package.json").exists():
        stacks.add("node")
    databricks_markers = [
        root / "databricks.yml",
        root / "bundle.yml",
        root / "app.yaml",
        root / "resources" / "app.yaml",
    ]
    if any(marker.exists() for marker in databricks_markers):
        stacks.add("databricks")
    return sorted(stacks)


def result(name: str, status: str, detail: str) -> dict[str, str]:
    return {"check": name, "status": status, "detail": detail}


def check_databricks(root: Path) -> list[dict[str, str]]:
    checks = databricks_readiness.environment_checks(root)
    readiness = databricks_readiness.build_payload(root)
    for section_name in ["bundles", "apps", "governance", "jobs", "boundary"]:
        section = readiness["sections"][section_name]
        checks.append(
            result(
                f"databricks-{section_name}",
                section["status"],
                f"see databricks-readiness section {section_name}",
            )
        )
    return checks


def check_terraform(_: Path) -> list[dict[str, str]]:
    return [
        result(
            "terraform-cli",
            "pass" if shutil.which("terraform") else "warn",
            "terraform found in PATH" if shutil.which("terraform") else "terraform not found in PATH",
        )
    ]


def check_github_actions(root: Path) -> list[dict[str, str]]:
    workflows = sorted((root / ".github" / "workflows").glob("*.y*ml")) if (root / ".github" / "workflows").exists() else []
    return [
        result(
            "workflows-present",
            "pass" if workflows else "warn",
            f"{len(workflows)} workflow files found" if workflows else "no workflow files found",
        )
    ]


def check_python(root: Path) -> list[dict[str, str]]:
    return [
        result(
            "python-project",
            "pass" if (root / "pyproject.toml").exists() or (root / "requirements.txt").exists() else "warn",
            "python project markers found" if (root / "pyproject.toml").exists() or (root / "requirements.txt").exists() else "python markers missing",
        )
    ]


def check_node(root: Path) -> list[dict[str, str]]:
    return [
        result(
            "package-json",
            "pass" if (root / "package.json").exists() else "warn",
            "package.json found" if (root / "package.json").exists() else "package.json missing",
        )
    ]


def run_checks(root: Path, stack: str) -> list[dict[str, str]]:
    if stack == "databricks":
        return check_databricks(root)
    if stack == "terraform":
        return check_terraform(root)
    if stack == "github-actions":
        return check_github_actions(root)
    if stack == "python":
        return check_python(root)
    if stack == "node":
        return check_node(root)
    return [result("unsupported", "warn", f"unsupported stack: {stack}")]


def aggregate_status(checks: list[dict[str, str]]) -> str:
    statuses = {item["status"] for item in checks}
    if "fail" in statuses:
        return "fail"
    if "warn" in statuses:
        return "warn"
    return "pass"


def write_report(root: Path, payload: dict[str, object]) -> Path:
    path = root / ".agentcodex" / "reports" / "preflight-report.md"
    lines = [
        "# Preflight Report",
        "",
        f"- generated_at: {payload['generated_at']}",
        f"- target_root: {payload['target_root']}",
        "",
    ]
    for stack, summary in payload["stacks"].items():
        lines.extend([f"## {stack}", "", f"- status: {summary['status']}", ""])
        for item in summary["checks"]:
            lines.append(f"- {item['check']}: {item['status']} - {item['detail']}")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> int:
    parsed = parse_args(sys.argv[1:])
    if parsed is None:
        return print_usage()
    root, requested_stack, as_json = parsed
    if not root.exists():
        print(f"Target does not exist: {root}", file=sys.stderr)
        return 1

    ensure_agentcodex_dirs(root)
    stacks = [requested_stack] if requested_stack else detect_stacks(root)
    if requested_stack and requested_stack not in KNOWN_STACKS:
        print(f"Unsupported stack: {requested_stack}", file=sys.stderr)
        return 1

    payload = {"generated_at": now_iso(), "target_root": str(root), "stacks": {}}
    for stack in stacks:
        checks = run_checks(root, stack)
        payload["stacks"][stack] = {
            "status": aggregate_status(checks),
            "checks": checks,
        }

    report_path = write_report(root, payload)
    state = load_project_state(root)
    state["preflight"] = {
        "stacks": payload["stacks"],
        "last_report": str(report_path.relative_to(root)),
    }
    state_path = save_project_state(root, state)
    payload["report_path"] = str(report_path.relative_to(root))
    payload["state_path"] = str(state_path.relative_to(root))

    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("# Preflight")
        print()
        for stack, summary in payload["stacks"].items():
            print(f"- {stack}: {summary['status']}")
        print(f"- report_path: {payload['report_path']}")
        print(f"- state_path: {payload['state_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
