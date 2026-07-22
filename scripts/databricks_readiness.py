#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import shutil
import sys
from pathlib import Path

from state_utils import ensure_agentcodex_dirs, load_project_state, now_iso, resolve_root, save_project_state


BUNDLE_FILES = ("databricks.yml", "bundle.yml")
APP_FILES = ("app.yaml", "resources/app.yaml")
RESOURCE_FILES = ("resources/jobs.yml", "resources/pipelines.yml", "resources/dashboards.yml", "resources/*.yml")


def print_usage() -> int:
    print("Usage: python3 scripts/agentcodex.py databricks-readiness [target-project-dir] [--json]")
    return 1


def find_first(root: Path, candidates: tuple[str, ...]) -> Path | None:
    for candidate in candidates:
        path = root / candidate
        if path.exists():
            return path
    return None


def collect_resource_files(root: Path) -> list[Path]:
    resources_dir = root / "resources"
    if not resources_dir.exists():
        return []
    return sorted(path for path in resources_dir.rglob("*.yml") if path.is_file())


def load_text(path: Path | None) -> str:
    if path is None or not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def check(name: str, status: str, detail: str) -> dict[str, str]:
    return {"check": name, "status": status, "detail": detail}


def aggregate_status(items: list[dict[str, str]]) -> str:
    statuses = {item["status"] for item in items}
    if "fail" in statuses:
        return "fail"
    if "warn" in statuses:
        return "warn"
    return "pass"


def bundle_checks(root: Path) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    bundle_path = find_first(root, BUNDLE_FILES)
    if bundle_path is None:
        return [check("bundle-file", "warn", "databricks.yml or bundle.yml not found")]
    text = load_text(bundle_path)
    items.append(check("bundle-file", "pass", f"{bundle_path.relative_to(root)} found"))
    items.append(
        check(
            "bundle-targets",
            "pass" if "targets:" in text else "warn",
            "bundle targets defined" if "targets:" in text else "bundle targets section missing",
        )
    )
    items.append(
        check(
            "bundle-variables",
            "pass" if "variables:" in text else "warn",
            "bundle variables defined" if "variables:" in text else "bundle variables section missing",
        )
    )
    resource_files = collect_resource_files(root)
    if not resource_files:
        items.append(check("bundle-resources", "warn", "resources/*.yml not found"))
    else:
        items.append(check("bundle-resources", "pass", f"{len(resource_files)} resource files found"))
    wrong_paths: list[str] = []
    for path in resource_files:
        text = load_text(path)
        if "./src/" in text:
            wrong_paths.append(str(path.relative_to(root)))
    items.append(
        check(
            "resource-path-resolution",
            "warn" if wrong_paths else "pass",
            f"resource files using ./src/: {', '.join(wrong_paths)}" if wrong_paths else "resource paths do not show the common ./src/ gotcha",
        )
    )
    return items


def app_checks(root: Path) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    app_path = find_first(root, APP_FILES)
    if app_path is None:
        return [check("app-manifest", "warn", "app.yaml not found")]
    text = load_text(app_path)
    items.append(check("app-manifest", "pass", f"{app_path.relative_to(root)} found"))
    has_port = "PORT" in text or "DATABRICKS_APP_PORT" in text
    items.append(
        check(
            "app-port-env",
            "pass" if has_port else "warn",
            "PORT or DATABRICKS_APP_PORT referenced" if has_port else "app manifest does not reference PORT or DATABRICKS_APP_PORT",
        )
    )
    dev_server_markers = ("flask run", "uvicorn --reload", "app.run(", "streamlit run")
    uses_dev_server = any(marker in text for marker in dev_server_markers)
    items.append(
        check(
            "app-production-server",
            "warn" if uses_dev_server else "pass",
            "manifest hints at a development server" if uses_dev_server else "no obvious development-server marker found in manifest",
        )
    )
    return items


def governance_checks(root: Path) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    sql_files = sorted(root.rglob("*.sql"))
    yaml_files = sorted(root.rglob("*.yml"))
    text_paths = sql_files + yaml_files
    combined = "\n".join(load_text(path) for path in text_paths[:200])
    has_three_level = bool(re.search(r"\b[a-zA-Z0-9_]+\.[a-zA-Z0-9_]+\.[a-zA-Z0-9_]+\b", combined))
    has_use_catalog = "USE CATALOG" in combined.upper() or "use catalog" in combined.casefold()
    has_use_schema = "USE SCHEMA" in combined.upper() or "use schema" in combined.casefold()
    volume_usage = "/Volumes/" in combined
    dbfs_usage = "dbfs:/" in combined.casefold() or "/dbfs/" in combined.casefold()
    items.append(check("uc-three-level-names", "pass" if has_three_level else "warn", "found catalog.schema.object reference" if has_three_level else "no explicit catalog.schema.object reference found"))
    items.append(check("uc-parent-grants", "pass" if has_use_catalog and has_use_schema else "warn", "grant order hints found" if has_use_catalog and has_use_schema else "no clear USE CATALOG and USE SCHEMA grant hints found"))
    items.append(check("uc-volumes-vs-dbfs", "warn" if dbfs_usage and not volume_usage else "pass", "DBFS paths detected without UC Volumes evidence" if dbfs_usage and not volume_usage else "no DBFS-first anti-pattern detected"))
    return items


