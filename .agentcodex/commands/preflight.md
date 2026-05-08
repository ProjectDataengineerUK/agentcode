# Preflight Procedure

## Purpose

Codex-native procedure for running stack-aware environment and platform checks before build or deploy slices.

## Primary Role

- `data-platform-engineer`

## Escalation Roles

- `terraform-specialist`
- `ci-cd-specialist`
- `data-observability-engineer`

## KB Domains

- `databricks`
- `terraform`
- `observability`

## Use When

- a project is about to enter build or deploy work
- environment assumptions need to be surfaced before runtime failures
- stack-specific prerequisites should be written to a repo-local report

## Inputs

- optional target project directory
- optional `--stack <id>` when auto-detection should be bypassed
- optional `--json`

## Procedure

1. Route to `data-platform-engineer`.
2. Run `python3 scripts/agentcodex.py preflight [target-project-dir] [--stack <id>] [--json]`.
3. Auto-detect supported stacks from repo markers when no explicit stack is provided.
4. Check local prerequisites such as CLIs, workflow presence, project markers, and Databricks environment hints.
5. Write the report to `.agentcodex/reports/preflight-report.md`.
6. Persist the machine-readable snapshot to `.agentcodex/state/project-state.json`.
7. Escalate Terraform failures to `terraform-specialist`, pipeline-surface issues to `ci-cd-specialist`, and missing runtime observability to `data-observability-engineer`.

## Outputs

- repo-local preflight report
- stack-by-stack check status
- canonical preflight snapshot in project state
