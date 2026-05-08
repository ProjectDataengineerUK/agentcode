# Platform Health Procedure

## Purpose

Codex-native procedure for validating Databricks or Microsoft Fabric platform connectivity through repo-local checks and reports.

## Primary Role

- `data-platform-engineer`

## Escalation Roles

- `databricks-architect`
- `fabric-architect`
- `data-observability-engineer`

## KB Domains

- `databricks`
- `microsoft-fabric`
- `observability`

## Use When

- platform credentials or SDK wiring need verification before implementation
- a project needs proof that Databricks or Fabric access is configured
- operational readiness must be recorded in a repo-local report

## Inputs

- target platform: `databricks` or `fabric`
- local environment credentials for the selected platform
- optional `--json` when the output should be machine-readable

## Procedure

1. Route to `data-platform-engineer`.
2. Run `python3 scripts/agentcodex.py platform-health <databricks|fabric> [--json]`.
3. Check whether required SDK dependencies are installed locally.
4. Validate auth and a minimal read-only connectivity path for the selected platform.
5. Write the result to `.agentcodex/reports/platform-health/`.
6. Escalate Databricks-specific issues to `databricks-architect`, Fabric-specific issues to `fabric-architect`, and logging/reporting gaps to `data-observability-engineer`.

## Outputs

- repo-local platform health report
- explicit dependency or credential failures when present
- machine-readable payload when `--json` is requested