def jobs_checks(root: Path) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    resource_files = collect_resource_files(root)
    job_text = "\n".join(load_text(path) for path in resource_files)
    if not job_text:
        return [check("jobs-resources", "warn", "no Databricks resource yml files found for jobs review")]
    items.append(check("jobs-timeout", "pass" if "timeout_seconds" in job_text else "warn", "timeout_seconds found" if "timeout_seconds" in job_text else "task timeout_seconds not found"))
    items.append(check("jobs-retries", "pass" if "max_retries" in job_text else "warn", "max_retries found" if "max_retries" in job_text else "max_retries not found"))
    items.append(check("jobs-notifications", "pass" if "webhook_notifications" in job_text or "email_notifications" in job_text else "warn", "job notifications found" if "webhook_notifications" in job_text or "email_notifications" in job_text else "job notifications not found"))
    interactive_cluster = "existing_cluster_id" in job_text
    items.append(check("jobs-interactive-cluster", "warn" if interactive_cluster else "pass", "existing_cluster_id found; verify this is not an interactive-cluster production dependency" if interactive_cluster else "no existing_cluster_id marker found"))
    return items


def environment_checks(_: Path) -> list[dict[str, str]]:
    items = [
        check("databricks-cli", "pass" if shutil.which("databricks") else "warn", "databricks CLI found in PATH" if shutil.which("databricks") else "databricks CLI not found in PATH"),
        check("databricks-host", "pass" if os.environ.get("DATABRICKS_HOST") else "warn", "DATABRICKS_HOST is set" if os.environ.get("DATABRICKS_HOST") else "DATABRICKS_HOST is not set"),
        check("databricks-auth", "pass" if os.environ.get("DATABRICKS_TOKEN") or os.environ.get("DATABRICKS_CLIENT_ID") else "warn", "Databricks token or OAuth client variables found" if os.environ.get("DATABRICKS_TOKEN") or os.environ.get("DATABRICKS_CLIENT_ID") else "Databricks token or OAuth client variables not found"),
    ]
    return items


def boundary_checks(root: Path) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    resource_files = collect_resource_files(root)
    text = "\n".join(load_text(path) for path in resource_files)
    ownership_markers = ("GRANT ", "owner", "permissions:")
    runtime_markers = ("spark_python_task", "notebook_task", "python_wheel_task", "sql_task")
    mixed = any(marker in text for marker in ownership_markers) and any(marker in text for marker in runtime_markers)
    items.append(
        check(
            "governance-runtime-boundary",
            "warn" if mixed else "pass",
            "resource files mix runtime tasks with ownership/grant concerns; verify separation" if mixed else "no obvious governance/runtime mixing detected in resource files",
        )
    )
    principal_marker = "service_principal" in text.casefold() or "run_as" in text.casefold()
    items.append(
        check(
            "runtime-principal-explicit",
            "pass" if principal_marker else "warn",
            "run_as or service principal markers found" if principal_marker else "no explicit runtime principal marker found",
        )
    )
    return items


def build_payload(root: Path) -> dict[str, object]:
    sections = {
        "environment": environment_checks(root),
        "bundles": bundle_checks(root),
        "apps": app_checks(root),
        "governance": governance_checks(root),
        "jobs": jobs_checks(root),
        "boundary": boundary_checks(root),
    }
    return {
        "generated_at": now_iso(),
        "target_root": str(root),
        "sections": {
            name: {"status": aggregate_status(items), "checks": items}
            for name, items in sections.items()
        },
    }


def write_report(root: Path, payload: dict[str, object]) -> Path:
    path = root / ".agentcodex" / "reports" / "databricks-readiness.md"
    lines = [
        "# Databricks Readiness Report",
        "",
        f"- generated_at: {payload['generated_at']}",
        f"- target_root: {payload['target_root']}",
        "",
    ]
    for name, section in payload["sections"].items():
        lines.extend([f"## {name}", "", f"- status: {section['status']}", ""])
        for item in section["checks"]:
            lines.append(f"- {item['check']}: {item['status']} - {item['detail']}")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> int:
    args = sys.argv[1:]
    target_arg: str | None = None
    as_json = False
    for arg in args:
        if arg == "--json":
            as_json = True
        elif target_arg is None:
            target_arg = arg
        else:
            return print_usage()
    root = resolve_root(target_arg)
    if not root.exists():
        print(f"Target does not exist: {root}", file=sys.stderr)
        return 1
    ensure_agentcodex_dirs(root)
    payload = build_payload(root)
    report_path = write_report(root, payload)
    state = load_project_state(root)
    state["databricks_readiness"] = {
        "sections": payload["sections"],
        "last_report": str(report_path.relative_to(root)),
    }
    state_path = save_project_state(root, state)
    payload["report_path"] = str(report_path.relative_to(root))
    payload["state_path"] = str(state_path.relative_to(root))
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("# Databricks Readiness")
        print()
        for name, section in payload["sections"].items():
            print(f"- {name}: {section['status']}")
        print(f"- report_path: {payload['report_path']}")
        print(f"- state_path: {payload['state_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
