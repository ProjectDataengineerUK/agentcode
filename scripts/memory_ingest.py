#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

from memory_backend import get_backend
import memory_retrieve as memory
from memory_observability import record_memory_failure, update_memory_metrics
from observability_runtime import ScriptRun


ROOT = Path(__file__).resolve().parent.parent
MEMORY_ROOT = ROOT / ".agentcodex" / "memory"
MEMORY_CANDIDATES_ROOT = MEMORY_ROOT / "candidates"
MEMORY_INGEST_ROOT = MEMORY_ROOT / "ingest"
ALLOWED_SOURCE_ROOTS = (MEMORY_CANDIDATES_ROOT, MEMORY_INGEST_ROOT)
REPORTS_ROOT = ROOT / ".agentcodex" / "reports" / "memory"
BACKEND = get_backend()

REQUIRED_FIELDS = {
    "semantic": [
        "memory_id",
        "memory_type",
        "scope",
        "subject",
        "canonical_fact",
        "supporting_context",
        "confidence",
        "source",
        "created_at",
        "updated_at",
        "tags",
        "sensitivity",
        "retention_policy",
        "owner",
    ],
    "episodic": [
        "memory_id",
        "memory_type",
        "scope",
        "event_title",
        "event_summary",
        "actors",
        "timestamp",
        "outcome",
        "references",
        "importance",
        "tags",
        "sensitivity",
        "retention_policy",
        "owner",
    ],
    "procedural": [
        "memory_id",
        "memory_type",
        "scope",
        "procedure_title",
        "trigger",
        "steps",
        "constraints",
        "success_signals",
        "failure_signals",
        "source",
        "approval_state",
        "updated_at",
        "tags",
        "owner",
    ],
}


def print_usage() -> int:
    print("Usage: python3 scripts/agentcodex.py memory-ingest <semantic|episodic|procedural> <json-file>")
    return 1


def text_for_item(item: dict, memory_type: str) -> str:
    if memory_type == "semantic":
        return memory.semantic_text(item)
    if memory_type == "episodic":
        return memory.episodic_text(item)
    return memory.procedural_text(item)


def similarity(left: dict, right: dict, memory_type: str) -> float:
    left_tokens = memory.tokenize(text_for_item(left, memory_type))
    right_tokens = memory.tokenize(text_for_item(right, memory_type))
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / len(left_tokens | right_tokens)


def validate_item(item: dict, memory_type: str) -> list[str]:
    errors: list[str] = []
    for field in REQUIRED_FIELDS[memory_type]:
        if field not in item:
            errors.append(f"missing field: {field}")
    scope = item.get("scope")
    if not isinstance(scope, dict) or not scope.get("type") or not scope.get("value"):
        errors.append("scope must be an object with type and value")
    if not item.get("owner"):
        errors.append("owner is required")
    if not item.get("source"):
        errors.append("source is required")
    if not item.get("sensitivity"):
        errors.append("sensitivity is required")
    if not item.get("retention_policy"):
        errors.append("retention_policy is required")
    return errors


def write_report(memory_type: str, source_path: Path, action: str, issues: list[str], target_path: Path) -> Path:
    REPORTS_ROOT.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_ROOT / "ingest-report.md"
    lines = [
        "# Memory Ingest Report",
        "",
        f"- generated_at: {datetime.now(UTC).isoformat()}",
        f"- memory_type: {memory_type}",
        f"- source_file: {display_path(source_path)}",
        f"- action: {action}",
        f"- target_snapshot: {display_path(target_path)}",
        "",
    ]
    if issues:
        lines.extend(["## Issues", ""])
        lines.extend(f"- {issue}" for issue in issues)
        lines.append("")
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def resolve_source_path(path_arg: str, allowed_roots: tuple[Path, ...] = ALLOWED_SOURCE_ROOTS) -> Path:
    path = Path(path_arg)
    if not path.is_absolute():
        path = ROOT / path
    resolved = path.resolve()
    for root in allowed_roots:
        try:
            resolved.relative_to(root.resolve())
            return resolved
        except ValueError:
            continue
    allowed_display = ", ".join(str(root.relative_to(ROOT)) for root in allowed_roots)
    raise ValueError(f"source file must stay within approved memory roots: {allowed_display}")


