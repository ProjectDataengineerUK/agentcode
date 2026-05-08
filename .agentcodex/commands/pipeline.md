# Pipeline Procedure

## Purpose

Codex-native replacement for AgentSpec's `/pipeline` command.

## Primary Role

- `pipeline-architect`

## Escalation Roles

- `spark-engineer`
- `dbt-specialist`
- `data-quality-analyst`

## KB Domains

- `orchestration`
- `airflow`
- `dbt`
- `data-quality`

## Use When

- a data pipeline must be designed from requirements or a feature brief
- DAG structure, stages, retries, and dependencies are not yet explicit
- you need a project-local design artifact instead of an ad-hoc sketch

## Inputs

- a short description or requirements file
- known sources, sinks, cadence, and SLA assumptions
- platform hints such as Airflow, Spark, dbt, or warehouse target

## Procedure

1. Route to `pipeline-architect` first.
2. Read the relevant feature artifact under `.agentcodex/features/` when it exists.
3. Load `orchestration`, `airflow`, and any required platform domains before proposing structure.
4. Produce task boundaries, dependency order, retries, idempotency expectations, and quality gates.
5. Escalate Spark-heavy transforms to `spark-engineer` and dbt model execution to `dbt-specialist`.
6. Record the outcome in a design artifact or build report, not in hidden session state.

## Outputs

- pipeline structure
- task graph and dependency notes
- retry and failure-handling guidance
- implementation handoff for build work
