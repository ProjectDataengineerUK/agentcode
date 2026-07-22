#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import re
import sys
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS_ROOT = ROOT / ".agentcodex" / "workflows"
ARCHIVE_ROOT = ROOT / ".agentcodex" / "archive" / "workflows"
TEMPLATES_ROOT = ROOT / ".agentcodex" / "templates"
REPORTS_ROOT = ROOT / ".agentcodex" / "reports" / "workflows"

WORKFLOW_DEFINITIONS = {
    "wf-pipeline": {
        "name": "WF-PIPELINE",
        "template": "data-pipeline-spec.md",
        "keywords": ["pipeline completo", "end-to-end", "bronze", "gold", "medallion", "etl", "elt"],
        "stages": [
            {"id": "stage-01", "role": "pipeline-architect", "goal": "define pipeline architecture and source-to-target flow"},
            {"id": "stage-02", "role": "spark-engineer", "goal": "implement transformation and loading logic"},
            {"id": "stage-03", "role": "data-quality-analyst", "goal": "define and validate quality controls"},
            {"id": "stage-04", "role": "data-governance-architect", "goal": "review governance, controls, and evidence"},
        ],
    },
    "wf-star-schema": {
        "name": "WF-STAR-SCHEMA",
        "template": "star-schema-overview.md",
        "keywords": ["star schema", "camada gold", "gold layer", "dimensional", "fact", "dimension"],
        "stages": [
            {"id": "stage-01", "role": "schema-designer", "goal": "define grain, dimensions, and fact boundaries"},
            {"id": "stage-02", "role": "sql-optimizer", "goal": "shape ddl and join strategy"},
            {"id": "stage-03", "role": "data-quality-analyst", "goal": "validate key integrity and quality rules"},
        ],
    },
    "wf-cross-platform": {
        "name": "WF-CROSS-PLATFORM",
        "template": "cross-platform-operation.md",
        "keywords": ["cross-platform", "migrar", "migration", "databricks", "fabric", "snowflake", "sync entre"],
        "stages": [
            {"id": "stage-01", "role": "data-platform-engineer", "goal": "define movement strategy and platform boundaries"},
            {"id": "stage-02", "role": "databricks-architect", "goal": "shape Databricks-side constraints when relevant"},
            {"id": "stage-03", "role": "fabric-architect", "goal": "shape Fabric-side constraints when relevant"},
            {"id": "stage-04", "role": "data-governance-architect", "goal": "review governance, security, and auditability"},
        ],
    },
    "wf-backlog-to-define": {
        "name": "WF-BACKLOG-TO-DEFINE",
        "template": "business-backlog.md",
        "keywords": ["briefing", "meeting", "reunião", "backlog", "requisitos", "transcript"],
        "stages": [
            {"id": "stage-01", "role": "meeting-analyst", "goal": "extract decisions, stakeholders, and open questions"},
            {"id": "stage-02", "role": "workflow-definer", "goal": "convert backlog into implementation-ready definition"},
            {"id": "stage-03", "role": "planner", "goal": "sequence work and dependencies"},
        ],
    },
}

VALID_STATUSES = {"pending", "in_progress", "completed"}
VALID_WORKFLOW_STATUSES = {"active", "closed", "archived"}
SAFE_WORKFLOW_RUN_ID_RE = re.compile(r"^[a-zA-Z0-9._-]+$")


def now_iso() -> str:
    return datetime.now(UTC).isoformat()


def slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower())
    return value.strip("-") or "workflow"


def validate_workflow_run_id(workflow_run_id: str) -> str:
    if not workflow_run_id:
        raise ValueError("workflow_run_id cannot be empty")
    if not SAFE_WORKFLOW_RUN_ID_RE.fullmatch(workflow_run_id):
        raise ValueError(
            "Invalid workflow_run_id; only letters, numbers, dot, underscore, and hyphen are allowed"
        )
    if ".." in workflow_run_id or "/" in workflow_run_id or "\\" in workflow_run_id:
        raise ValueError("Invalid workflow_run_id; path separators and traversal markers are not allowed")
    if Path(workflow_run_id).is_absolute():
        raise ValueError("Invalid workflow_run_id; absolute paths are not allowed")
    return workflow_run_id


