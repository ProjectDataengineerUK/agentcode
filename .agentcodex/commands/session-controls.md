# Session Controls Procedure

## Purpose

Codex-native procedure for surfacing repo-local context-budget and cost-summary signals without hidden runtime hooks.

## Primary Role

- `context-optimizer`

## Escalation Roles

- `data-observability-engineer`
- `planner`

## KB Domains

- `observability`
- `ai-data-engineering`

## Use When

- a session needs a compact budget and cost view before continuing
- context pressure should be assessed without replaying the whole history
- local control signals should be recorded in a repo-local report

## Inputs

- optional `--json` for machine-readable output

## Procedure

1. Route to `context-optimizer`.
2. Run `python3 scripts/agentcodex.py session-controls [--json]`.
3. Read local observability metrics and infer a repo-local context budget heuristic.
4. Summarize recent script activity through fixed cost tiers.
5. Summarize the active model-routing policy and latest automatic selection.
6. Write the result to `.agentcodex/reports/session-controls/session-controls.md`.
7. Escalate metric semantics to `data-observability-engineer` when the heuristic needs refinement.

## Outputs

- local context-budget snapshot
- local cost-summary snapshot
- active model-routing snapshot
- repo-local report path for audit and resume use
