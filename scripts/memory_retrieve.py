#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import re
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

from memory_backend import get_backend, parse_simple_yaml
from memory_lifecycle import STALE_THRESHOLDS, compute_decayed_confidence
from memory_observability import record_memory_failure, update_memory_metrics
from observability_runtime import ScriptRun

ROOT = Path(__file__).resolve().parent.parent
MEMORY_ROOT = ROOT / ".agentcodex" / "memory"
CACHE_ROOT = ROOT / ".agentcodex" / "cache" / "memory"
REPORTS_ROOT = ROOT / ".agentcodex" / "reports" / "memory"
BACKEND = get_backend()
SUMMARY_PATH = BACKEND.summary_path()
SNAPSHOT_PATHS = {
    **BACKEND.snapshot_paths(),
}
LIMITS = {"semantic": 3, "episodic": 2, "procedural": 1}
PROCEDURAL_TASK_TYPES = {"implement", "operate", "debug", "troubleshoot", "review", "ship"}
TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9-]+")
DEFAULT_REQUESTER_ROLE = "explorer"


def print_usage() -> int:
    print(
        "Usage: python3 scripts/agentcodex.py memory-retrieve <query> "
        "[--task-type <type>] [--scope <scope>] [--scope-value <value>] "
        "[--requester-role <role>] [--requester-owner <owner>] [--json]"
    )
    return 1


def tokenize(value: str) -> set[str]:
    return {token for token in TOKEN_RE.findall(value.casefold()) if len(token) > 1}


