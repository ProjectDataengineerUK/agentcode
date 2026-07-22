from __future__ import annotations

from dataclasses import dataclass
import sys
from typing import Callable


RunCommand = Callable[[str, list[str]], int]


@dataclass(frozen=True)
class CommandSpec:
    script: str
    description: str
    usage_args: str = ""
    min_args: int = 0
    exact_args: int | None = None
    forwarded_command: str | None = None
    append_args: tuple[str, ...] = ()
    aliases: tuple[str, ...] = ()

    def usage(self, executable: str, command_name: str) -> str:
        suffix = f" {self.usage_args}" if self.usage_args else ""
        return f"{executable} {command_name}{suffix}"


COMMANDS: dict[str, CommandSpec] = {
    "install": CommandSpec(
        "bootstrap_project.py",
        "Codex-first install flow; create lightweight project state by default",
        "<target-project-dir> [--mode light|full] [--full] [--with-codex] [--profile <profile-id>]",
        min_args=1,
    ),
    "init": CommandSpec(
        "bootstrap_project.py",
        "Bootstrap a target project with AgentCodex",
        "<target-project-dir> [--mode light|full] [--full] [--with-codex] [--profile <profile-id>]",
        min_args=1,
    ),
    "sync-project": CommandSpec(
        "sync_project.py",
        "Refresh AgentCodex-managed files in an existing project",
        "<target-project-dir> [--mode light|full] [--full] [--with-codex] [--profile <profile-id>]",
        min_args=1,
    ),
    "sync-kb-upstreams": CommandSpec(
        "sync_upstream_kb.py",
        "Refresh imported KB sources and sync mapped KB domains into .agentcodex/kb",
        "[--refresh-imports] [--apply] [--domain <domain>]",
    ),
    "sync-sources": CommandSpec(
        "sync_sources.py",
        "Collect lightweight metadata from trusted upstream source repositories",
        "[--source <source-id>] [--apply] [--use-git] [--limit <n>]",
    ),
    "sync-context": CommandSpec(
        "sync_context_history.py",
        "Create or refresh a feature context history entry from workflow artifacts",
        "<feature> [--owner <owner>]",
        min_args=1,
    ),
    "project-intake": CommandSpec("project_intake.py", "Run the interactive zero-state project intake flow"),
    "start": CommandSpec("start.py", "Scan the current project and launch the appropriate onboarding flow"),
    "daily-tasks": CommandSpec(
        "daily_tasks.py",
        "Record a daily task snapshot with done, in-progress, and backlog sections",
        "[--date YYYY-MM-DD] [--owner <owner>] [--done <task>] [--in-progress <task>] [--backlog <task>]",
    ),
    "new-context": CommandSpec(
        "new_context_history.py",
        "Create a standardized context history entry in .agentcodex/history",
        "<feature-or-topic> [--kind feature|session] [--owner <owner>]",
        min_args=1,
    ),
    "resume-context": CommandSpec(
        "resume_context.py",
        "Show the latest context history entry summary for a scope",
        "<feature-or-topic> [--kind feature|session]",
        min_args=1,
    ),
    "status": CommandSpec("current_status.py", "Show the current repo status snapshot or a specific section", "[section]"),
    "session-controls": CommandSpec(
        "session_controls_status.py",
        "Show local context-budget and cost-summary controls",
        "[--json]",
    ),
    "model-route": CommandSpec(
        "model_route.py",
        "Select and record the Codex model tier for an activity, role, budget, and risk",
        "[task-description ...] [--activity <id>] [--role <role-id>] [--budget low|standard|high] [--risk low|medium|high] [--json]",
    ),
    "audit-summary": CommandSpec("audit_summary.py", "Summarize repo-local run and failure audit signals", "[--json]"),
    "judge": CommandSpec(
        "judge.py",
        "Run an opt-in OpenRouter second-model review with a repo-local budget ledger",
        "<file|--stdin> [--phase generic|define|design|build] [--context <text>] [--model <model>] [--json] [--ledger]",
    ),
    "orchestrate-workflow": CommandSpec(
        "workflow_orchestrator.py",
        "Create repo-local workflow state, stages, and handoffs for a multi-agent task",
        "<prompt> [--json]",
        min_args=1,
    ),
    "list-workflows": CommandSpec(
        "workflow_orchestrator.py",
        "List repo-local workflow runs and their progress",
        "[--json]",
        forwarded_command="list-workflows",
    ),
    "workflow-status": CommandSpec(
        "workflow_orchestrator.py",
        "Show the current state and next step of a workflow run",
        "<workflow-run-id> [--json]",
        min_args=1,
        forwarded_command="workflow-status",
    ),
    "resume-workflow": CommandSpec(
        "workflow_orchestrator.py",
        "Show the current state and next step of a workflow run",
        "<workflow-run-id> [--json]",
        min_args=1,
        forwarded_command="resume-workflow",
    ),
    "workflow-note": CommandSpec(
        "workflow_orchestrator.py",
        "Add a repo-local note to a workflow stage",
        "<workflow-run-id> <stage-id> --note <text> [--json]",
        min_args=2,
        forwarded_command="workflow-note",
    ),
    "workflow-handoff": CommandSpec(
        "workflow_orchestrator.py",
        "Record a handoff note between two workflow stages",
        "<workflow-run-id> <from-stage-id> <to-stage-id> --note <text> [--json]",
        min_args=3,
        forwarded_command="workflow-handoff",
    ),
    "start-stage": CommandSpec(
        "workflow_orchestrator.py",
        "Mark a workflow stage as in progress",
        "<workflow-run-id> <stage-id> [--note <text>] [--json]",
        min_args=2,
        forwarded_command="start-stage",
    ),
    "complete-stage": CommandSpec(
        "workflow_orchestrator.py",
        "Mark a workflow stage as completed",
        "<workflow-run-id> <stage-id> [--note <text>] [--json]",
        min_args=2,
        forwarded_command="complete-stage",
    ),
    "advance-stage": CommandSpec(
        "workflow_orchestrator.py",
        "Complete a stage and automatically hand off to the next stage",
        "<workflow-run-id> <stage-id> [--note <text>] [--json]",
        min_args=2,
        forwarded_command="advance-stage",
    ),
    "workflow-next": CommandSpec(
        "workflow_orchestrator.py",
        "Start only the next valid pending stage",
        "<workflow-run-id> [--note <text>] [--json]",
        min_args=1,
        forwarded_command="workflow-next",
    ),
    "workflow-close": CommandSpec(
        "workflow_orchestrator.py",
        "Close a fully completed workflow run",
        "<workflow-run-id> [--note <text>] [--json]",
        min_args=1,
        forwarded_command="workflow-close",
    ),
    "workflow-archive": CommandSpec(
        "workflow_orchestrator.py",
        "Archive a closed workflow run under .agentcodex/archive",
        "<workflow-run-id> [--note <text>] [--json]",
        min_args=1,
        forwarded_command="workflow-archive",
    ),
    "validate": CommandSpec("validate_agentcodex.py", "Validate routing, KB, and roles manifests"),
    "validate-plugin": CommandSpec("validate_plugin_manifest.py", "Validate plugin manifest publication readiness"),
    "generate-roles": CommandSpec("generate_roles_manifest.py", "Regenerate .agentcodex/roles/roles.yaml from docs/roles"),
    "generate-routing": CommandSpec("generate_routing_manifest.py", "Regenerate .agentcodex/routing/routing.json"),
    "import-upstreams": CommandSpec(
        "import_upstreams.py",
        "Import as much as possible from AgentSpec, ECC, and data-agents into .agentcodex/imports",
        "[all|agentspec|ecc|data-agents]",
        min_args=1,
    ),
    "generate-import-catalog": CommandSpec("generate_import_catalog.py", "Regenerate import indexes from .agentcodex/imports"),
    "generate-ecc-extension": CommandSpec(
        "generate_ecc_extension_registry.py",
        "Regenerate the ECC extension registry from .agentcodex/imports/ecc without duplicating active surfaces",
    ),
    "generate-data-agents-extension": CommandSpec(
        "generate_data_agents_extension_registry.py",
        "Regenerate the Data Agents extension registry without duplicating active Codex-native surfaces",
    ),
    "check-project": CommandSpec(
        "check_bootstrapped_project.py",
        "Validate a bootstrapped target project",
        "<target-project-dir>",
        min_args=1,
    ),
    "readiness-report": CommandSpec(
        "project_readiness_report.py",
        "Generate a project-standard readiness report for a target project",
        "<target-project-dir>",
        min_args=1,
    ),
    "ship-gate": CommandSpec(
        "project_ship_gate.py",
        "Enforce the project-standard ship gate for a target project",
        "<target-project-dir>",
        min_args=1,
    ),
    "control-plane-check": CommandSpec(
        "control_plane_check.py",
        "Run multi-agent, token, cost, and security/compliance control checks for a target project",
        "<target-project-dir> [all|multi-agent|token|cost|security] [--json]",
        min_args=1,
    ),
    "enterprise-readiness": CommandSpec(
        "control_plane_check.py",
        "Alias for control-plane-check",
        "<target-project-dir> [all|multi-agent|token|cost|security] [--json]",
        min_args=1,
    ),
    "maturity5-check": CommandSpec(
        "maturity5_check.py",
        "Evaluate the executable Maturity 5 DataOps + LLMOps baseline for a target project",
        "<target-project-dir> [--profile <profile-id>] [--json]",
        min_args=1,
        aliases=("maturity-5-check",),
    ),
    "refresh-all": CommandSpec(
        "refresh_all.py",
        "Refresh generated artifacts and optionally sync/check a target project",
        "[--target-project <path>] [--with-codex] [--skip-import-catalog]",
    ),
    "install-local-automation": CommandSpec(
        "install_local_automation.py",
        "Install repo-local git hooks for refresh automation",
    ),
    "memory-retrieve": CommandSpec(
        "memory_retrieve.py",
        "Retrieve compact long-term memory context from local memory snapshots",
        "<query> [--task-type <type>] [--scope <scope>] [--scope-value <value>] [--json]",
        min_args=1,
    ),
    "memory-ingest": CommandSpec(
        "memory_ingest.py",
        "Ingest a local memory payload into the file-based memory backend",
        "<semantic|episodic|procedural> <json-file>",
        exact_args=2,
    ),
    "memory-compact": CommandSpec("memory_compact.py", "Deduplicate and compact file-based memory snapshots"),
    "memory-health": CommandSpec(
        "memory_backend_health.py",
        "Show health and storage paths for the active or requested memory backend",
        "[backend-id] [--json]",
    ),
    "memory-lint": CommandSpec("memory_lint.py", "Run local memory lint checks over the current snapshots", "[--json]"),
    "memory-extract": CommandSpec(
        "memory_extract.py",
        "Produce repo-local seed memory candidates without external LLM calls",
        "[--json]",
    ),
    "extract-log-knowledge": CommandSpec(
        "extract_log_knowledge.py",
        "Produce memory/knowledge candidates from local observability logs",
        "[--json]",
    ),
    "memory-review-candidates": CommandSpec(
        "memory_review_candidates.py",
        "Create a review file for the latest or requested memory candidates",
        "[candidate-file] [--json]",
    ),
    "memory-approve-candidates": CommandSpec(
        "memory_approve_candidates.py",
        "Approve and ingest reviewed memory candidates",
        "[review-file] [--json]",
    ),
    "review-kb-updates": CommandSpec(
        "review_kb_updates.py",
        "List KB update proposal files generated from reviewed operational evidence",
        "[--json]",
    ),
    "promote-kb-update": CommandSpec(
        "promote_kb_update.py",
        "Promote a KB update proposal into draft KB pages without overwriting existing content",
        "<candidate-file> [--json]",
        min_args=1,
    ),
    "platform-health": CommandSpec(
        "platform_health.py",
        "Run repo-local Databricks or Fabric platform health checks",
        "<databricks|fabric> [--json]",
    ),
    "status-reconcile": CommandSpec(
        "status_reconcile.py",
        "Reconcile architecture and evidence signals into a canonical repo-local state snapshot",
        "[target-project-dir] [--json]",
    ),
    "architecture-pivot": CommandSpec(
        "architecture_pivot.py",
        "Record an architecture pivot and mark mandatory propagation targets for reconciliation",
        "[target-project-dir] --to <new-architecture> [--from <old-architecture>] [--rationale <text>] [--json]",
    ),
    "preflight": CommandSpec(
        "preflight.py",
        "Run stack-aware preflight checks before build or deploy slices",
        "[target-project-dir] [--stack <id>] [--json]",
    ),
    "stack-detect": CommandSpec(
        "stack_detect.py",
        "Detect the project stack by layer and recommend specialists plus risk areas",
        "[target-project-dir] [--json]",
    ),
    "failure-pattern-promote": CommandSpec(
        "failure_pattern_promote.py",
        "Cluster recurrent failure signals and emit repo-local guardrail promotion candidates",
        "[target-project-dir] [--json]",
    ),
    "databricks-readiness": CommandSpec(
        "databricks_readiness.py",
        "Run a Databricks-specific readiness review over bundles, apps, jobs, governance, and runtime boundaries",
        "[target-project-dir] [--json]",
    ),
    "project-structure": CommandSpec(
        "project_structure.py",
        "Summarize the canonical AgentCodex structure groups and write a repo-local layout report",
        "[--json]",
    ),
    "approval-gate-sync": CommandSpec(
        "approval_gate_sync.py",
        "Persist approval-gate state transitions in a canonical repo-local control plane file",
        "[target-project-dir] <gate-id> <pending|approved|dispatched|executed|expired|invalidated> [--commit <sha>] [--run <id-or-url>] [--note <text>] [--json]",
        min_args=2,
    ),
    "memory-validate": CommandSpec(
        "memory_validate.py",
        "Validate memory schemas, examples, snapshots, and synthetic contracts",
    ),
}

