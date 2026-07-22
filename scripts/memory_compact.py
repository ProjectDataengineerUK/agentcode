#!/usr/bin/env python3
from __future__ import annotations

import sys
import time
from datetime import UTC, datetime
from pathlib import Path

from memory_backend import get_backend
import memory_ingest as ingest
import memory_retrieve as memory
from memory_observability import update_memory_metrics
from observability_runtime import ScriptRun


ROOT = Path(__file__).resolve().parent.parent
REPORTS_ROOT = ROOT / ".agentcodex" / "reports" / "memory"
BACKEND = get_backend()
SUMMARY_PATH = BACKEND.summary_path()


def deduplicate(items: list[dict], memory_type: str) -> tuple[list[dict], int]:
    result: list[dict] = []
    dedup_count = 0
    for item in items:
        merged = False
        for idx, existing in enumerate(result):
            if existing.get("memory_id") == item.get("memory_id") or ingest.similarity(existing, item, memory_type) >= 0.82:
                combined = dict(existing)
                combined.update(item)
                result[idx] = combined
                dedup_count += 1
                merged = True
                break
        if not merged:
            result.append(item)
    return result, dedup_count


def build_summary(semantic: list[dict], episodic: list[dict], procedural: list[dict]) -> str:
    lines = [
        "# Local Memory Summary",
        "",
        "## Snapshot",
        "",
        f"- semantic memories: {len(semantic)}",
        f"- episodic memories: {len(episodic)}",
        f"- procedural memories: {len(procedural)}",
        "",
        "## Local Use",
        "",
        "- use semantic memories for stable facts",
        "- use episodic memories for important past outcomes",
        "- use procedural memories only when the task type justifies operational guidance",
        "",
        "## Top Semantic Facts",
        "",
    ]
    for item in semantic[:3]:
        lines.append(f"- {item.get('canonical_fact')}")
    lines.extend(["", "## Top Episodic Events", ""])
    for item in episodic[:2]:
        lines.append(f"- {item.get('event_summary')}")
    lines.extend(["", "## Top Procedures", ""])
    for item in procedural[:1]:
        lines.append(f"- {item.get('procedure_title')}: {item.get('trigger')}")
    return "\n".join(lines) + "\n"


def write_report(results: dict[str, dict]) -> Path:
    REPORTS_ROOT.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_ROOT / "compaction-report.md"
    lines = [
        "# Memory Compaction Report",
        "",
        f"- generated_at: {datetime.now(UTC).isoformat()}",
        "",
    ]
    for memory_type, result in results.items():
        lines.extend(
            [
                f"## {memory_type}",
                "",
                f"- before: {result['before']}",
                f"- after: {result['after']}",
                f"- deduplicated: {result['deduplicated']}",
                "",
            ]
        )
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def main() -> int:
    run = ScriptRun(ROOT, "memory-compact")
    started = time.perf_counter()
    run.event("info", "memory compaction started")
    if len(sys.argv) != 1:
        print("Usage: python3 scripts/agentcodex.py memory-compact")
        return 1

    results: dict[str, dict] = {}
    compacted: dict[str, list[dict]] = {}
    for memory_type in memory.SNAPSHOT_PATHS:
        items = BACKEND.load(memory_type)
        deduped, dedup_count = deduplicate(items, memory_type)
        compacted[memory_type] = deduped
        results[memory_type] = {
            "before": len(items),
            "after": len(deduped),
            "deduplicated": dedup_count,
        }

    summary_text = build_summary(compacted["semantic"], compacted["episodic"], compacted["procedural"])
    index_payload = {
        "version": "0.1.0",
        "generated_for": "phase-9-compaction",
        "generated_at": datetime.now(UTC).isoformat(),
        "sources": [
            str(SUMMARY_PATH.relative_to(ROOT)),
            *[str(path.relative_to(ROOT)) for path in BACKEND.snapshot_paths().values()],
        ],
        "limits": memory.LIMITS,
        "counts": {memory_type: len(items) for memory_type, items in compacted.items()},
        "backend": BACKEND.backend_id,
    }
    BACKEND.compact(compacted, summary_text, index_payload)

    report_path = write_report(results)
    dedup_count = sum(item["deduplicated"] for item in results.values())
    run.event("info", "memory compaction completed", dedup_count=dedup_count, report_path=str(report_path.relative_to(ROOT)))
    metrics = {
        "retrieval_count": 0,
        "memory_hit_rate": 0.0,
        "write_count": 0,
        "dedup_count": dedup_count,
        "compaction_events": 1,
        "retention_actions": 0,
        "access_denials": 0,
        "latency_ms": round((time.perf_counter() - started) * 1000, 2),
        "backend_failures": 0,
        "active_backend": BACKEND.backend_id,
    }
    for key, value in metrics.items():
        run.metric(key, value)
    run.finalize("success", {"report_path": str(report_path.relative_to(ROOT))})
    update_memory_metrics("memory-compact", metrics, "success")
    print(f"Memory compaction complete. Report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
