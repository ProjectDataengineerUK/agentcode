#!/usr/bin/env python3
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from memory_backend import get_backend


ROOT = Path(__file__).resolve().parent.parent
MEMORY_ROOT = ROOT / ".agentcodex" / "memory"

DECAY_DAYS = {
    "semantic": None,
    "episodic": 14.0,
    "procedural": None,
}

STALE_THRESHOLDS = {
    "episodic": 0.30,
}


@dataclass(frozen=True)
class MemoryLintIssue:
    severity: str
    check: str
    memory_id: str
    message: str


def parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def compute_decayed_confidence(item: dict, now: datetime | None = None) -> float:
    memory_type = str(item.get("memory_type", ""))
    decay_days = DECAY_DAYS.get(memory_type)
    confidence = float(item.get("confidence", 1.0))
    if decay_days is None:
        return confidence
    created_at = parse_iso(item.get("created_at")) or parse_iso(item.get("timestamp"))
    if created_at is None:
        return confidence
    now = now or datetime.now(UTC)
    elapsed_days = max((now - created_at).total_seconds() / 86400.0, 0.0)
    if elapsed_days <= 0:
        return confidence
    rate = -math.log(0.1) / decay_days
    decayed = confidence * math.exp(-rate * elapsed_days)
    return max(0.0, min(1.0, decayed))


def load_all_memories() -> dict[str, list[dict]]:
    backend = get_backend()
    return {
        "semantic": backend.load("semantic"),
        "episodic": backend.load("episodic"),
        "procedural": backend.load("procedural"),
    }


def lint_memories(now: datetime | None = None) -> tuple[list[MemoryLintIssue], dict[str, int]]:
    now = now or datetime.now(UTC)
    grouped = load_all_memories()
    issues: list[MemoryLintIssue] = []
    stats = {
        "total_memories": 0,
        "semantic": len(grouped["semantic"]),
        "episodic": len(grouped["episodic"]),
        "procedural": len(grouped["procedural"]),
    }
    seen_ids: set[str] = set()
    seen_summaries: dict[str, str] = {}

    for memory_type, items in grouped.items():
        stats["total_memories"] += len(items)
        for item in items:
            memory_id = str(item.get("memory_id", "missing-id"))
            if memory_id in seen_ids:
                issues.append(MemoryLintIssue("error", "duplicate_id", memory_id, "duplicate memory_id across snapshots"))
            seen_ids.add(memory_id)

            if memory_type == "semantic":
                summary_key = str(item.get("canonical_fact", "")).strip().casefold()
            elif memory_type == "episodic":
                summary_key = str(item.get("event_summary", "")).strip().casefold()
            else:
                summary_key = str(item.get("trigger", "")).strip().casefold()
            if summary_key:
                if summary_key in seen_summaries:
                    issues.append(
                        MemoryLintIssue(
                            "warning",
                            "duplicate_summary",
                            memory_id,
                            f"duplicates semantic/summary signal from {seen_summaries[summary_key]}",
                        )
                    )
                else:
                    seen_summaries[summary_key] = memory_id

            tags = item.get("tags", [])
            if not isinstance(tags, list) or not all(isinstance(tag, str) for tag in tags):
                issues.append(MemoryLintIssue("warning", "tag_hygiene", memory_id, "tags should be a list of strings"))
            if "owner" not in item or not item.get("owner"):
                issues.append(MemoryLintIssue("error", "missing_owner", memory_id, "owner is required"))

            if memory_type == "episodic":
                decayed = compute_decayed_confidence(item, now)
                if decayed < STALE_THRESHOLDS["episodic"]:
                    issues.append(
                        MemoryLintIssue(
                            "warning",
                            "stale_episodic",
                            memory_id,
                            f"episodic confidence decayed to {decayed:.3f}",
                        )
                    )

    return issues, stats


def extract_seed_memories() -> list[dict]:
    seeds: list[dict] = []
    status_path = ROOT / "docs" / "STATUS.md"
    handoff_path = ROOT / "docs" / "SESSION-HANDOFF.md"
    if status_path.exists():
        seeds.append(
            {
                "memory_type": "semantic",
                "scope": {"type": "project", "value": "agentcodex"},
                "subject": "repo-status-snapshot",
                "canonical_fact": "AgentCodex maintains a repo-local status snapshot and fixed status command surface.",
                "supporting_context": "See docs/STATUS.md and agentcodex status for current operational state.",
                "confidence": 0.88,
                "source": "repo-docs",
                "created_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                "updated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                "tags": ["memory", "status", "operations"],
                "sensitivity": "internal",
                "retention_policy": "semantic-default",
                "owner": "agentcodex",
            }
        )
    if handoff_path.exists():
        seeds.append(
            {
                "memory_type": "episodic",
                "scope": {"type": "project", "value": "agentcodex"},
                "event_title": "Session handoff updated",
                "event_summary": "The working session was consolidated into repo-local handoff and history artifacts for resumable execution.",
                "actors": ["agentcodex", "codex"],
                "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                "outcome": "Resume state became auditable by files instead of hidden chat state.",
                "references": ["docs/SESSION-HANDOFF.md", ".agentcodex/history/SESSION_2026-04-22_AGENT_PORT_AND_CONTEXT_RUNTIME.md"],
                "importance": 0.76,
                "tags": ["memory", "handoff", "resume"],
                "sensitivity": "internal",
                "retention_policy": "episodic-default",
                "owner": "agentcodex",
            }
        )
    return seeds