ALIASES = {alias: name for name, spec in COMMANDS.items() for alias in spec.aliases}


def command_names(include_aliases: bool = False) -> list[str]:
    names = list(COMMANDS)
    if include_aliases:
        names.extend(ALIASES)
    return sorted(names)


def resolve_command(name: str) -> tuple[str, CommandSpec] | None:
    canonical = ALIASES.get(name, name)
    spec = COMMANDS.get(canonical)
    if spec is None:
        return None
    return canonical, spec


def print_help(executable: str) -> int:
    print("AgentCodex CLI")
    print()
    print("Usage:")
    for name, spec in COMMANDS.items():
        print(f"  {spec.usage(executable, name)}")
    print(f"  {executable} help")
    print()
    print("Commands:")
    width = max(len(name) for name in COMMANDS)
    for name, spec in COMMANDS.items():
        print(f"  {name:<{width}} {spec.description}")
    print()
    print("Note:")
    print("  `install` is the preferred Codex-first bootstrap path and uses lightweight mode by default.")
    print("  Use `--mode full` when you want to vendor runtime assets into a project.")
    print("  The CLI can run from an editable checkout or from an installed runtime bundle.")
    return 0


def usage_error(executable: str, command_name: str, spec: CommandSpec) -> int:
    print(f"Usage: {spec.usage(executable, command_name)}", file=sys.stderr)
    return 1


def dispatch(args: list[str], run_command: RunCommand, executable: str) -> int:
    if not args or args[0] in {"help", "--help", "-h"}:
        return print_help(executable)

    command = args[0]
    rest = args[1:]
    resolved = resolve_command(command)
    if resolved is None:
        print(f"Unknown command: {command}", file=sys.stderr)
        return print_help(executable)

    canonical, spec = resolved
    if spec.exact_args is not None and len(rest) != spec.exact_args:
        return usage_error(executable, canonical, spec)
    if len(rest) < spec.min_args:
        return usage_error(executable, canonical, spec)

    forwarded_args = [spec.forwarded_command, *rest] if spec.forwarded_command else [*rest]
    if spec.append_args:
        forwarded_args.extend(spec.append_args)
    return run_command(spec.script, forwarded_args)
