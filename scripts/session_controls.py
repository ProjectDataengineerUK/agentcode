#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
OBS_ROOT = ROOT / ".agentcodex" / "observability"
METRICS_ROOT = OBS_ROOT / "metrics"
REPORTS_ROOT = ROOT / ".agentcodex" / "reports" / "session-controls"
MODEL_ROUTING_POLICY = ROOT / ".agentcodex" / "model-routing.json"
MODEL_ROUTING_LATEST = ROOT / ".agentcodex" / "reports" / "model-routing" / "latest-selection.json"

CONTEXT_LIMIT = 180_000
WARN_THRESHOLD = 0.80
CRITICAL_THRESHOLD = 0.95

COST_TIERS = {
    "platform-health": "LOW",
    "sync-sources": "MEDIUM",
    "check-updates": "MEDIUM",
    "memory-retrieve": "LOW",
    "memory-ingest": "LOW",
    "memory-compact": "LOW",
}


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def infer_context_budget() -> dict[str, object]:
    kb_metrics = load_json(METRICS_ROOT / "kb-health.json")
    memory_metrics = load_json(METRICS_ROOT / "memory-health.json")

    latest_latency = 0.0
    latest_entries = 0
    for payload in [kb_metrics.get("metrics", {}), memory_metrics.get("script_metrics", {}).get("memory-retrieve", {})]:
        if isinstance(payload, dict):
            latest_latency = max(latest_latency, float(payload.get("latency_ms", 0.0) or 0.0))
            latest_entries = max(latest_entries, int(payload.get("indexed_entries", 0) or 0))

    estimated_input_tokens = min(
        CONTEXT_LIMIT,
        int((latest_entries * 11) + (latest_latency * 12) + 1200),
    )
    estimated_output_tokens = max(200, int(estimated_input_tokens * 0.08))
    usage_ratio = estimated_input_tokens / CONTEXT_LIMIT
    if usage_ratio >= CRITICAL_THRESHOLD:
        status = "critical"
    elif usage_ratio >= WARN_THRESHOLD:
        status = "warning"
    else:
        status = "ok"

    return {
        "input_tokens": estimated_input_tokens,
        "output_tokens": estimated_output_tokens,
        "total_tokens": estimated_input_tokens + estimated_output_tokens,
        "limit": CONTEXT_LIMIT,
        "usage_ratio": round(usage_ratio, 4),
        "remaining_tokens": max(0, CONTEXT_LIMIT - estimated_input_tokens),
        "status": status,
        "estimation_mode": "repo-local-heuristic",
    }


def infer_cost_summary() -> dict[str, object]:
    kb_metrics = load_json(METRICS_ROOT / "kb-health.json")
    memory_metrics = load_json(METRICS_ROOT / "memory-health.json")
    last_runs = []
    for payload in [kb_metrics.get("last_runs", []), memory_metrics.get("last_runs", [])]:
        if isinstance(payload, list):
            last_runs.extend(payload)

    by_tier: dict[str, int] = {}
    by_script: dict[str, int] = {}
    for run in last_runs:
        script = str(run.get("script", "unknown"))
        tier = COST_TIERS.get(script, "LOW")
        by_tier[tier] = by_tier.get(tier, 0) + 1
        by_script[script] = by_script.get(script, 0) + 1

    return {
        "total_operations": sum(by_script.values()),
        "by_tier": by_tier,
        "by_script": by_script,
        "classification_mode": "repo-local-script-tiering",
    }


def infer_model_routing_summary() -> dict[str, object]:
    policy = load_json(MODEL_ROUTING_POLICY)
    latest = load_json(MODEL_ROUTING_LATEST)
    return {
        "policy_present": bool(policy),
        "policy_version": policy.get("version"),
        "record_every_automatic_selection": bool(
            policy.get("token_policy", {}).get("record_every_automatic_selection", False)
        ),
        "latest_model": latest.get("model"),
        "latest_activity": latest.get("activity"),
        "latest_tier": latest.get("tier"),
        "latest_reasoning_effort": latest.get("reasoning_effort"),
        "latest_generated_at": latest.get("generated_at"),
        "classification_mode": "repo-local-model-routing-policy",
    }


def write_report(payload: dict[str, object]) -> Path:
    REPORTS_ROOT.mkdir(parents=True, exist_ok=True)
    path = REPORTS_ROOT / "session-controls.md"
    context = payload["context_budget"]
    cost = payload["cost_summary"]
    model_routing = payload["model_routing"]
    lines = [
        "# Session Controls Report",
        "",
        f"- generated_at: {payload['generated_at']}",
        "",
        "## Context Budget",
        "",
        f"- input_tokens: {context['input_tokens']}",
        f"- output_tokens: {context['output_tokens']}",
        f"- total_tokens: {context['total_tokens']}",
        f"- limit: {context['limit']}",
        f"- usage_ratio: {context['usage_ratio']}",
        f"- remaining_tokens: {context['remaining_tokens']}",
        f"- status: {context['status']}",
        f"- estimation_mode: {context['estimation_mode']}",
        "",
        "## Cost Summary",
        "",
        f"- total_operations: {cost['total_operations']}",
        f"- classification_mode: {cost['classification_mode']}",
        "",
        "### By Tier",
        "",
    ]
    for tier, count in sorted(cost["by_tier"].items()):
        lines.append(f"- {tier}: {count}")
    lines.extend(["", "### By Script", ""])
    for script, count in sorted(cost["by_script"].items()):
        lines.append(f"- {script}: {count}")
    lines.extend(
        [
            "",
            "## Model Routing",
            "",
            f"- policy_present: {model_routing['policy_present']}",
            f"- policy_version: {model_routing['policy_version']}",
            f"- record_every_automatic_selection: {model_routing['record_every_automatic_selection']}",
            f"- latest_model: {model_routing['latest_model']}",
            f"- latest_activity: {model_routing['latest_activity']}",
            f"- latest_tier: {model_routing['latest_tier']}",
            f"- latest_reasoning_effort: {model_routing['latest_reasoning_effort']}",
            f"- latest_generated_at: {model_routing['latest_generated_at']}",
            f"- classification_mode: {model_routing['classification_mode']}",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def build_payload() -> dict[str, object]:
    payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "context_budget": infer_context_budget(),
        "cost_summary": infer_cost_summary(),
        "model_routing": infer_model_routing_summary(),
    }
    report_path = write_report(payload)
    payload["report_path"] = str(report_path.relative_to(ROOT))
    return payload
