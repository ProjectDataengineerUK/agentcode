#!/usr/bin/env python3
from __future__ import annotations

import json
import hashlib
from datetime import UTC, datetime
from pathlib import Path

from memory_backend import get_backend
import memory_ingest as ingest


ROOT = Path(__file__).resolve().parent.parent
CANDIDATES_ROOT = ROOT / ".agentcodex" / "memory" / "candidates"
REVIEWS_ROOT = ROOT / ".agentcodex" / "memory" / "reviews"
REPORTS_ROOT = ROOT / ".agentcodex" / "reports" / "memory"
CANDIDATE_PREFIXES = ("memory-extract-", "log-knowledge-extract-")
KB_UPDATE_ROOT = ROOT / ".agentcodex" / "kb" / "update-candidates"
ALLOWED_CANDIDATE_ROOTS = (CANDIDATES_ROOT,)
ALLOWED_REVIEW_ROOTS = (REVIEWS_ROOT,)


def latest_candidates_file() -> Path:
    candidates: list[Path] = []
    for prefix in CANDIDATE_PREFIXES:
        candidates.extend(CANDIDATES_ROOT.glob(f"{prefix}*.json"))
    candidates = sorted(candidates, key=lambda path: path.stat().st_mtime)
    if not candidates:
        raise FileNotFoundError("No memory candidate file found")
    return candidates[-1]


def ensure_within_allowed_roots(path: Path, allowed_roots: tuple[Path, ...], label: str) -> Path:
    resolved = path.resolve()
    for root in allowed_roots:
        try:
            resolved.relative_to(root.resolve())
            return resolved
        except ValueError:
            continue
    allowed_display = ", ".join(str(root.relative_to(ROOT)) for root in allowed_roots)
    raise ValueError(f"{label} must stay within approved roots: {allowed_display}")


def load_candidates(path: Path | None = None) -> tuple[Path, list[dict]]:
    resolved = path or latest_candidates_file()
    resolved = ensure_within_allowed_roots(resolved, ALLOWED_CANDIDATE_ROOTS, "candidate file")
    payload = json.loads(resolved.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"Candidate file must be a JSON array: {resolved}")
    return resolved, payload


def review_path_for(candidate_path: Path) -> Path:
    REVIEWS_ROOT.mkdir(parents=True, exist_ok=True)
    stem = candidate_path.stem
    stem = stem.replace("memory-extract-", "memory-review-")
    stem = stem.replace("log-knowledge-extract-", "memory-review-logs-")
    try:
        candidate_path.relative_to(ROOT)
    except ValueError:
        suffix = hashlib.sha1(str(candidate_path).encode("utf-8")).hexdigest()[:8]
        stem = f"{stem}-{suffix}"
    return REVIEWS_ROOT / f"{stem}.json"


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def build_review(candidate_path: Path, candidates: list[dict]) -> tuple[Path, dict]:
    review_path = review_path_for(candidate_path)
    items = []
    for index, candidate in enumerate(candidates, start=1):
        summary = (
            candidate.get("canonical_fact")
            or candidate.get("event_summary")
            or candidate.get("trigger")
            or candidate.get("subject")
            or candidate.get("event_title")
            or "candidate"
        )
        items.append(
            {
                "candidate_id": f"{candidate_path.stem}:{index}",
                "decision": "pending",
                "memory_type": candidate.get("memory_type"),
                "summary": summary,
                "reason": "",
                "candidate": candidate,
            }
        )
    payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "source_candidates": display_path(candidate_path),
        "items": items,
    }
    review_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return review_path, payload


def load_review(path: Path) -> dict:
    path = ensure_within_allowed_roots(path, ALLOWED_REVIEW_ROOTS, "review file")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("items"), list):
        raise ValueError(f"Invalid review file: {path}")
    return payload


def approve_all(path: Path) -> dict:
    payload = load_review(path)
    changed = 0
    for item in payload["items"]:
        if item.get("decision") == "pending":
            item["decision"] = "approved"
            item["reason"] = item.get("reason") or "approved-by-default-flow"
            changed += 1
    payload["updated_at"] = datetime.now(UTC).isoformat()
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    payload["changed"] = changed
    return payload