def main() -> int:
    run = ScriptRun(ROOT, "memory-ingest")
    started = time.perf_counter()
    run.event("info", "memory ingest started")
    if len(sys.argv) != 3:
        record_memory_failure("memory-ingest", "invalid arguments", "argument-parse")
        run.event("error", "memory ingest failed", reason="invalid arguments")
        update_memory_metrics("memory-ingest", {"write_count": 0, "dedup_count": 0, "latency_ms": 0}, "failed")
        return print_usage()

    memory_type = sys.argv[1].strip()
    if memory_type not in REQUIRED_FIELDS:
        record_memory_failure("memory-ingest", f"invalid memory type: {memory_type}", "argument-parse")
        run.event("error", "memory ingest failed", reason=f"invalid memory type: {memory_type}")
        update_memory_metrics("memory-ingest", {"write_count": 0, "dedup_count": 0, "latency_ms": 0}, "failed")
        return print_usage()
    try:
        source_path = resolve_source_path(sys.argv[2])
    except ValueError as exc:
        record_memory_failure("memory-ingest", str(exc), "load-source")
        run.event("error", "memory ingest failed", reason=str(exc))
        update_memory_metrics("memory-ingest", {"write_count": 0, "dedup_count": 0, "latency_ms": 0}, "failed")
        print(str(exc))
        return 1
    if not source_path.exists():
        record_memory_failure("memory-ingest", f"source file missing: {source_path}", "load-source")
        run.event("error", "memory ingest failed", reason=f"source file missing: {source_path}")
        update_memory_metrics("memory-ingest", {"write_count": 0, "dedup_count": 0, "latency_ms": 0}, "failed")
        print(f"Source file does not exist: {source_path}")
        return 1

    item = json.loads(source_path.read_text(encoding="utf-8"))
    errors = validate_item(item, memory_type)
    snapshot_path = BACKEND.snapshot_paths()[memory_type]
    if errors:
        report_path = write_report(memory_type, source_path, "rejected", errors, snapshot_path)
        run.event("error", "memory ingest rejected", memory_type=memory_type, report_path=str(report_path.relative_to(ROOT)))
        metrics = {
            "retrieval_count": 0,
            "memory_hit_rate": 0.0,
            "write_count": 0,
            "dedup_count": 0,
            "compaction_events": 0,
            "retention_actions": 0,
            "access_denials": 0,
            "latency_ms": round((time.perf_counter() - started) * 1000, 2),
            "backend_failures": 0,
        }
        for key, value in metrics.items():
            run.metric(key, value)
        run.finalize("failed", {"report_path": str(report_path.relative_to(ROOT)), "reason": "validation"})
        update_memory_metrics("memory-ingest", metrics, "failed")
        print(f"Memory ingest failed. Report: {report_path}")
        for issue in errors:
            print(f"- {issue}")
        return 1

    current = BACKEND.load(memory_type)

    for index, existing in enumerate(current):
        if existing.get("memory_id") == item["memory_id"]:
            current[index] = item
            report_path = write_report(memory_type, source_path, "updated-by-id", [], snapshot_path)
            BACKEND.upsert(memory_type, current)
            run.event("info", "memory ingest updated by id", memory_type=memory_type, memory_id=item["memory_id"])
            metrics = {
                "retrieval_count": 0,
                "memory_hit_rate": 0.0,
                "write_count": 1,
                "dedup_count": 0,
                "compaction_events": 0,
                "retention_actions": 0,
                "access_denials": 0,
                "latency_ms": round((time.perf_counter() - started) * 1000, 2),
                "backend_failures": 0,
            }
            for key, value in metrics.items():
                run.metric(key, value)
            run.finalize("success", {"report_path": str(report_path.relative_to(ROOT)), "action": "updated-by-id"})
            update_memory_metrics("memory-ingest", metrics, "success")
            print(f"Updated memory by id. Report: {report_path}")
            return 0

    for index, existing in enumerate(current):
        if similarity(existing, item, memory_type) >= 0.82:
            merged = dict(existing)
            merged.update(item)
            if memory_type == "semantic":
                merged["updated_at"] = item.get("updated_at", existing.get("updated_at"))
            elif memory_type == "episodic":
                merged["timestamp"] = item.get("timestamp", existing.get("timestamp"))
            else:
                merged["updated_at"] = item.get("updated_at", existing.get("updated_at"))
            current[index] = merged
            report_path = write_report(memory_type, source_path, "merged-near-duplicate", [], snapshot_path)
            BACKEND.upsert(memory_type, current)
            run.event("info", "memory ingest merged near-duplicate", memory_type=memory_type, memory_id=item["memory_id"])
            metrics = {
                "retrieval_count": 0,
                "memory_hit_rate": 0.0,
                "write_count": 1,
                "dedup_count": 1,
                "compaction_events": 0,
                "retention_actions": 0,
                "access_denials": 0,
                "latency_ms": round((time.perf_counter() - started) * 1000, 2),
                "backend_failures": 0,
            }
            for key, value in metrics.items():
                run.metric(key, value)
            run.finalize("success", {"report_path": str(report_path.relative_to(ROOT)), "action": "merged-near-duplicate"})
            update_memory_metrics("memory-ingest", metrics, "success")
            print(f"Merged near-duplicate memory. Report: {report_path}")
            return 0

    current.append(item)
    BACKEND.upsert(memory_type, current)
    report_path = write_report(memory_type, source_path, "appended", [], snapshot_path)
    run.event("info", "memory ingest appended", memory_type=memory_type, memory_id=item["memory_id"])
    metrics = {
        "retrieval_count": 0,
        "memory_hit_rate": 0.0,
        "write_count": 1,
        "dedup_count": 0,
        "compaction_events": 0,
        "retention_actions": 0,
        "access_denials": 0,
        "latency_ms": round((time.perf_counter() - started) * 1000, 2),
        "backend_failures": 0,
    }
    for key, value in metrics.items():
        run.metric(key, value)
    run.finalize("success", {"report_path": str(report_path.relative_to(ROOT)), "action": "appended"})
    update_memory_metrics("memory-ingest", metrics, "success")
    print(f"Appended memory. Report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