def parse_iso(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def lexical_score(query_tokens: set[str], candidate_text: str) -> float:
    candidate_tokens = tokenize(candidate_text)
    if not query_tokens or not candidate_tokens:
        return 0.0
    overlap = len(query_tokens & candidate_tokens)
    return overlap / max(len(query_tokens), 1)


def recency_score(timestamp: str) -> float:
    parsed = parse_iso(timestamp)
    if parsed is None:
        return 0.0
    now = datetime.now(UTC)
    age_days = max((now - parsed).total_seconds() / 86400.0, 0.0)
    return 1.0 / (1.0 + math.log1p(age_days))


def scope_match(item: dict, scope: str | None, scope_value: str | None) -> float:
    item_scope = item.get("scope", {})
    if not isinstance(item_scope, dict):
        return 0.0
    if scope is None:
        return 0.1
    if item_scope.get("type") != scope:
        return 0.0
    if scope_value is None:
        return 0.25
    return 0.35 if item_scope.get("value") == scope_value else 0.0


def load_items(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def parse_access_controls() -> tuple[dict[str, str], dict[str, dict[str, list[str]]]]:
    path = MEMORY_ROOT / "manifests" / "memory-access.yaml"
    default_rules: dict[str, str] = {}
    access_templates: dict[str, dict[str, list[str]]] = {}
    current_template_id: str | None = None
    current_list_key: str | None = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("version:"):
            continue
        if stripped in {"default_rules:", "access_templates:"}:
            current_template_id = None
            current_list_key = None
            continue
        if line.startswith("  ") and not line.startswith("    ") and ":" in stripped and not stripped.startswith("- "):
            key, value = stripped.split(":", 1)
            default_rules[key.strip()] = value.strip()
            current_list_key = None
            continue
        if stripped.startswith("- template_id:"):
            current_template_id = stripped.split(":", 1)[1].strip()
            access_templates[current_template_id] = {"permitted_roles": [], "allowed_scopes": []}
            current_list_key = None
            continue
        if current_template_id and stripped.endswith(":") and stripped[:-1] in {"permitted_roles", "allowed_scopes"}:
            current_list_key = stripped[:-1]
            continue
        if current_template_id and current_list_key and stripped.startswith("- "):
            access_templates[current_template_id][current_list_key].append(stripped[2:].strip())

    return default_rules, access_templates


def resolve_access_template_id(item: dict) -> str:
    sensitivity = str(item.get("sensitivity", "")).strip().lower()
    if sensitivity == "restricted":
        return "restricted-memory"
    return "project-default"


def access_filter(
    items: list[dict],
    requester_role: str,
    requester_owner: str | None,
    requested_scope: str | None,
    requested_scope_value: str | None,
) -> tuple[list[dict], int]:
    default_rules, templates = parse_access_controls()
    filtered: list[dict] = []
    denied = 0

    require_owner = default_rules.get("require_owner") == "true"
    require_sensitivity = default_rules.get("require_sensitivity") == "true"
    deny_cross_scope_without_owner_match = default_rules.get("deny_cross_scope_without_owner_match") == "true"

    for item in items:
        owner = str(item.get("owner", "")).strip()
        sensitivity = str(item.get("sensitivity", "")).strip()
        item_scope = item.get("scope", {})
        item_scope_type = item_scope.get("type") if isinstance(item_scope, dict) else None
        item_scope_value = item_scope.get("value") if isinstance(item_scope, dict) else None

        if require_owner and not owner:
            denied += 1
            continue
        if require_sensitivity and not sensitivity:
            denied += 1
            continue

        template = templates.get(resolve_access_template_id(item), {})
        permitted_roles = template.get("permitted_roles", [])
        allowed_scopes = template.get("allowed_scopes", [])

        if permitted_roles and requester_role not in permitted_roles:
            denied += 1
            continue
        if allowed_scopes and item_scope_type not in allowed_scopes:
            denied += 1
            continue

        cross_scope = False
        if requested_scope and item_scope_type != requested_scope:
            cross_scope = True
        if requested_scope_value and item_scope_value != requested_scope_value:
            cross_scope = True
        if deny_cross_scope_without_owner_match and cross_scope and requester_owner != owner:
            denied += 1
            continue

        filtered.append(item)

    return filtered, denied


def parse_retention_policies() -> dict[str, dict[str, str]]:
    path = MEMORY_ROOT / "manifests" / "memory-retention.yaml"
    policies: dict[str, dict[str, str]] = {}
    current_id: str | None = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("version:") or stripped == "policies:":
            continue
        if stripped.startswith("- id:"):
            current_id = stripped.split(":", 1)[1].strip()
            policies[current_id] = {"id": current_id}
            continue
        if current_id and ":" in stripped:
            key, value = stripped.split(":", 1)
            policies[current_id][key.strip()] = value.strip()

    return policies


def retention_filter(items: list[dict], now: datetime | None = None) -> tuple[list[dict], int]:
    now = now or datetime.now(UTC)
    policies = parse_retention_policies()
    filtered: list[dict] = []
    denied = 0

    for item in items:
        policy_id = str(item.get("retention_policy", "")).strip()
        if not policy_id:
            denied += 1
            continue
        policy = policies.get(policy_id)
        if not policy:
            denied += 1
            continue

        memory_type = str(item.get("memory_type", "")).strip()
        item_scope = item.get("scope", {})
        item_scope_type = item_scope.get("type") if isinstance(item_scope, dict) else None
        if policy.get("memory_type") and policy.get("memory_type") != memory_type:
            denied += 1
            continue
        if policy.get("scope") and policy.get("scope") != item_scope_type:
            denied += 1
            continue

        if memory_type == "episodic":
            decayed = compute_decayed_confidence(item, now)
            if decayed < STALE_THRESHOLDS["episodic"]:
                denied += 1
                continue

        filtered.append(item)

    return filtered, denied


def semantic_text(item: dict) -> str:
    return " ".join(
        str(item.get(key, ""))
        for key in ["subject", "canonical_fact", "supporting_context"]
    ) + " " + " ".join(item.get("tags", []))


def episodic_text(item: dict) -> str:
    return " ".join(
        [
            str(item.get("event_title", "")),
            str(item.get("event_summary", "")),
            str(item.get("outcome", "")),
            " ".join(item.get("actors", [])),
            " ".join(item.get("references", [])),
            " ".join(item.get("tags", [])),
        ]
    )


def procedural_text(item: dict) -> str:
    return " ".join(
        [
            str(item.get("procedure_title", "")),
            str(item.get("trigger", "")),
            " ".join(item.get("steps", [])),
            " ".join(item.get("constraints", [])),
            " ".join(item.get("success_signals", [])),
            " ".join(item.get("failure_signals", [])),
            " ".join(item.get("tags", [])),
        ]
    )


def rank_semantic(items: list[dict], query_tokens: set[str], scope: str | None, scope_value: str | None) -> list[dict]:
    ranked: list[tuple[float, dict]] = []
    for item in items:
        score = (
            0.55 * lexical_score(query_tokens, semantic_text(item))
            + 0.2 * recency_score(str(item.get("updated_at", item.get("created_at", ""))))
            + 0.15 * float(item.get("confidence", 0.0))
            + 0.1 * scope_match(item, scope, scope_value)
        )
        ranked.append((score, item))
    return [item for score, item in sorted(ranked, key=lambda pair: pair[0], reverse=True)[: LIMITS["semantic"]] if score > 0]


def rank_episodic(items: list[dict], query_tokens: set[str], scope: str | None, scope_value: str | None) -> list[dict]:
    ranked: list[tuple[float, dict]] = []
    for item in items:
        score = (
            0.5 * lexical_score(query_tokens, episodic_text(item))
            + 0.2 * recency_score(str(item.get("timestamp", "")))
            + 0.2 * float(item.get("importance", 0.0))
            + 0.1 * scope_match(item, scope, scope_value)
        )
        ranked.append((score, item))
    return [item for score, item in sorted(ranked, key=lambda pair: pair[0], reverse=True)[: LIMITS["episodic"]] if score > 0]


def rank_procedural(items: list[dict], query_tokens: set[str], scope: str | None, scope_value: str | None) -> list[dict]:
    ranked: list[tuple[float, dict]] = []
    for item in items:
        approval_bonus = 0.15 if item.get("approval_state") == "approved" else 0.0
        score = (
            0.55 * lexical_score(query_tokens, procedural_text(item))
            + 0.2 * recency_score(str(item.get("updated_at", "")))
            + approval_bonus
            + 0.1 * scope_match(item, scope, scope_value)
        )
        ranked.append((score, item))
    return [item for score, item in sorted(ranked, key=lambda pair: pair[0], reverse=True)[: LIMITS["procedural"]] if score > 0]


def compact_view(item: dict, memory_type: str) -> dict:
    common = {
        "memory_id": item.get("memory_id"),
        "scope": item.get("scope"),
        "tags": item.get("tags", []),
        "owner": item.get("owner"),
        "sensitivity": item.get("sensitivity"),
    }
    if memory_type == "semantic":
        common.update(
            {
                "subject": item.get("subject"),
                "canonical_fact": item.get("canonical_fact"),
                "confidence": item.get("confidence"),
            }
        )
    elif memory_type == "episodic":
        common.update(
            {
                "event_title": item.get("event_title"),
                "event_summary": item.get("event_summary"),
                "outcome": item.get("outcome"),
                "importance": item.get("importance"),
            }
        )
    else:
        common.update(
            {
                "procedure_title": item.get("procedure_title"),
                "trigger": item.get("trigger"),
                "approval_state": item.get("approval_state"),
                "steps": item.get("steps", [])[:3],
            }
        )
    return common


def write_report(query: str, task_type: str, packet: dict) -> Path:
    REPORTS_ROOT.mkdir(parents=True, exist_ok=True)
    path = REPORTS_ROOT / "retrieval-report.md"
    lines = [
        "# Memory Retrieval Report",
        "",
        f"- query: {query}",
        f"- task_type: {task_type}",
        f"- generated_at: {datetime.now(UTC).isoformat()}",
        "",
        "## Summary",
        "",
        f"- semantic_count: {len(packet['semantic_memories'])}",
        f"- episodic_count: {len(packet['episodic_memories'])}",
        f"- procedural_count: {len(packet['procedural_memories'])}",
        "",
        "## Local Summaries",
        "",
    ]
    for item in packet["local_summaries"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Selected Memories", ""])
    for label in ["semantic_memories", "episodic_memories", "procedural_memories"]:
        lines.append(f"### {label}")
        lines.append("")
        for item in packet[label]:
            lines.append(f"- `{item.get('memory_id')}`")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> int:
    run = ScriptRun(ROOT, "memory-retrieve")
    started = time.perf_counter()
    run.event("info", "memory retrieval started")
    args = sys.argv[1:]
    if not args:
        record_memory_failure("memory-retrieve", "missing query", "argument-parse")
        run.event("error", "memory retrieval failed", reason="missing query")
        update_memory_metrics("memory-retrieve", {"access_denials": 0, "retrieval_count": 0}, "failed")
        return print_usage()

    query_parts: list[str] = []
    task_type = "general"
    scope: str | None = None
    scope_value: str | None = None
    requester_role = DEFAULT_REQUESTER_ROLE
    requester_owner: str | None = None
    as_json = False
    i = 0
    while i < len(args):
        arg = args[i]
        if not arg.startswith("--"):
            query_parts.append(arg)
            i += 1
            continue
        if arg == "--task-type" and i + 1 < len(args):
            task_type = args[i + 1].strip()
            i += 2
            continue
        if arg == "--scope" and i + 1 < len(args):
            scope = args[i + 1].strip()
            i += 2
            continue
        if arg == "--scope-value" and i + 1 < len(args):
            scope_value = args[i + 1].strip()
            i += 2
            continue
        if arg == "--requester-role" and i + 1 < len(args):
            requester_role = args[i + 1].strip()
            i += 2
            continue
        if arg == "--requester-owner" and i + 1 < len(args):
            requester_owner = args[i + 1].strip()
            i += 2
            continue
        if arg == "--json":
            as_json = True
            i += 1
            continue
        record_memory_failure("memory-retrieve", f"unknown arg: {arg}", "argument-parse")
        run.event("error", "memory retrieval failed", reason=f"unknown arg: {arg}")
        update_memory_metrics("memory-retrieve", {"access_denials": 0, "retrieval_count": 0}, "failed")
        return print_usage()

    query = " ".join(query_parts).strip()
    if not query:
        record_memory_failure("memory-retrieve", "empty query", "argument-parse")
        run.event("error", "memory retrieval failed", reason="empty query")
        update_memory_metrics("memory-retrieve", {"access_denials": 0, "retrieval_count": 0}, "failed")
        return print_usage()

    if requester_owner is None:
        requester_owner = scope_value

    semantic_items = BACKEND.load("semantic")
    episodic_items = BACKEND.load("episodic")
    procedural_items = BACKEND.load("procedural")

    semantic_items, semantic_access_denials = access_filter(
        semantic_items, requester_role, requester_owner, scope, scope_value
    )
    episodic_items, episodic_access_denials = access_filter(
        episodic_items, requester_role, requester_owner, scope, scope_value
    )
    procedural_items, procedural_access_denials = access_filter(
        procedural_items, requester_role, requester_owner, scope, scope_value
    )
    access_denials = semantic_access_denials + episodic_access_denials + procedural_access_denials

    semantic_items, semantic_retention_denials = retention_filter(semantic_items)
    episodic_items, episodic_retention_denials = retention_filter(episodic_items)
    procedural_items, procedural_retention_denials = retention_filter(procedural_items)
    retention_actions = (
        semantic_retention_denials + episodic_retention_denials + procedural_retention_denials
    )

    query_tokens = tokenize(query)
    selected_semantic = rank_semantic(semantic_items, query_tokens, scope, scope_value)
    selected_episodic = rank_episodic(episodic_items, query_tokens, scope, scope_value)
    selected_procedural: list[dict] = []
    if task_type in PROCEDURAL_TASK_TYPES:
        selected_procedural = rank_procedural(procedural_items, query_tokens, scope, scope_value)

    local_summaries: list[str] = []
    if SUMMARY_PATH.exists():
        local_summaries.append(str(SUMMARY_PATH.relative_to(ROOT)))

    packet = {
        "query": query,
        "task_type": task_type,
        "requester": {"role": requester_role, "owner": requester_owner},
        "scope_filter": {"scope": scope, "scope_value": scope_value},
        "limits": LIMITS,
        "local_summaries": local_summaries,
        "access_denials": access_denials,
        "retention_filtered": retention_actions,
        "semantic_memories": [compact_view(item, "semantic") for item in selected_semantic],
        "episodic_memories": [compact_view(item, "episodic") for item in selected_episodic],
        "procedural_memories": [compact_view(item, "procedural") for item in selected_procedural],
    }
    report_path = write_report(query, task_type, packet)
    packet["report_path"] = str(report_path.relative_to(ROOT))
    duration_ms = round((time.perf_counter() - started) * 1000, 2)
    metrics = {
        "retrieval_count": len(packet["semantic_memories"]) + len(packet["episodic_memories"]) + len(packet["procedural_memories"]),
        "memory_hit_rate": 1.0 if any([packet["semantic_memories"], packet["episodic_memories"], packet["procedural_memories"]]) else 0.0,
        "write_count": 0,
        "dedup_count": 0,
        "compaction_events": 0,
        "retention_actions": retention_actions,
        "access_denials": access_denials,
        "latency_ms": duration_ms,
        "backend_failures": 0,
        "active_backend": BACKEND.backend_id,
    }
    run.event(
        "info",
        "memory retrieval completed",
        query=query,
        task_type=task_type,
        retrieval_count=metrics["retrieval_count"],
    )
    for key, value in metrics.items():
        run.metric(key, value)
    run.finalize("success", {"query": query, "task_type": task_type, "report_path": str(report_path.relative_to(ROOT))})
    update_memory_metrics("memory-retrieve", metrics, "success")

    if as_json:
        print(json.dumps(packet, indent=2))
        return 0

    print("# Memory Context Packet")
    print()
    print(f"- query: {query}")
    print(f"- task_type: {task_type}")
    print(f"- report_path: {report_path.relative_to(ROOT)}")
    print()
    print("## Local Summaries")
    for item in local_summaries:
        print(f"- {item}")
    print()
    print("## Semantic")
    for item in packet["semantic_memories"]:
        print(f"- {item['memory_id']}: {item.get('canonical_fact')}")
    print()
    print("## Episodic")
    for item in packet["episodic_memories"]:
        print(f"- {item['memory_id']}: {item.get('event_summary')}")
    print()
    print("## Procedural")
    for item in packet["procedural_memories"]:
        print(f"- {item['memory_id']}: {item.get('trigger')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
