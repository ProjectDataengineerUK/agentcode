# Status Reconcile Procedure

## Purpose

Codex-native procedure for reconciling competing status, architecture, and evidence signals into one repo-local canonical snapshot.

## Primary Role

- `workflow-iterator`

## Escalation Roles

- `architect`
- `data-governance-architect`
- `data-observability-engineer`

## KB Domains

- `governance`
- `observability`
- `ai-data-engineering`

## Use When

- multiple status artifacts disagree about readiness or architecture
- a handoff needs one current source of truth before more implementation
- final claims should be blocked until contradictions are explicit

## Inputs

- optional target project directory
- optional `--json` for machine-readable output

## Procedure

1. Route to `workflow-iterator`.
2. Run `python3 scripts/agentcodex.py status-reconcile [target-project-dir] [--json]`.
3. Inspect `AGENTS.md`, context history, handoff, readiness, and build/delivery reports.
4. Extract architecture candidates, evidence levels, and contradictory completion signals.
5. Write the reconciliation report to `.agentcodex/reports/status-reconcile.md`.
6. Persist the canonical snapshot to `.agentcodex/state/project-state.json`.
7. Escalate architecture conflicts to `architect`, governance drift to `data-governance-architect`, and reporting gaps to `data-observability-engineer`.

## Outputs

- repo-local status reconciliation report
- canonical machine-readable project state snapshot
- explicit contradiction list and `needs_reconciliation` flag
