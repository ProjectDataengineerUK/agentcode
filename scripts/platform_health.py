#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
REPORTS_ROOT = ROOT / ".agentcodex" / "reports" / "platform-health"


def print_usage() -> int:
    print("Usage: python3 scripts/agentcodex.py platform-health <databricks|fabric> [--json]")
    return 1


def write_report(platform: str, payload: dict) -> Path:
    REPORTS_ROOT.mkdir(parents=True, exist_ok=True)
    path = REPORTS_ROOT / f"{platform}-health.md"
    lines = [
        f"# {platform.title()} Health Report",
        "",
        f"- generated_at: {payload['generated_at']}",
        f"- platform: {platform}",
        f"- status: {payload['status']}",
        "",
        "## Summary",
        "",
    ]
    for key in ["message", "host", "workspace_count", "warehouse_count", "catalog_count", "principal"]:
        value = payload.get(key)
        if value not in [None, ""]:
            lines.append(f"- {key}: {value}")
    if payload.get("checks"):
        lines.extend(["", "## Checks", ""])
        for check in payload["checks"]:
            lines.append(f"- {check}")
    if payload.get("errors"):
        lines.extend(["", "## Errors", ""])
        for error in payload["errors"]:
            lines.append(f"- {error}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def databricks_health() -> dict:
    payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "status": "unavailable",
        "checks": [],
        "errors": [],
        "host": os.environ.get("DATABRICKS_HOST", ""),
    }
    try:
        from databricks.sdk import WorkspaceClient
        from databricks.sdk.errors import DatabricksError
    except ImportError:
        payload["message"] = "databricks-sdk not installed"
        payload["errors"].append("Install dependency: pip install databricks-sdk")
        return payload

    try:
        client = WorkspaceClient()
        me = client.current_user.me()
        payload["principal"] = getattr(me, "user_name", "") or getattr(me, "display_name", "")
        payload["checks"].append("authentication ok")
        payload["host"] = getattr(client.config, "host", payload["host"])

        warehouses = list(client.warehouses.list())
        payload["warehouse_count"] = len(warehouses)
        payload["checks"].append("warehouses list ok")

        try:
            catalogs = list(client.catalogs.list())
            payload["catalog_count"] = len(catalogs)
            payload["checks"].append("unity catalog list ok")
        except Exception as exc:  # noqa: BLE001
            payload["errors"].append(f"catalog list failed: {exc}")

        payload["status"] = "ok"
        payload["message"] = "Databricks credentials and workspace APIs responded"
        return payload
    except DatabricksError as exc:
        payload["message"] = "Databricks communication failed"
        payload["errors"].append(str(exc))
        return payload
    except Exception as exc:  # noqa: BLE001
        payload["message"] = "Unexpected Databricks health error"
        payload["errors"].append(str(exc))
        return payload


def fabric_health() -> dict:
    payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "status": "unavailable",
        "checks": [],
        "errors": [],
    }
    try:
        from azure.identity import DefaultAzureCredential
        from azure.core.exceptions import ClientAuthenticationError
    except ImportError:
        payload["message"] = "azure-identity not installed"
        payload["errors"].append("Install dependency: pip install azure-identity")
        return payload

    try:
        credential = DefaultAzureCredential(exclude_interactive_browser_credential=True)
        token = credential.get_token("https://api.fabric.microsoft.com/.default")
        payload["checks"].append("entra id token ok")

        request = urllib.request.Request(
            "https://api.fabric.microsoft.com/v1/workspaces",
            headers={
                "Authorization": f"Bearer {token.token}",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(request, timeout=10) as response:
            body = json.loads(response.read().decode("utf-8"))
        workspaces = body.get("value", [])
        payload["workspace_count"] = len(workspaces)
        payload["checks"].append("fabric workspaces api ok")
        payload["status"] = "ok"
        payload["message"] = "Fabric credentials and API connectivity validated"
        return payload
    except ClientAuthenticationError as exc:
        payload["message"] = "Fabric authentication failed"
        payload["errors"].append(str(exc))
        return payload
    except urllib.error.HTTPError as exc:
        payload["message"] = "Fabric API request failed"
        payload["errors"].append(f"{exc.code} {exc.reason}")
        return payload
    except Exception as exc:  # noqa: BLE001
        payload["message"] = "Unexpected Fabric health error"
        payload["errors"].append(str(exc))
        return payload


def main() -> int:
    args = sys.argv[1:]
    if not args or len(args) > 2:
        return print_usage()

    platform = args[0].strip().lower()
    as_json = len(args) == 2 and args[1] == "--json"
    if len(args) == 2 and not as_json:
        return print_usage()

    if platform == "databricks":
        payload = databricks_health()
    elif platform == "fabric":
        payload = fabric_health()
    else:
        return print_usage()

    report_path = write_report(platform, payload)
    payload["report_path"] = str(report_path.relative_to(ROOT))

    if as_json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"# {platform.title()} Health")
        print()
        print(f"- status: {payload['status']}")
        print(f"- message: {payload.get('message', '')}")
        print(f"- report_path: {payload['report_path']}")
        for key in ["host", "workspace_count", "warehouse_count", "catalog_count", "principal"]:
            value = payload.get(key)
            if value not in [None, ""]:
                print(f"- {key}: {value}")
        if payload["errors"]:
            print("- errors:")
            for error in payload["errors"]:
                print(f"  - {error}")
    return 0 if payload["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
