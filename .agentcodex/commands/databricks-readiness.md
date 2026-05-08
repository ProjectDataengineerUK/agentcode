# Databricks Readiness Procedure

## Purpose

Codex-native procedure for reviewing Databricks project readiness beyond generic platform health, including bundles, apps, jobs, governance, and runtime boundaries.

## Primary Role

- `databricks-architect`

## Escalation Roles

- `platform-access-engineer`
- `ci-cd-specialist`
- `mosaic-ai-engineer`

## KB Domains

- `databricks`
- `governance`
- `observability`

## Use When

- Databricks work is operationally harder than the current generic checks explain
- a repo uses DABs, Apps, Jobs, Unity Catalog, or AI surfaces and needs a real readiness pass
- runtime and governance boundaries need to be checked before deploy claims

## Inputs

- optional target project directory
- Databricks bundle files, app manifests, resource YAMLs, SQL, and config files
- optional `--json`

## Procedure

1. Route to `databricks-architect`.
2. Run `python3 scripts/agentcodex.py databricks-readiness [target-project-dir] [--json]`.
3. Review environment, bundle shape, app manifest, job reliability markers, Unity Catalog signals, and governance/runtime boundaries.
4. Flag common DAB path mistakes, missing targets or variables, weak app configuration, missing retries/timeouts/notifications, and DBFS-first anti-patterns.
5. Write the report to `.agentcodex/reports/databricks-readiness.md`.
6. Persist the machine-readable result to `.agentcodex/state/project-state.json`.
7. Escalate principal and grant boundary concerns to `platform-access-engineer`, deployment automation concerns to `ci-cd-specialist`, and Databricks AI surface concerns to `mosaic-ai-engineer`.

## Outputs

- repo-local Databricks readiness report
- Databricks-specific warnings grounded in project files
- canonical readiness snapshot for Databricks work
