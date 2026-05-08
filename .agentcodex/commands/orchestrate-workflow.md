# Orchestrate Workflow Procedure

## Purpose

Codex-native procedure for selecting a workflow, copying the matching spec template, and creating explicit stage/handoff state in repo-local files.

## Primary Role

- `planner`

## Escalation Roles

- `workflow-definer`
- `data-platform-engineer`
- `meeting-analyst`

## KB Domains

- `observability`
- `governance`
- `ai-data-engineering`

## Use When

- a task is clearly multi-step or cross-domain
- a workflow should be made explicit before implementation starts
- stage ownership and handoff order should be recoverable from files

## Inputs

- a plain-language task prompt
- optional `--json` for machine-readable output
- optional stage note when starting or completing a stage
- a valid `workflow_run_id` when resuming an existing run; only letters, numbers, `.`, `_`, and `-` are accepted

## Procedure

1. Run `python3 scripts/agentcodex.py orchestrate-workflow "<prompt>" [--json]`.
2. Detect the best workflow family from the prompt.
3. Generate a repo-local `workflow_run_id` from the prompt; if the base id already exists in active or archived runs, append an incremental suffix such as `-2` or `-3`.
4. Copy the matching template into `.agentcodex/workflows/<workflow-run-id>/`.
5. Reject invalid resume/archive ids that contain separators, traversal markers, or absolute paths.
6. Write `state.json` with stages and handoff plan.
7. Start work with `python3 scripts/agentcodex.py workflow-next <workflow-run-id> [--note "<text>"]` or explicitly with `start-stage` when targeting the same next valid pending stage.
8. Complete a stage manually with `python3 scripts/agentcodex.py complete-stage <workflow-run-id> <stage-id> [--note "<text>"]` only for the current in-progress stage, or advance in one step with `python3 scripts/agentcodex.py advance-stage <workflow-run-id> <stage-id> [--note "<text>"]`.
9. Add local stage evidence with `python3 scripts/agentcodex.py workflow-note <workflow-run-id> <stage-id> --note "<text>"`.
10. Register explicit cross-stage transfer with `python3 scripts/agentcodex.py workflow-handoff <workflow-run-id> <from-stage-id> <to-stage-id> --note "<text>"` when the transfer should be operator-authored instead of auto-generated.
11. Inspect all runs with `python3 scripts/agentcodex.py list-workflows [--json]`.
12. Resume visibility at any point with `python3 scripts/agentcodex.py resume-workflow <workflow-run-id> [--json]` or `workflow-status`.
13. Close a fully completed run with `python3 scripts/agentcodex.py workflow-close <workflow-run-id> [--note "<text>"]`.
14. Archive a closed run with `python3 scripts/agentcodex.py workflow-archive <workflow-run-id> [--note "<text>"]` to move it under `.agentcodex/archive/workflows/`.
15. After archive, keep using the same `workflow_run_id`; the orchestrator resolves the archived path and rewrites `spec_path` references to `.agentcodex/archive/workflows/<workflow-run-id>/`.
16. Write a repo-local workflow report under `.agentcodex/reports/workflows/`.
17. Continue work from the generated spec and state artifacts until the run is closed or archived.

## Outputs

- workflow state file
- copied spec template
- workflow report
- stage event history inside `state.json`
- handoff log inside `state.json`
- explicit workflow lifecycle status (`active`, `closed`, `archived`)
- ordered stage transitions with stricter current/next-stage enforcement
- archive-safe path resolution for resumed archived runs
- collision-safe workflow id generation for repeated prompts
