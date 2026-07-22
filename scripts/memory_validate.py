#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MEMORY_ROOT = ROOT / ".agentcodex" / "memory"
SCHEMAS_DIR = MEMORY_ROOT / "schemas"
EXAMPLES_DIR = MEMORY_ROOT / "examples"
CACHE_ROOT = ROOT / ".agentcodex" / "cache" / "memory" / "snapshots"
REPORTS_ROOT = ROOT / ".agentcodex" / "reports" / "memory"
ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$")


def load_json(path: Path) -> dict | list:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_datetime(value: str) -> bool:
    if not isinstance(value, str) or not ISO_RE.match(value):
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def validate_instance(instance: object, schema: dict, path: str = "$") -> list[str]:
    errors: list[str] = []
    expected_type = schema.get("type")
    if isinstance(expected_type, list):
        valid = any(_matches_type(instance, item) for item in expected_type)
        if not valid:
            return [f"{path}: expected one of {expected_type}"]
    elif expected_type and not _matches_type(instance, expected_type):
        return [f"{path}: expected {expected_type}"]

    if "const" in schema and instance != schema["const"]:
        errors.append(f"{path}: expected const value {schema['const']!r}")
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: expected one of {schema['enum']}")
    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        minimum = schema.get("minimum")
        maximum = schema.get("maximum")
        if minimum is not None and instance < minimum:
            errors.append(f"{path}: value {instance} below minimum {minimum}")
        if maximum is not None and instance > maximum:
            errors.append(f"{path}: value {instance} above maximum {maximum}")
    if isinstance(instance, str):
        min_length = schema.get("minLength")
        if min_length is not None and len(instance) < min_length:
            errors.append(f"{path}: string shorter than {min_length}")
        if schema.get("format") == "date-time" and not validate_datetime(instance):
            errors.append(f"{path}: invalid date-time format")
    if isinstance(instance, list):
        min_items = schema.get("minItems")
        if min_items is not None and len(instance) < min_items:
            errors.append(f"{path}: list shorter than {min_items}")
        item_schema = schema.get("items")
        if item_schema:
            for index, item in enumerate(instance):
                errors.extend(validate_instance(item, item_schema, f"{path}[{index}]"))
    if isinstance(instance, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in instance:
                errors.append(f"{path}: missing required field {key}")
        properties = schema.get("properties", {})
        for key, prop_schema in properties.items():
            if key in instance:
                errors.extend(validate_instance(instance[key], prop_schema, f"{path}.{key}"))
    return errors


def _matches_type(instance: object, expected_type: str) -> bool:
    if expected_type == "object":
        return isinstance(instance, dict)
    if expected_type == "array":
        return isinstance(instance, list)
    if expected_type == "string":
        return isinstance(instance, str)
    if expected_type == "number":
        return isinstance(instance, (int, float)) and not isinstance(instance, bool)
    if expected_type == "integer":
        return isinstance(instance, int) and not isinstance(instance, bool)
    if expected_type == "null":
        return instance is None
    if expected_type == "boolean":
        return isinstance(instance, bool)
    return False


def write_report(lines: list[str]) -> Path:
    REPORTS_ROOT.mkdir(parents=True, exist_ok=True)
    path = REPORTS_ROOT / "validation-report.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def main() -> int:
    schema_paths = {
        "semantic": SCHEMAS_DIR / "semantic-memory.schema.json",
        "episodic": SCHEMAS_DIR / "episodic-memory.schema.json",
        "procedural": SCHEMAS_DIR / "procedural-memory.schema.json",
        "query": SCHEMAS_DIR / "memory-query.schema.json",
        "write_event": SCHEMAS_DIR / "memory-write-event.schema.json",
    }
    example_paths = {
        "semantic": EXAMPLES_DIR / "semantic-memory-example.json",
        "episodic": EXAMPLES_DIR / "episodic-memory-example.json",
        "procedural": EXAMPLES_DIR / "procedural-memory-example.json",
    }
    snapshot_paths = {
        "semantic": CACHE_ROOT / "semantic-memories.json",
        "episodic": CACHE_ROOT / "episodic-memories.json",
        "procedural": CACHE_ROOT / "procedural-memories.json",
    }

    errors: list[str] = []
    lines = [
        "# Memory Validation Report",
        "",
        f"- generated_at: {datetime.now(UTC).isoformat()}",
        "",
        "## Checks",
        "",
    ]

    schemas = {}
    for name, path in schema_paths.items():
        if not path.exists():
            errors.append(f"missing schema: {path}")
            continue
        try:
            schemas[name] = load_json(path)
            lines.append(f"- loaded schema: {path.relative_to(ROOT)}")
        except json.JSONDecodeError as exc:
            errors.append(f"invalid schema JSON {path}: {exc}")

    for name, path in example_paths.items():
        if not path.exists():
            errors.append(f"missing example: {path}")
            continue
        payload = load_json(path)
        issues = validate_instance(payload, schemas[name], f"example:{name}")
        if issues:
            errors.extend(issues)
        else:
            lines.append(f"- validated example: {path.relative_to(ROOT)}")

    for name, path in snapshot_paths.items():
        if not path.exists():
            errors.append(f"missing snapshot: {path}")
            continue
        payload = load_json(path)
        if not isinstance(payload, list):
            errors.append(f"snapshot is not a list: {path}")
            continue
        for index, item in enumerate(payload):
            issues = validate_instance(item, schemas[name], f"snapshot:{name}[{index}]")
            if issues:
                errors.extend(issues)
        lines.append(f"- validated snapshot collection: {path.relative_to(ROOT)} ({len(payload)} items)")

    synthetic_query = {
        "query": "project standard ship gate",
        "task_type": "review",
        "scope_filter": {"scope": "project", "scope_value": "agentcodex"},
        "limits": {"semantic": 3, "episodic": 2, "procedural": 1},
    }
    query_issues = validate_instance(synthetic_query, schemas["query"], "synthetic:query")
    if query_issues:
        errors.extend(query_issues)
    else:
        lines.append("- validated synthetic retrieval payload")

    synthetic_write = {
        "event_id": "evt-memory-001",
        "event_type": "append",
        "memory_type": "semantic",
        "memory_id": "sem-project-routing-001",
        "source": "repo-docs",
        "owner": "agentcodex",
        "timestamp": "2026-04-23T00:00:00Z",
        "issues": [],
        "target_snapshot": ".agentcodex/cache/memory/snapshots/semantic-memories.json",
    }
    write_issues = validate_instance(synthetic_write, schemas["write_event"], "synthetic:write_event")
    if write_issues:
        errors.extend(write_issues)
    else:
        lines.append("- validated synthetic write-event payload")

    if errors:
        lines.extend(["", "## Errors", ""])
        lines.extend(f"- {error}" for error in errors)
        report_path = write_report(lines)
        print(f"Memory validation failed. Report: {report_path}")
        for error in errors:
            print(f"- {error}")
        return 1

    lines.extend(["", "## Result", "", "- all schemas and checked payloads validated successfully"])
    report_path = write_report(lines)
    print(f"Memory validation passed. Report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
