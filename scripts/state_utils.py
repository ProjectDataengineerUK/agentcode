#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


EVIDENCE_LEVELS = ("none", "local-pass", "ci-pass", "deploy-pass", "runtime-pass")


def now_iso() -> str:
    return datetime.now(UTC).isoformat()


def resolve_root(target_arg: str | None = None) -> Path:
    if target_arg:
        return Path(target_arg).resolve()
    return Path.cwd().resolve()


def state_root(root: Path) -> Path:
    return root / ".agentcodex" / "state"


def reports_root(root: Path) -> Path:
    return root / ".agentcodex" / "reports"


def ensure_agentcodex_dirs(root: Path) -> None:
    (root / ".agentcodex").mkdir(parents=True, exist_ok=True)
    state_root(root).mkdir(parents=True, exist_ok=True)
    reports_root(root).mkdir(parents=True, exist_ok=True)


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def project_state_path(root: Path) -> Path:
    return state_root(root) / "project-state.json"


def approval_gates_path(root: Path) -> Path:
    return state_root(root) / "approval-gates.json"


def load_project_state(root: Path) -> dict[str, Any]:
    return read_json(
        project_state_path(root),
        {
            "updated_at": "",
            "architecture": {},
            "evidence": {},
            "reconciliation": {},
            "preflight": {},
            "history": [],
        },
    )


def save_project_state(root: Path, state: dict[str, Any]) -> Path:
    state["updated_at"] = now_iso()
    path = project_state_path(root)
    write_json(path, state)
    return path


def load_approval_gates(root: Path) -> dict[str, Any]:
    return read_json(
        approval_gates_path(root),
        {
            "updated_at": "",
            "gates": {},
        },
    )


def save_approval_gates(root: Path, payload: dict[str, Any]) -> Path:
    payload["updated_at"] = now_iso()
    path = approval_gates_path(root)
    write_json(path, payload)
    return path


def evidence_rank(level: str) -> int:
    try:
        return EVIDENCE_LEVELS.index(level)
    except ValueError:
        return 0


def max_evidence(values: list[str]) -> str:
    if not values:
        return "none"
    return max(values, key=evidence_rank)


def latest_matching(root: Path, pattern: str) -> Path | None:
    matches = sorted((root).glob(pattern), key=lambda item: item.stat().st_mtime)
    return matches[-1] if matches else None