def ensure_within_root(root: Path, candidate: Path) -> Path:
    resolved_root = root.resolve()
    resolved_candidate = candidate.resolve()
    try:
        resolved_candidate.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError(f"Resolved path escapes managed root: {candidate}") from exc
    return resolved_candidate


def workflow_dir_for_root(root: Path, workflow_run_id: str) -> Path:
    workflow_run_id = validate_workflow_run_id(workflow_run_id)
    return ensure_within_root(root, root / workflow_run_id)


def workflow_exists(workflow_run_id: str) -> bool:
    active = workflow_dir_for_root(WORKFLOWS_ROOT, workflow_run_id)
    archived = workflow_dir_for_root(ARCHIVE_ROOT, workflow_run_id)
    return active.exists() or archived.exists()


def next_workflow_run_id(workflow_id: str, prompt: str) -> str:
    base_run_id = f"{workflow_id}-{slugify(prompt)[:48]}"
    if not workflow_exists(base_run_id):
        return base_run_id
    suffix = 2
    while True:
        candidate = f"{base_run_id}-{suffix}"
        if not workflow_exists(candidate):
            return candidate
        suffix += 1


def detect_workflow(prompt: str) -> tuple[str, dict]:
    prompt_l = prompt.casefold()
    scored: list[tuple[int, str, dict]] = []
    for workflow_id, definition in WORKFLOW_DEFINITIONS.items():
        score = sum(1 for keyword in definition["keywords"] if keyword in prompt_l)
        if score:
            scored.append((score, workflow_id, definition))
    if scored:
        scored.sort(reverse=True, key=lambda item: item[0])
        _, workflow_id, definition = scored[0]
        return workflow_id, definition
    return "wf-pipeline", WORKFLOW_DEFINITIONS["wf-pipeline"]


def build_handoffs(definition: dict, spec_path: str) -> list[dict]:
    stages = definition["stages"]
    handoffs = []
    for index, stage in enumerate(stages, start=1):
        previous = stages[index - 2]["role"] if index > 1 else "orchestrator"
        handoffs.append(
            {
                "stage_id": stage["id"],
                "from": previous,
                "to": stage["role"],
                "goal": stage["goal"],
                "handoff_note": f"Read spec `{spec_path}` and continue from the prior stage output.",
            }
        )
    return handoffs


def workflow_root_path(workflow_run_id: str) -> Path:
    active = workflow_dir_for_root(WORKFLOWS_ROOT, workflow_run_id)
    archived = workflow_dir_for_root(ARCHIVE_ROOT, workflow_run_id)
    if active.exists():
        return active
    if archived.exists():
        return archived
    return active


def workflow_state_path(workflow_run_id: str) -> Path:
    return workflow_root_path(workflow_run_id) / "state.json"


