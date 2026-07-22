#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from state_utils import ensure_agentcodex_dirs, load_project_state, now_iso, resolve_root, save_project_state


LAYER_RULES = {
    "interface_app": [
        ("dash", ["app.py"], "fullstack-engineer", "ui runtime may drift from backend contracts"),
        ("streamlit", ["streamlit_app.py"], "fullstack-engineer", "ui runtime may drift from backend contracts"),
        ("react", ["package.json"], "frontend-engineer", "frontend dependencies and build output need separate verification"),
    ],
    "backend": [
        ("python", ["pyproject.toml", "requirements.txt"], "python-backend-engineer", "service logic and packaging need local and runtime validation"),
        ("fastapi", ["main.py", "app/main.py"], "python-backend-engineer", "API contracts and server startup need runtime validation"),
    ],
    "iac": [
        ("terraform", ["main.tf", "terraform"], "terraform-specialist", "provider auth and remote applies can fail late"),
        ("databricks-bundle", ["databricks.yml", "bundle.yml"], "databricks-architect", "bundle schema and workspace compatibility must be checked before deploy"),
    ],
    "ci_cd": [
        ("github-actions", [".github/workflows"], "ci-cd-specialist", "CI green does not prove deploy or runtime readiness"),
    ],
    "data": [
        ("dbt", ["dbt_project.yml"], "dbt-specialist", "data contract and transformation drift can hide behind successful builds"),
        ("spark", ["spark"], "spark-engineer", "cluster/runtime differences can invalidate local assumptions"),
        ("databricks", ["databricks"], "databricks-architect", "workspace resources and principals can block promotion"),
    ],
    "governance": [
        ("unity-catalog", ["unity", "catalog"], "data-governance-architect", "governance concerns can leak into runtime jobs"),
        ("data-contracts", ["contracts", "schemas"], "data-contracts-engineer", "schema drift needs explicit validation"),
    ],
    "ai_llm": [
        ("genai", ["prompt", "eval", "rag", "mcp"], "genai-architect", "LLM systems need guardrails, evals, and cost controls"),
        ("mosaic-ai", ["mosaic"], "genai-architect", "managed AI features need platform-specific runtime verification"),
    ],
    "observability": [
        ("observability", [".agentcodex/observability", "observability"], "data-observability-engineer", "logs and alerts must be promoted into actionable knowledge"),
    ],
}


def print_usage() -> int:
    print("Usage: python3 scripts/agentcodex.py stack-detect [target-project-dir] [--json]")
    return 1


def has_marker(root: Path, marker: str) -> bool:
    path = root / marker
    if path.exists():
        return True
    lowered = marker.casefold()
    for candidate in root.rglob("*"):
        try:
            rel = str(candidate.relative_to(root)).casefold()
        except ValueError:
            continue
        if lowered in rel:
            return True
    return False


def detect_layers(root: Path) -> dict[str, dict[str, object]]:
    detected: dict[str, dict[str, object]] = {}
    for layer, rules in LAYER_RULES.items():
        components: list[str] = []
        specialists: list[str] = []
        risks: list[str] = []
        for component, markers, specialist, risk in rules:
            if any(has_marker(root, marker) for marker in markers):
                components.append(component)
                specialists.append(specialist)
                risks.append(risk)
        if components:
            detected[layer] = {
                "components": sorted(set(components)),
                "recommended_specialists": sorted(set(specialists)),
                "risks": sorted(set(risks)),
            }
    return detected


def write_report(root: Path, payload: dict[str, object]) -> Path:
    path = root / ".agentcodex" / "reports" / "stack-detect.md"
    lines = [
        "# Stack Detection Report",
        "",
        f"- generated_at: {payload['generated_at']}",
        f"- target_root: {payload['target_root']}",
        f"- detected_layers: {len(payload['layers'])}",
        "",
    ]
    for layer, item in payload["layers"].items():
        lines.extend([f"## {layer}", ""])
        lines.append(f"- components: {', '.join(item['components'])}")
        lines.append(f"- recommended_specialists: {', '.join(item['recommended_specialists'])}")
        lines.append("- risks:")
        for risk in item["risks"]:
            lines.append(f"  - {risk}")
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
    layers = detect_layers(root)
    payload = {"generated_at": now_iso(), "target_root": str(root), "layers": layers}
    report_path = write_report(root, payload)
    state = load_project_state(root)
    state["stack_detection"] = {
        "layers": layers,
        "last_report": str(report_path.relative_to(root)),
    }
    state_path = save_project_state(root, state)
    payload["report_path"] = str(report_path.relative_to(root))
    payload["state_path"] = str(state_path.relative_to(root))
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("# Stack Detect")
        print()
        for layer, item in layers.items():
            print(f"- {layer}: {', '.join(item['components'])}")
        print(f"- report_path: {payload['report_path']}")
        print(f"- state_path: {payload['state_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
