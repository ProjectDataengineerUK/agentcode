#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def print_usage() -> int:
    print(
        "Usage: python3 scripts/agentcodex.py refresh-all "
        "[--target-project <path>] [--with-codex] [--skip-import-catalog]"
    )
    return 1


def run_step(label: str, command: list[str]) -> None:
    print(f"[refresh-all] {label}")
    subprocess.run(command, cwd=str(ROOT), check=True)


def main() -> int:
    args = sys.argv[1:]
    target_project: Path | None = None
    with_codex = False
    skip_import_catalog = False

    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--target-project":
            if i + 1 >= len(args):
                return print_usage()
            target_project = Path(args[i + 1]).resolve()
            i += 2
            continue
        if arg == "--with-codex":
            with_codex = True
            i += 1
            continue
        if arg == "--skip-import-catalog":
            skip_import_catalog = True
            i += 1
            continue
        return print_usage()

    python = sys.executable

    run_step("generate roles manifest", [python, str(ROOT / "scripts" / "generate_roles_manifest.py")])
    run_step("generate routing manifest", [python, str(ROOT / "scripts" / "generate_routing_manifest.py")])
    run_step("generate ECC extension registry", [python, str(ROOT / "scripts" / "generate_ecc_extension_registry.py")])
    run_step("generate Data Agents extension registry", [python, str(ROOT / "scripts" / "generate_data_agents_extension_registry.py")])
    run_step("generate status doc", [python, str(ROOT / "scripts" / "generate_status_doc.py")])
    run_step("sync all context histories", [python, str(ROOT / "scripts" / "sync_all_context_histories.py")])
    run_step("extract memory candidates", [python, str(ROOT / "scripts" / "memory_extract.py")])
    run_step("extract log knowledge candidates", [python, str(ROOT / "scripts" / "extract_log_knowledge.py")])
    run_step("lint memory snapshots", [python, str(ROOT / "scripts" / "memory_lint.py")])

    imports_manifest = ROOT / ".agentcodex" / "imports" / "manifest.json"
    if imports_manifest.exists() and not skip_import_catalog:
        run_step("generate import catalog", [python, str(ROOT / "scripts" / "generate_import_catalog.py")])

    run_step("validate agentcodex", [python, str(ROOT / "scripts" / "validate_agentcodex.py")])

    if target_project is not None:
        sync_args = [python, str(ROOT / "scripts" / "sync_project.py"), str(target_project)]
        if with_codex:
            sync_args.append("--with-codex")
        run_step("sync target project", sync_args)
        run_step(
            "check target project",
            [python, str(ROOT / "scripts" / "check_bootstrapped_project.py"), str(target_project)],
        )
        run_step(
            "generate target readiness report",
            [python, str(ROOT / "scripts" / "project_readiness_report.py"), str(target_project)],
        )

    print("[refresh-all] completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