def normalize_candidate(candidate: dict, candidate_id: str) -> dict:
    memory_type = str(candidate["memory_type"])
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")

    if memory_type == "semantic":
        return {
            "memory_id": candidate.get("memory_id") or candidate_id.replace(":", "-"),
            "memory_type": "semantic",
            "scope": candidate.get("scope", {"type": "project", "value": "agentcodex"}),
            "subject": candidate.get("subject") or candidate.get("canonical_fact", "memory-candidate"),
            "canonical_fact": candidate.get("canonical_fact") or candidate.get("summary") or candidate.get("subject", ""),
            "supporting_context": candidate.get("supporting_context") or candidate.get("content", ""),
            "confidence": candidate.get("confidence", 0.8),
            "source": candidate.get("source", "memory-candidate-review"),
            "created_at": candidate.get("created_at", now),
            "updated_at": candidate.get("updated_at", now),
            "tags": candidate.get("tags", ["memory", "candidate"]),
            "sensitivity": candidate.get("sensitivity", "internal"),
            "retention_policy": candidate.get("retention_policy", "semantic-default"),
            "owner": candidate.get("owner", "agentcodex"),
        }

    if memory_type == "episodic":
        return {
            "memory_id": candidate.get("memory_id") or candidate_id.replace(":", "-"),
            "memory_type": "episodic",
            "scope": candidate.get("scope", {"type": "project", "value": "agentcodex"}),
            "event_title": candidate.get("event_title") or candidate.get("summary") or "Memory candidate event",
            "event_summary": candidate.get("event_summary") or candidate.get("content") or candidate.get("summary", ""),
            "actors": candidate.get("actors", ["agentcodex"]),
            "timestamp": candidate.get("timestamp", now),
            "outcome": candidate.get("outcome", "Candidate reviewed and approved for ingestion."),
            "references": candidate.get("references", []),
            "source": candidate.get("source", "observability-log-review"),
            "importance": candidate.get("importance", 0.7),
            "tags": candidate.get("tags", ["memory", "candidate"]),
            "sensitivity": candidate.get("sensitivity", "internal"),
            "retention_policy": candidate.get("retention_policy", "episodic-default"),
            "owner": candidate.get("owner", "agentcodex"),
        }

    if memory_type == "procedural":
        return {
            "memory_id": candidate.get("memory_id") or candidate_id.replace(":", "-"),
            "memory_type": "procedural",
            "scope": candidate.get("scope", {"type": "project", "value": "agentcodex"}),
            "procedure_title": candidate.get("procedure_title") or candidate.get("summary") or "Memory candidate procedure",
            "trigger": candidate.get("trigger") or candidate.get("summary") or "approved memory candidate",
            "steps": candidate.get("steps", []),
            "constraints": candidate.get("constraints", []),
            "success_signals": candidate.get("success_signals", []),
            "failure_signals": candidate.get("failure_signals", []),
            "source": candidate.get("source", "memory-candidate-review"),
            "approval_state": candidate.get("approval_state", "approved"),
            "updated_at": candidate.get("updated_at", now),
            "tags": candidate.get("tags", ["memory", "candidate"]),
            "owner": candidate.get("owner", "agentcodex"),
        }

    raise ValueError(f"Unsupported memory_type: {memory_type}")


def ingest_approved(path: Path) -> tuple[dict, list[str]]:
    payload = load_review(path)
    backend = get_backend()
    ingested_ids: list[str] = []
    for item in payload["items"]:
        if item.get("decision") != "approved":
            continue
        candidate = item["candidate"]
        memory_type = str(candidate["memory_type"])
        snapshot = backend.load(memory_type)
        normalized = normalize_candidate(candidate, item["candidate_id"])
        for existing in snapshot:
            if existing.get("memory_id") == normalized.get("memory_id"):
                break
        else:
            synthetic_id = normalized["memory_id"]
            errors = ingest.validate_item(normalized, memory_type)
            if errors:
                item["decision"] = "rejected"
                item["reason"] = "; ".join(errors)
                continue
            item["normalized_candidate"] = normalized
            snapshot.append(normalized)
            backend.upsert(memory_type, snapshot)
            ingested_ids.append(synthetic_id)
    payload["updated_at"] = datetime.now(UTC).isoformat()
    payload["ingested_ids"] = ingested_ids
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload, ingested_ids


def build_kb_update_candidates(path: Path) -> tuple[list[dict], Path]:
    payload = load_review(path)
    KB_UPDATE_ROOT.mkdir(parents=True, exist_ok=True)
    updates: list[dict] = []
    for item in payload["items"]:
        if item.get("decision") != "approved":
            continue
        candidate = item.get("candidate", {})
        references = candidate.get("references", [])
        tags = candidate.get("tags", [])
        if "logs" not in tags and "sentinel" not in tags:
            continue
        summary = (
            candidate.get("event_summary")
            or candidate.get("canonical_fact")
            or candidate.get("trigger")
            or item.get("summary")
            or "Operational knowledge candidate"
        )
        updates.append(
            {
                "candidate_id": item["candidate_id"],
                "title": f"KB update from {item['candidate_id']}",
                "purpose": "Capture stable operational knowledge derived from reviewed Sentinel or observability logs.",
                "suggested_domain": "observability",
                "suggested_path": ".agentcodex/kb/operations/observability/",
                "summary": summary,
                "source_review": display_path(path),
                "references": references,
                "tags": tags,
                "status": "proposed",
                "review_required": True,
            }
        )
    output_path = KB_UPDATE_ROOT / f"{path.stem}.json"
    output_path.write_text(json.dumps({"generated_from": display_path(path), "items": updates}, indent=2) + "\n", encoding="utf-8")
    return updates, output_path


def write_report(name: str, lines: list[str]) -> Path:
    REPORTS_ROOT.mkdir(parents=True, exist_ok=True)
    path = REPORTS_ROOT / name
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
