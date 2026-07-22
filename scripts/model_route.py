#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import UTC, datetime
import json
from pathlib import Path
import re
import sys
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
POLICY_PATH = ROOT / ".agentcodex" / "model-routing.json"
REPORT_DIR = ROOT / ".agentcodex" / "reports" / "model-routing"
LATEST_JSON = REPORT_DIR / "latest-selection.json"
LATEST_MD = REPORT_DIR / "model-routing.md"
ROLES_PATH = ROOT / ".agentcodex" / "roles" / "roles.yaml"


def load_policy(path: Path = POLICY_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize(value: str | None) -> str:
    return (value or "").strip().lower()


def infer_activity(policy: dict[str, Any], task_text: str, explicit_activity: str | None) -> tuple[str, float, str]:
    if explicit_activity:
        activity = normalize(explicit_activity)
        if activity in policy["activities"]:
            return activity, 0.95, "explicit activity"
        raise ValueError(f"Unknown activity: {explicit_activity}")

    text = normalize(task_text)
    best_activity = policy["default_activity"]
    best_score = 0
    for activity, config in policy["activities"].items():
        score = sum(1 for keyword in config.get("keywords", []) if normalize(keyword) in text)
        if score > best_score:
            best_activity = activity
            best_score = score

    if best_score:
        return best_activity, min(0.6 + (best_score * 0.1), 0.9), "keyword inference"
    return best_activity, 0.55, "default activity"


def infer_risk(policy: dict[str, Any], task_text: str, explicit_risk: str | None) -> tuple[str, str]:
    if explicit_risk:
        risk = normalize(explicit_risk)
        if risk not in {"low", "medium", "high"}:
            raise ValueError(f"Unknown risk: {explicit_risk}")
        return risk, "explicit risk"

    text = normalize(task_text)
    for risk in ("high", "medium"):
        keywords = policy.get("risk_escalation_keywords", {}).get(risk, [])
        if any(normalize(keyword) in text for keyword in keywords):
            return risk, f"{risk} risk keyword"
    return "low", "default low risk"


def infer_context_status() -> str:
    try:
        scripts_dir = str(ROOT / "scripts")
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
        from session_controls import infer_context_budget

        return str(infer_context_budget().get("status", "unknown"))
    except Exception:
        return "unknown"


def resolve_role_activity(policy: dict[str, Any], role: str | None) -> tuple[str | None, str]:
    role_id = normalize(role)
    if not role_id:
        return None, "no role"

    overrides = policy.get("role_activity_overrides", {})
    if role_id in overrides:
        return overrides[role_id], "explicit role override"

    suffixes = policy.get("role_suffix_fallbacks", {})
    for suffix, activity in suffixes.items():
        if role_id.endswith(f"-{suffix}") or role_id == suffix:
            return activity, f"role suffix fallback: {suffix}"

    default_activity = policy.get("default_role_activity")
    if default_activity:
        return default_activity, "default role activity"

    return None, "no matching role rule"


def read_role_ids(path: Path = ROLES_PATH) -> list[str]:
    if not path.exists():
        return []
    roles: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("- id:"):
            roles.append(stripped.split(":", 1)[1].strip())
    return roles


def role_coverage(policy: dict[str, Any]) -> dict[str, Any]:
    role_ids = read_role_ids()
    unresolved = []
    for role_id in role_ids:
        activity, _reason = resolve_role_activity(policy, role_id)
        if not activity:
            unresolved.append(role_id)
    return {
        "roles_total": len(role_ids),
        "roles_resolved": len(role_ids) - len(unresolved),
        "unresolved_roles": unresolved,
    }


def select_tier(
    policy: dict[str, Any],
    activity: str,
    risk: str,
    budget: str,
    context_status: str,
) -> tuple[str, list[str]]:
    activity_config = policy["activities"][activity]
    reasons: list[str] = [f"base activity tier: {activity_config['tier']}"]

    if risk == "high":
        tier = activity_config.get("high_risk_tier", "frontier")
        reasons.append(f"risk escalation: {tier}")
    elif budget == "low":
        tier = activity_config.get("low_budget_tier", activity_config["tier"])
        reasons.append(f"low budget tier: {tier}")
    else:
        tier = activity_config["tier"]

    if context_status in {"warning", "critical"}:
        reasons.append(f"context status {context_status}: compact before expanding")
        if risk != "high" and tier == "frontier":
            tier = "balanced"
            reasons.append("downgraded from frontier under context pressure")

    return tier, reasons


def build_selection(args: argparse.Namespace, policy: dict[str, Any]) -> dict[str, Any]:
    task_text = " ".join(args.task).strip()
    role_activity, role_reason = resolve_role_activity(policy, args.role)
    explicit_activity = args.activity or role_activity
    activity, confidence, activity_reason = infer_activity(policy, task_text, explicit_activity)
    risk, risk_reason = infer_risk(policy, task_text, args.risk)
    budget = normalize(args.budget or "standard")
    if budget not in {"low", "standard", "high"}:
        raise ValueError(f"Unknown budget: {args.budget}")

    context_status = infer_context_status()
    tier, tier_reasons = select_tier(policy, activity, risk, budget, context_status)
    model_config = policy["model_tiers"][tier]
    coverage = role_coverage(policy)

    compact_first = context_status in set(policy["token_policy"]["compact_when_context_status"])
    selection = {
        "generated_at": datetime.now(UTC).isoformat(),
        "task": task_text,
        "activity": activity,
        "activity_reason": activity_reason,
        "role": args.role,
        "role_reason": role_reason,
        "risk": risk,
        "risk_reason": risk_reason,
        "budget": budget,
        "context_status": context_status,
        "compact_first": compact_first,
        "tier": tier,
        "model": model_config["model"],
        "reasoning_effort": model_config["reasoning_effort"],
        "model_use_for": model_config["use_for"],
        "confidence": round(confidence, 2),
        "selection_reasons": tier_reasons,
        "role_coverage": coverage,
        "policy_path": str(POLICY_PATH.relative_to(ROOT)),
        "report_path": str(LATEST_MD.relative_to(ROOT)),
    }
    return selection


def write_reports(selection: dict[str, Any]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    LATEST_JSON.write_text(json.dumps(selection, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    reasons = "\n".join(f"- {reason}" for reason in selection["selection_reasons"])
    unresolved = selection["role_coverage"]["unresolved_roles"]
    unresolved_text = ", ".join(f"`{role}`" for role in unresolved) if unresolved else "none"
    lines = [
        "# Model Routing Selection",
        "",
        f"- generated_at: `{selection['generated_at']}`",
        f"- activity: `{selection['activity']}`",
        f"- role: `{selection['role'] or 'none'}`",
        f"- risk: `{selection['risk']}`",
        f"- budget: `{selection['budget']}`",
        f"- context_status: `{selection['context_status']}`",
        f"- compact_first: `{str(selection['compact_first']).lower()}`",
        f"- selected_tier: `{selection['tier']}`",
        f"- selected_model: `{selection['model']}`",
        f"- reasoning_effort: `{selection['reasoning_effort']}`",
        f"- confidence: `{selection['confidence']}`",
        "",
        "## Reasons",
        "",
        reasons,
        "",
        "## Specialist Coverage",
        "",
        f"- roles_total: `{selection['role_coverage']['roles_total']}`",
        f"- roles_resolved_by_policy: `{selection['role_coverage']['roles_resolved']}`",
        f"- unresolved_roles: {unresolved_text}",
        "",
        "## Policy",
        "",
        f"- manifest: `{selection['policy_path']}`",
        f"- latest_json: `{LATEST_JSON.relative_to(ROOT)}`",
    ]
    LATEST_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Select the Codex model tier for an AgentCodex task and record the decision."
    )
    parser.add_argument("task", nargs="*", help="Task description used for automatic activity inference")
    parser.add_argument("--activity", help="Explicit activity id, such as brainstorm, design, implementation, review")
    parser.add_argument("--role", help="Specialist role id, such as explorer, reviewer, or ai-data-engineer")
    parser.add_argument("--budget", choices=["low", "standard", "high"], default="standard")
    parser.add_argument("--risk", choices=["low", "medium", "high"])
    parser.add_argument("--json", action="store_true", help="Print the full selection payload as JSON")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    policy = load_policy()
    selection = build_selection(args, policy)
    write_reports(selection)

    if args.json:
        print(json.dumps(selection, indent=2, sort_keys=True))
    else:
        print(
            f"{selection['model']} "
            f"(tier={selection['tier']}, reasoning={selection['reasoning_effort']}, "
            f"activity={selection['activity']}, risk={selection['risk']})"
        )
        print(f"Recorded: {selection['report_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
