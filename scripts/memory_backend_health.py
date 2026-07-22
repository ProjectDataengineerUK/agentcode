#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from memory_backend import active_backend_id, get_backend


ROOT = Path(__file__).resolve().parent.parent


def print_usage() -> int:
    print("Usage: python3 scripts/agentcodex.py memory-health [backend-id] [--json]")
    return 1


def main() -> int:
    args = sys.argv[1:]
    backend_id: str | None = None
    as_json = False

    for arg in args:
        if arg == "--json":
            as_json = True
            continue
        if backend_id is None:
            backend_id = arg
            continue
        return print_usage()

    resolved_id = backend_id or active_backend_id()
    backend = get_backend(resolved_id)
    health = backend.health()
    snapshot_paths = {key: str(path.relative_to(ROOT)) for key, path in backend.snapshot_paths().items()}
    payload = {
        "backend_id": health.backend_id,
        "status": health.status,
        "active_sources": health.active_sources,
        "writable": health.writable,
        "summary_path": str(backend.summary_path().relative_to(ROOT)),
        "snapshot_paths": snapshot_paths,
    }

    if as_json:
        print(json.dumps(payload, indent=2))
        return 0

    print("# Memory Backend Health")
    print()
    print(f"- backend_id: {payload['backend_id']}")
    print(f"- status: {payload['status']}")
    print(f"- active_sources: {payload['active_sources']}")
    print(f"- writable: {payload['writable']}")
    print(f"- summary_path: {payload['summary_path']}")
    print("- snapshot_paths:")
    for memory_type, path in payload["snapshot_paths"].items():
        print(f"  - {memory_type}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
