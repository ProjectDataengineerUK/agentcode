# /workflow — DOMA Protocol Orchestrator

Activate the DOMA Supervisor to orchestrate a complete data engineering workflow across
Databricks and Microsoft Fabric, following the KB-First + platform isolation protocol.

## Usage

```
/workflow <complex task description>
/workflow "build a complete Bronze→Gold pipeline for order data in Databricks"
/workflow "migrate this SQL Server schema to Fabric Lakehouse"
/workflow "set up data governance for the customer domain"
```

## What This Does

Routes the task through `@doma-supervisor`, which:

1. **Analyzes** the task against `kb/doma-protocol/index.md`
2. **Decomposes** into domain-specific sub-tasks
3. **Routes** each sub-task to the right specialist:
   - SQL → `@databricks-sql-expert`
   - Spark/DLT → `@databricks-spark-expert`
   - Pipelines → `@fabric-pipeline-expert`
   - dbt → `@dbt-fabric-expert`
   - Semantics → `@semantic-modeler`
   - Governance → `@data-governance-auditor`
   - Migration → `@data-migration-expert`
4. **Validates** outputs against DOMA guardrails
5. **Synthesizes** results into a coherent deliverable

## DOMA Guardrails (always enforced)

- Platform isolation: Databricks and Fabric operations never mixed
- KB-First: every specialist reads relevant KB before generating code
- No destructive SQL without explicit user confirmation
- PII exposure limited to 10-row samples
- Confidence < 0.75 → surface uncertainty before proceeding

## When to Use

- Multi-domain tasks spanning SQL + pipelines + governance
- End-to-end feature builds (Bronze to Gold to Semantic Model)
- Any task where you're not sure which specialist to call

## References

- Supervisor: `agents/data-engineering/doma-supervisor.md`
- KB: `kb/doma-protocol/`, `kb/guardrails/constitution.md`
