from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
OBS_ROOT = ROOT / ".agentcodex" / "observability"
MEMORY_METRICS_PATH = OBS_ROOT / "metrics" / "memory-health.json"
MEMORY_FAILURES_PATH = OBS_ROOT / "failures" / "memory-failures.json"


def update_memory_metrics(script_name: str, metrics: dict[str, object], status: str) -> None:
    MEMORY_METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, object] = {}
    if MEMORY_METRICS_PATH.exists():
        try:
            payload = json.loads(MEMORY_METRICS_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            payload = {}

    last_runs = payload.get("last_runs", [])
    if not isinstance(last_runs, list):
        last_runs = []
    last_runs.append(
        {
            "script": script_name,
            "status": status,
            "metrics": metrics,
            "finished_at": datetime.now(UTC).isoformat(),
        }
    )
    payload["last_runs"] = last_runs[-30:]
    script_metrics = payload.get("script_metrics", {})
    if not isinstance(script_metrics, dict):
        script_metrics = {}
    script_metrics[script_name] = metrics
    payload["script_metrics"] = script_metrics
    payload["updated_at"] = datetime.now(UTC).isoformat()
    MEMORY_METRICS_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def record_memory_failure(script_name: str, reason: str, stage: str) -> None:
    MEMORY_FAILURES_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload: list[dict[str, str]] = []
    if MEMORY_FAILURES_PATH.exists():
        try:
            payload = json.loads(MEMORY_FAILURES_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            payload = []
    payload.append(
        {
            "script": script_name,
            "reason": reason,
            "stage": stage,
            "observed_at": datetime.now(UTC).isoformat(),
        }
    )
    MEMORY_FAILURES_PATH.write_text(json.dumps(payload[-50:], indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
