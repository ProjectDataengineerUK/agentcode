from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path


@dataclass
class ScriptRun:
    root: Path
    script_name: str
    started_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    events: list[dict] = field(default_factory=list)
    metrics: dict[str, object] = field(default_factory=dict)
    source_failures: list[dict[str, str]] = field(default_factory=list)
    status: str = "running"

    def __post_init__(self) -> None:
        self.obs_root = self.root / ".agentcodex" / "observability"
        self.logs_root = self.obs_root / "logs"
        self.runs_root = self.obs_root / "runs"
        self.failures_root = self.obs_root / "failures"
        self.metrics_root = self.obs_root / "metrics"
        self.integrations_root = self.obs_root / "integrations"
        for directory in (
            self.logs_root,
            self.runs_root,
            self.failures_root,
            self.metrics_root,
            self.integrations_root,
        ):
            directory.mkdir(parents=True, exist_ok=True)
        self.run_id = f"{self.script_name}-{self.started_at.replace(':', '-').replace('+00:00', 'Z')}"
        self.log_path = self.logs_root / f"{self.script_name}.jsonl"
        self.run_path = self.runs_root / f"{self.run_id}.json"
        self.failures_path = self.failures_root / "source-failures.json"
        self.metrics_path = self.metrics_root / "kb-health.json"
        self.integration_markers_path = self.integrations_root / "targets.json"

    def event(self, level: str, message: str, **fields: object) -> None:
        payload = {
            "timestamp": datetime.now(UTC).isoformat(),
            "script": self.script_name,
            "run_id": self.run_id,
            "level": level,
            "message": message,
        }
        payload.update(fields)
        self.events.append(payload)
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=True) + "\n")

    def metric(self, key: str, value: object) -> None:
        self.metrics[key] = value

    def record_source_failure(self, source_id: str, reason: str, stage: str) -> None:
        item = {
            "source_id": source_id,
            "reason": reason,
            "stage": stage,
            "observed_at": datetime.now(UTC).isoformat(),
            "run_id": self.run_id,
            "script": self.script_name,
        }
        self.source_failures.append(item)

    def finalize(self, status: str, summary: dict[str, object] | None = None) -> None:
        self.status = status
        finished_at = datetime.now(UTC).isoformat()
        run_payload = {
            "run_id": self.run_id,
            "script": self.script_name,
            "started_at": self.started_at,
            "finished_at": finished_at,
            "status": status,
            "metrics": self.metrics,
            "summary": summary or {},
            "event_count": len(self.events),
        }
        self.run_path.write_text(json.dumps(run_payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
        self._persist_source_failures()
        self._persist_metrics(run_payload)
        self._persist_integration_markers()

    def _persist_source_failures(self) -> None:
        existing: list[dict[str, str]] = []
        if self.failures_path.exists():
            try:
                existing = json.loads(self.failures_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                existing = []
        trimmed = [item for item in existing if item.get("source_id") not in {f["source_id"] for f in self.source_failures}]
        trimmed.extend(self.source_failures)
        self.failures_path.write_text(json.dumps(trimmed, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    def _persist_metrics(self, run_payload: dict[str, object]) -> None:
        existing: dict[str, object] = {}
        if self.metrics_path.exists():
            try:
                existing = json.loads(self.metrics_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                existing = {}
        history = existing.get("last_runs", [])
        if not isinstance(history, list):
            history = []
        history.append(
            {
                "run_id": run_payload["run_id"],
                "script": self.script_name,
                "status": run_payload["status"],
                "finished_at": run_payload["finished_at"],
            }
        )
        existing["last_runs"] = history[-20:]
        existing["updated_at"] = datetime.now(UTC).isoformat()
        script_metrics = existing.get("script_metrics", {})
        if not isinstance(script_metrics, dict):
            script_metrics = {}
        script_metrics[self.script_name] = {
            **self.metrics,
            "last_run_id": run_payload["run_id"],
            "last_status": run_payload["status"],
            "last_finished_at": run_payload["finished_at"],
        }
        existing["script_metrics"] = script_metrics
        aggregate_metrics = existing.get("metrics", {})
        if not isinstance(aggregate_metrics, dict):
            aggregate_metrics = {}
        aggregate_metrics[self.script_name] = {
            **self.metrics,
            "status": run_payload["status"],
            "finished_at": run_payload["finished_at"],
        }
        existing["metrics"] = aggregate_metrics
        self.metrics_path.write_text(json.dumps(existing, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    def _persist_integration_markers(self) -> None:
        payload = {
            "version": "0.1.0",
            "prepared_for": [
                "opentelemetry",
                "phoenix",
                "langfuse",
            ],
            "mode": "file-based-local-observability",
            "updated_at": datetime.now(UTC).isoformat(),
            "notes": "These markers describe intended future integration targets while current observability remains local and auditable by files."
        }
        self.integration_markers_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
