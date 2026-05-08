# Architecture Pivot Procedure

## Purpose

Codex-native procedure for recording an architecture pivot and forcing propagation work across the required project artifacts.

## Primary Role

- `architect`

## Escalation Roles

- `workflow-designer`
- `data-governance-architect`
- `ci-cd-specialist`

## KB Domains

- `governance`
- `orchestration`
- `observability`

## Use When

- the project changes its primary architecture or delivery surface
- new sessions must stop re-deciding which architecture is current
- multiple artifacts need a tracked before-vs-after reconciliation workflow

## Inputs

- optional target project directory
- required `--to <new-architecture>`
- optional `--from <old-architecture>`
- optional `--rationale <text>`
- optional `--json`

## Procedure

1. Route to `architect`.
2. Run `python3 scripts/agentcodex.py architecture-pivot [target-project-dir] --to <new-architecture> [--from <old-architecture>] [--rationale <text>] [--json]`.
3. Record the previous and new architecture values plus the pivot rationale.
4. Generate the mandatory propagation checklist for canonical artifacts such as `AGENTS.md`, context history, status, and project-standard status.
5. Persist the pivot state in `.agentcodex/state/project-state.json`.
6. Run `agentcodex status-reconcile` after the follow-up artifact updates land.
7. Escalate workflow implications to `workflow-designer`, governance implications to `data-governance-architect`, and deployment-surface implications to `ci-cd-specialist`.

## Outputs

- repo-local architecture pivot report
- canonical pending-reconciliation state
- explicit before-vs-after artifact checklist
