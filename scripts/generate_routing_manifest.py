#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ROLES_PATH = ROOT / ".agentcodex" / "roles" / "roles.yaml"
ROUTING_SOURCE_PATH = ROOT / ".agentcodex" / "routing" / "routing-source.json"
ROUTING_OUTPUT_PATH = ROOT / ".agentcodex" / "routing" / "routing.json"


def parse_roles_yaml(path: Path) -> dict[str, dict]:
    roles: dict[str, dict] = {}
    current: dict | None = None
    current_id: str | None = None
    current_list_key: str | None = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("version:") or stripped == "roles:":
            continue
        if stripped.startswith("- id:"):
            current_id = stripped.split(":", 1)[1].strip()
            current = {"id": current_id, "escalates_to": []}
            roles[current_id] = current
            current_list_key = None
            continue
        if current is None:
            continue
        if stripped.endswith(":") and stripped[:-1] in {"kb_domains", "owns", "escalates_to"}:
            current_list_key = stripped[:-1]
            current[current_list_key] = []
            continue
        if stripped.startswith("- ") and current_list_key:
            current[current_list_key].append(stripped[2:].strip())
            continue
        if ":" in stripped:
            key, value = stripped.split(":", 1)
            normalized_key = key.strip()
            normalized_value = value.strip()
            if normalized_key in {"kb_domains", "owns", "escalates_to"} and normalized_value == "[]":
                current[normalized_key] = []
            else:
                current[normalized_key] = normalized_value
            current_list_key = None

    return roles


def main() -> int:
    source = json.loads(ROUTING_SOURCE_PATH.read_text(encoding="utf-8"))
    roles = parse_roles_yaml(ROLES_PATH)

    escalations: list[dict[str, str]] = []
    for role_id, role in sorted(roles.items()):
        for target in role.get("escalates_to", []):
            escalations.append({
                "from": role_id,
                "to": target,
                "condition": "see role documentation"
            })

    output = {
        "version": source.get("version", "0.1.0"),
        "workflow_phase_routing": source.get("workflow_phase_routing", []),
        "data_engineering_routing": source.get("data_engineering_routing", []),
        "domain_routing": source.get("domain_routing", []),
        "platform_routing": source.get("platform_routing", []),
        "control_routing": source.get("control_routing", []),
        "file_pattern_hints": source.get("file_pattern_hints", []),
        "escalations": escalations
    }

    ROUTING_OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote routing manifest: {ROUTING_OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