def load_state(workflow_run_id: str) -> dict:
    path = workflow_state_path(workflow_run_id)
    if not path.exists():
        raise FileNotFoundError(f"Workflow state not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def save_state(workflow_run_id: str, payload: dict) -> Path:
    path = workflow_state_path(workflow_run_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def summarize_progress(payload: dict) -> dict:
    counts = {status: 0 for status in VALID_STATUSES}
    current_stage = None
    next_stage = None
    for stage in payload["stages"]:
        counts[stage["status"]] = counts.get(stage["status"], 0) + 1
        if stage["status"] == "in_progress":
            current_stage = stage["id"]
        if next_stage is None and stage["status"] == "pending":
            next_stage = stage["id"]
    return {
        "pending": counts.get("pending", 0),
        "in_progress": counts.get("in_progress", 0),
        "completed": counts.get("completed", 0),
        "current_stage": current_stage,
        "next_stage": next_stage,
    }


def is_workflow_closed(payload: dict) -> bool:
    return payload.get("workflow_status", "active") in {"closed", "archived"}


def is_workflow_archived(payload: dict) -> bool:
    return payload.get("workflow_status") == "archived"


def require_mutable_workflow(payload: dict) -> bool:
    return not is_workflow_closed(payload)


def next_pending_stage(payload: dict) -> dict | None:
    for stage in payload["stages"]:
        if stage["status"] == "pending":
            return stage
    return None


def current_in_progress_stage(payload: dict) -> dict | None:
    for stage in payload["stages"]:
        if stage["status"] == "in_progress":
            return stage
    return None


def next_actionable_stage(payload: dict) -> dict | None:
    current = current_in_progress_stage(payload)
    if current is not None:
        return current
    return next_pending_stage(payload)


def ensure_stage_is_next_pending(payload: dict, stage_id: str) -> tuple[bool, str | None]:
    next_stage = next_pending_stage(payload)
    if next_stage is None:
        return False, "No pending stage available"
    if next_stage["id"] != stage_id:
        return False, f"Stage {stage_id} is out of order; next pending stage is {next_stage['id']}"
    return True, None


def ensure_stage_is_current(payload: dict, stage_id: str) -> tuple[bool, str | None]:
    current = current_in_progress_stage(payload)
    if current is None:
        return False, "No stage is currently in progress"
    if current["id"] != stage_id:
        return False, f"Stage {stage_id} is not current; current in-progress stage is {current['id']}"
    return True, None


def write_report(payload: dict) -> Path:
    REPORTS_ROOT.mkdir(parents=True, exist_ok=True)
    path = REPORTS_ROOT / f"{payload['workflow_run_id']}.md"
    progress = summarize_progress(payload)
    lines = [
        "# Workflow Orchestrator Report",
        "",
        f"- generated_at: {payload['generated_at']}",
        f"- updated_at: {payload.get('updated_at', payload['generated_at'])}",
        f"- workflow: {payload['workflow_name']}",
        f"- workflow_run_id: {payload['workflow_run_id']}",
        f"- workflow_status: {payload.get('workflow_status', 'active')}",
        f"- spec_template: {payload['spec_template']}",
        f"- spec_path: {payload['spec_path']}",
        f"- current_stage: {progress['current_stage'] or 'none'}",
        f"- next_stage: {progress['next_stage'] or 'none'}",
        "",
        "## Stages",
        "",
    ]
    for stage in payload["stages"]:
        lines.append(f"- {stage['id']}: `{stage['role']}` [{stage['status']}] -> {stage['goal']}")
    lines.extend(["", "## Handoffs", ""])
    for handoff in payload["handoffs"]:
        lines.append(f"- {handoff['from']} -> {handoff['to']}: {handoff['goal']}")
    if payload.get("events"):
        lines.extend(["", "## Events", ""])
        for event in payload["events"][-10:]:
            lines.append(f"- {event['at']}: `{event['event']}` on `{event['stage_id']}`")
    if payload.get("handoff_log"):
        lines.extend(["", "## Handoff Log", ""])
        for handoff in payload["handoff_log"][-10:]:
            lines.append(
                f"- {handoff['at']}: `{handoff['from_stage_id']}` -> `{handoff['to_stage_id']}`: {handoff['note']}"
            )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def make_payload(prompt: str, workflow_id: str, definition: dict, workflow_run_id: str, spec_path: Path) -> dict:
    return {
        "generated_at": now_iso(),
        "updated_at": now_iso(),
        "workflow_id": workflow_id,
        "workflow_name": definition["name"],
        "workflow_run_id": workflow_run_id,
        "prompt": prompt,
        "workflow_status": "active",
        "closed_at": None,
        "archived_at": None,
        "spec_template": definition["template"],
        "spec_path": str(spec_path.relative_to(ROOT)),
        "stages": [
            {
                "id": stage["id"],
                "role": stage["role"],
                "goal": stage["goal"],
                "status": "pending",
                "started_at": None,
                "completed_at": None,
                "notes": [],
            }
            for stage in definition["stages"]
        ],
        "handoffs": build_handoffs(definition, str(spec_path.relative_to(ROOT))),
        "handoff_log": [],
        "events": [],
    }


def print_usage() -> None:
    print("Usage:")
    print("  python3 scripts/agentcodex.py orchestrate-workflow <prompt> [--json]")
    print("  python3 scripts/agentcodex.py list-workflows [--json]")
    print("  python3 scripts/agentcodex.py workflow-status <workflow-run-id> [--json]")
    print("  python3 scripts/agentcodex.py resume-workflow <workflow-run-id> [--json]")
    print("  python3 scripts/agentcodex.py workflow-note <workflow-run-id> <stage-id> --note <text> [--json]")
    print("  python3 scripts/agentcodex.py workflow-handoff <workflow-run-id> <from-stage-id> <to-stage-id> --note <text> [--json]")
    print("  python3 scripts/agentcodex.py start-stage <workflow-run-id> <stage-id> [--note <text>] [--json]")
    print("  python3 scripts/agentcodex.py complete-stage <workflow-run-id> <stage-id> [--note <text>] [--json]")
    print("  python3 scripts/agentcodex.py advance-stage <workflow-run-id> <stage-id> [--note <text>] [--json]")
    print("  python3 scripts/agentcodex.py workflow-next <workflow-run-id> [--note <text>] [--json]")
    print("  python3 scripts/agentcodex.py workflow-close <workflow-run-id> [--note <text>] [--json]")
    print("  python3 scripts/agentcodex.py workflow-archive <workflow-run-id> [--note <text>] [--json]")


def render_payload(payload: dict, as_json: bool) -> int:
    progress = summarize_progress(payload)
    state_path = workflow_state_path(payload["workflow_run_id"])
    report_path = REPORTS_ROOT / f"{payload['workflow_run_id']}.md"
    output = dict(payload)
    output["state_path"] = str(state_path.relative_to(ROOT))
    output["report_path"] = str(report_path.relative_to(ROOT))
    output["progress"] = progress
    if as_json:
        print(json.dumps(output, indent=2))
        return 0
    print("# Workflow Orchestrator")
    print()
    print(f"- workflow: {payload['workflow_name']}")
    print(f"- workflow_run_id: {payload['workflow_run_id']}")
    print(f"- workflow_status: {payload.get('workflow_status', 'active')}")
    print(f"- spec_path: {payload['spec_path']}")
    print(f"- state_path: {output['state_path']}")
    print(f"- report_path: {output['report_path']}")
    print(f"- current_stage: {progress['current_stage'] or 'none'}")
    print(f"- next_stage: {progress['next_stage'] or 'none'}")
    print("## Stages")
    for stage in payload["stages"]:
        print(f"- {stage['id']}: `{stage['role']}` [{stage['status']}] -> {stage['goal']}")
    return 0


def create_workflow(prompt: str, as_json: bool) -> int:
    workflow_id, definition = detect_workflow(prompt)
    workflow_run_id = next_workflow_run_id(workflow_id, prompt)
    workflow_root = workflow_dir_for_root(WORKFLOWS_ROOT, workflow_run_id)
    workflow_root.mkdir(parents=True, exist_ok=True)
    spec_template = definition["template"]
    spec_path = workflow_root / spec_template
    if not spec_path.exists():
        spec_path.write_text((TEMPLATES_ROOT / spec_template).read_text(encoding="utf-8"), encoding="utf-8")
    payload = make_payload(prompt, workflow_id, definition, workflow_run_id, spec_path)
    save_state(workflow_run_id, payload)
    write_report(payload)
    return render_payload(payload, as_json)


def list_workflows(as_json: bool) -> int:
    items = []
    state_paths: list[Path] = []
    if WORKFLOWS_ROOT.exists():
        state_paths.extend(WORKFLOWS_ROOT.glob("*/state.json"))
    if ARCHIVE_ROOT.exists():
        state_paths.extend(ARCHIVE_ROOT.glob("*/state.json"))
    if state_paths:
        for state_path in sorted(state_paths, reverse=True):
            payload = json.loads(state_path.read_text(encoding="utf-8"))
            progress = summarize_progress(payload)
            items.append(
                {
                    "workflow_run_id": payload["workflow_run_id"],
                    "workflow_name": payload["workflow_name"],
                    "workflow_id": payload["workflow_id"],
                    "workflow_status": payload.get("workflow_status", "active"),
                    "updated_at": payload.get("updated_at", payload["generated_at"]),
                    "current_stage": progress["current_stage"],
                    "next_stage": progress["next_stage"],
                    "completed": progress["completed"],
                    "in_progress": progress["in_progress"],
                    "pending": progress["pending"],
                    "state_path": str(state_path.relative_to(ROOT)),
                }
            )
    if as_json:
        print(json.dumps({"workflows": items}, indent=2))
        return 0
    print("# Workflows")
    print()
    if not items:
        print("- none")
        return 0
    for item in items:
        print(
            f"- {item['workflow_run_id']}: `{item['workflow_name']}` "
            f"[status={item['workflow_status']} current={item['current_stage'] or 'none'} next={item['next_stage'] or 'none'} "
            f"completed={item['completed']} in_progress={item['in_progress']} pending={item['pending']}]"
        )
    return 0


def find_stage(payload: dict, stage_id: str) -> dict | None:
    for stage in payload["stages"]:
        if stage["id"] == stage_id:
            return stage
    return None


def add_event(payload: dict, event_name: str, stage_id: str, note: str | None) -> None:
    payload.setdefault("events", []).append(
        {
            "event": event_name,
            "stage_id": stage_id,
            "note": note or "",
            "at": now_iso(),
        }
    )
    payload["updated_at"] = now_iso()


def rewrite_spec_references(payload: dict, workflow_root: Path) -> None:
    spec_path = workflow_root / payload["spec_template"]
    payload["spec_path"] = str(spec_path.relative_to(ROOT))
    for handoff in payload.get("handoffs", []):
        handoff["handoff_note"] = f"Read spec `{payload['spec_path']}` and continue from the prior stage output."


def close_workflow_payload(payload: dict, note: str | None) -> None:
    payload["workflow_status"] = "closed"
    payload["closed_at"] = payload.get("closed_at") or now_iso()
    payload["updated_at"] = now_iso()
    add_event(payload, "workflow-close", "workflow", note)


def archive_workflow_payload(payload: dict, note: str | None) -> None:
    payload["workflow_status"] = "archived"
    payload["closed_at"] = payload.get("closed_at") or now_iso()
    payload["archived_at"] = payload.get("archived_at") or now_iso()
    payload["updated_at"] = now_iso()
    add_event(payload, "workflow-archive", "workflow", note)


def add_handoff(payload: dict, from_stage_id: str, to_stage_id: str, note: str) -> None:
    payload.setdefault("handoff_log", []).append(
        {
            "from_stage_id": from_stage_id,
            "to_stage_id": to_stage_id,
            "note": note,
            "at": now_iso(),
        }
    )
    payload["updated_at"] = now_iso()


def resume_workflow(workflow_run_id: str, as_json: bool) -> int:
    payload = load_state(workflow_run_id)
    write_report(payload)
    return render_payload(payload, as_json)


def workflow_note(workflow_run_id: str, stage_id: str, note: str | None, as_json: bool) -> int:
    if not note:
        print("workflow-note requires --note <text>", file=sys.stderr)
        return 1
    payload = load_state(workflow_run_id)
    if not require_mutable_workflow(payload):
        print(f"Workflow is not mutable: {payload.get('workflow_status', 'active')}", file=sys.stderr)
        return 1
    stage = find_stage(payload, stage_id)
    if stage is None:
        print(f"Unknown stage: {stage_id}", file=sys.stderr)
        return 1
    stage.setdefault("notes", []).append(note)
    add_event(payload, "workflow-note", stage_id, note)
    save_state(workflow_run_id, payload)
    write_report(payload)
    return render_payload(payload, as_json)


def workflow_handoff(
    workflow_run_id: str,
    from_stage_id: str,
    to_stage_id: str,
    note: str | None,
    as_json: bool,
) -> int:
    if not note:
        print("workflow-handoff requires --note <text>", file=sys.stderr)
        return 1
    payload = load_state(workflow_run_id)
    if not require_mutable_workflow(payload):
        print(f"Workflow is not mutable: {payload.get('workflow_status', 'active')}", file=sys.stderr)
        return 1
    from_stage = find_stage(payload, from_stage_id)
    to_stage = find_stage(payload, to_stage_id)
    if from_stage is None:
        print(f"Unknown stage: {from_stage_id}", file=sys.stderr)
        return 1
    if to_stage is None:
        print(f"Unknown stage: {to_stage_id}", file=sys.stderr)
        return 1
    add_handoff(payload, from_stage_id, to_stage_id, note)
    add_event(payload, "workflow-handoff", from_stage_id, note)
    save_state(workflow_run_id, payload)
    write_report(payload)
    return render_payload(payload, as_json)


def start_stage(workflow_run_id: str, stage_id: str, note: str | None, as_json: bool) -> int:
    payload = load_state(workflow_run_id)
    if not require_mutable_workflow(payload):
        print(f"Workflow is not mutable: {payload.get('workflow_status', 'active')}", file=sys.stderr)
        return 1
    stage = find_stage(payload, stage_id)
    if stage is None:
        print(f"Unknown stage: {stage_id}", file=sys.stderr)
        return 1
    current = current_in_progress_stage(payload)
    if current is not None and current["id"] != stage_id:
        print(f"Another stage is already in progress: {current['id']}", file=sys.stderr)
        return 1
    if stage["status"] == "completed":
        print(f"Stage already completed: {stage_id}", file=sys.stderr)
        return 1
    if stage["status"] == "pending":
        ok, error = ensure_stage_is_next_pending(payload, stage_id)
        if not ok:
            print(error, file=sys.stderr)
            return 1
    stage["status"] = "in_progress"
    stage["started_at"] = stage.get("started_at") or now_iso()
    if note:
        stage.setdefault("notes", []).append(note)
    add_event(payload, "start-stage", stage_id, note)
    save_state(workflow_run_id, payload)
    write_report(payload)
    return render_payload(payload, as_json)


def complete_stage(workflow_run_id: str, stage_id: str, note: str | None, as_json: bool) -> int:
    payload = load_state(workflow_run_id)
    if not require_mutable_workflow(payload):
        print(f"Workflow is not mutable: {payload.get('workflow_status', 'active')}", file=sys.stderr)
        return 1
    stage = find_stage(payload, stage_id)
    if stage is None:
        print(f"Unknown stage: {stage_id}", file=sys.stderr)
        return 1
    if stage["status"] == "completed":
        print(f"Stage already completed: {stage_id}", file=sys.stderr)
        return 1
    ok, error = ensure_stage_is_current(payload, stage_id)
    if not ok:
        print(error, file=sys.stderr)
        return 1
    stage["status"] = "completed"
    stage["started_at"] = stage.get("started_at") or now_iso()
    stage["completed_at"] = now_iso()
    if note:
        stage.setdefault("notes", []).append(note)
    add_event(payload, "complete-stage", stage_id, note)
    save_state(workflow_run_id, payload)
    write_report(payload)
    return render_payload(payload, as_json)


def advance_stage(workflow_run_id: str, stage_id: str, note: str | None, as_json: bool) -> int:
    payload = load_state(workflow_run_id)
    if not require_mutable_workflow(payload):
        print(f"Workflow is not mutable: {payload.get('workflow_status', 'active')}", file=sys.stderr)
        return 1
    stage = find_stage(payload, stage_id)
    if stage is None:
        print(f"Unknown stage: {stage_id}", file=sys.stderr)
        return 1
    if stage["status"] == "completed":
        print(f"Stage already completed: {stage_id}", file=sys.stderr)
        return 1
    current = current_in_progress_stage(payload)
    if current is not None and current["id"] != stage_id:
        print(f"Stage {stage_id} is not current; current in-progress stage is {current['id']}", file=sys.stderr)
        return 1
    if current is None:
        ok, error = ensure_stage_is_next_pending(payload, stage_id)
        if not ok:
            print(error, file=sys.stderr)
            return 1

    stage["status"] = "completed"
    stage["started_at"] = stage.get("started_at") or now_iso()
    stage["completed_at"] = now_iso()
    if note:
        stage.setdefault("notes", []).append(note)
    add_event(payload, "advance-stage", stage_id, note)

    next_stage = next_pending_stage(payload)
    if next_stage is not None:
        handoff_note = note or f"Advance from {stage_id} to {next_stage['id']}"
        add_handoff(payload, stage_id, next_stage["id"], handoff_note)
        next_stage["status"] = "in_progress"
        next_stage["started_at"] = next_stage.get("started_at") or now_iso()
        add_event(payload, "start-stage", next_stage["id"], f"auto-advanced from {stage_id}")

    save_state(workflow_run_id, payload)
    write_report(payload)
    return render_payload(payload, as_json)


def workflow_next(workflow_run_id: str, note: str | None, as_json: bool) -> int:
    payload = load_state(workflow_run_id)
    if not require_mutable_workflow(payload):
        print(f"Workflow is not mutable: {payload.get('workflow_status', 'active')}", file=sys.stderr)
        return 1
    current = current_in_progress_stage(payload)
    if current is not None:
        print(f"Stage already in progress: {current['id']}", file=sys.stderr)
        return 1
    next_stage = next_pending_stage(payload)
    if next_stage is None:
        print("No pending stage available", file=sys.stderr)
        return 1
    return start_stage(workflow_run_id, next_stage["id"], note, as_json)


def workflow_close(workflow_run_id: str, note: str | None, as_json: bool) -> int:
    payload = load_state(workflow_run_id)
    if is_workflow_archived(payload):
        print("Workflow already archived", file=sys.stderr)
        return 1
    if any(stage["status"] != "completed" for stage in payload["stages"]):
        print("Cannot close workflow with incomplete stages", file=sys.stderr)
        return 1
    if payload.get("workflow_status") == "closed":
        print("Workflow already closed", file=sys.stderr)
        return 1
    close_workflow_payload(payload, note)
    save_state(workflow_run_id, payload)
    write_report(payload)
    return render_payload(payload, as_json)


def workflow_archive(workflow_run_id: str, note: str | None, as_json: bool) -> int:
    payload = load_state(workflow_run_id)
    if is_workflow_archived(payload):
        print("Workflow already archived", file=sys.stderr)
        return 1
    if any(stage["status"] != "completed" for stage in payload["stages"]):
        print("Cannot archive workflow with incomplete stages", file=sys.stderr)
        return 1
    if payload.get("workflow_status") != "closed":
        close_workflow_payload(payload, note=None)
    archive_workflow_payload(payload, note)
    source_root = workflow_root_path(workflow_run_id)
    target_root = workflow_dir_for_root(ARCHIVE_ROOT, workflow_run_id)
    rewrite_spec_references(payload, target_root)
    save_state(workflow_run_id, payload)
    if source_root != target_root:
        ARCHIVE_ROOT.mkdir(parents=True, exist_ok=True)
        if target_root.exists():
            shutil.rmtree(target_root)
        shutil.move(str(source_root), str(target_root))
    write_report(payload)
    return render_payload(payload, as_json)


def parse_note(args: list[str]) -> tuple[list[str], str | None, bool]:
    clean: list[str] = []
    note = None
    as_json = False
    index = 0
    while index < len(args):
        token = args[index]
        if token == "--json":
            as_json = True
            index += 1
            continue
        if token == "--note":
            if index + 1 >= len(args):
                raise ValueError("--note requires a value")
            note = args[index + 1]
            index += 2
            continue
        clean.append(token)
        index += 1
    return clean, note, as_json


def main() -> int:
    raw_args = sys.argv[1:]
    if not raw_args:
        print_usage()
        return 1

    command = raw_args[0]
    try:
        if command in {"list-workflows"}:
            _, _, as_json = parse_note(raw_args[1:])
            return list_workflows(as_json)

        if command in {
            "status",
            "workflow-status",
            "resume",
            "resume-workflow",
            "workflow-note",
            "workflow-handoff",
            "start-stage",
            "complete-stage",
            "advance-stage",
            "workflow-next",
            "workflow-close",
            "workflow-archive",
        }:
            try:
                args, note, as_json = parse_note(raw_args[1:])
            except ValueError as exc:
                print(str(exc), file=sys.stderr)
                return 1
            if command in {"status", "workflow-status", "resume", "resume-workflow"}:
                if len(args) != 1:
                    print_usage()
                    return 1
                return resume_workflow(args[0], as_json)
            if command == "workflow-note":
                if len(args) != 2:
                    print_usage()
                    return 1
                return workflow_note(args[0], args[1], note, as_json)
            if command == "workflow-handoff":
                if len(args) != 3:
                    print_usage()
                    return 1
                return workflow_handoff(args[0], args[1], args[2], note, as_json)
            if command == "workflow-close":
                if len(args) != 1:
                    print_usage()
                    return 1
                return workflow_close(args[0], note, as_json)
            if command == "workflow-next":
                if len(args) != 1:
                    print_usage()
                    return 1
                return workflow_next(args[0], note, as_json)
            if command == "workflow-archive":
                if len(args) != 1:
                    print_usage()
                    return 1
                return workflow_archive(args[0], note, as_json)
            if len(args) != 2:
                print_usage()
                return 1
            if command == "start-stage":
                return start_stage(args[0], args[1], note, as_json)
            if command == "advance-stage":
                return advance_stage(args[0], args[1], note, as_json)
            return complete_stage(args[0], args[1], note, as_json)

        as_json = False
        args = raw_args
        if args[-1] == "--json":
            as_json = True
            args = args[:-1]
        prompt = " ".join(args).strip()
        if not prompt:
            print_usage()
            return 1
        return create_workflow(prompt, as_json)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
