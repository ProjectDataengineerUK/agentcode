# Approval Gate Sync Procedure

## Purpose

Codex-native procedure for recording approval-gated operations in one canonical repo-local control-plane file.

## Primary Role

- `ci-cd-specialist`

## Escalation Roles

- `architect`
- `data-governance-architect`
- `data-observability-engineer`

## KB Domains

- `governance`
- `orchestration`
- `observability`

## Use When

- deploy, apply, or migration steps require an auditable approval lifecycle
- approval state is drifting across workflow files, reports, and CI runs
- a project needs `pending`, `approved`, `dispatched`, `executed`, `expired`, or `invalidated` tracking

## Inputs

- optional target project directory
- required gate id
- required gate status
- optional `--commit <sha>`
- optional `--run <id-or-url>`
- optional `--note <text>`
- optional `--json`

## Procedure

1. Route to `ci-cd-specialist`.
2. Run `python3 scripts/agentcodex.py approval-gate-sync [target-project-dir] <gate-id> <status> [--commit <sha>] [--run <id-or-url>] [--note <text>] [--json]`.
3. Update the gate lifecycle in `.agentcodex/state/approval-gates.json`.
4. Regenerate the human-readable report in `.agentcodex/reports/approval-gates.md`.
5. Tie the gate update to the relevant commit or workflow run when available.
6. Escalate architecture-level release decisions to `architect`, governance approval policy questions to `data-governance-architect`, and observability/reporting issues to `data-observability-engineer`.

## Outputs

- canonical approval-gate state file
- repo-local approval gate report
- auditable link between gate status, commit, and workflow run
