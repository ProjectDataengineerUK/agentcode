# Audit Summary Procedure

## Purpose

Codex-native procedure for summarizing repo-local run and failure audit signals.

## Primary Role

- `data-observability-engineer`

## Escalation Roles

- `planner`
- `reviewer`

## KB Domains

- `observability`
- `governance`

## Use When

- the current operational state should be summarized from repo-local evidence
- failures or run patterns need a compact audit view
- the user wants a quick operational summary without opening raw JSON files

## Inputs

- optional `--json` for machine-readable output

## Procedure

1. Run `python3 scripts/agentcodex.py audit-summary [--json]`.
2. Read `.agentcodex/observability/runs/` and `.agentcodex/observability/failures/`.
3. Aggregate runs by script and status.
4. Aggregate source failures by stage.
5. Write the report to `.agentcodex/reports/audit/audit-summary.md`.

## Outputs

- repo-local audit summary report
- compact counts by script, status, and failure stage
