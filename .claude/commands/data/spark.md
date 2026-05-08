# /spark — Databricks Spark & PySpark Expert

Activate the Spark specialist for PySpark, Spark SQL, DLT pipelines, and Delta Lake operations
on Databricks and Microsoft Fabric.

## Usage

```
/spark <task>
/spark "create a Bronze→Silver pipeline with Auto Loader"
/spark "optimize this PySpark join for skew"
/spark "implement SCD Type 2 in LakeFlow"
```

## What This Does

Delegates to `@databricks-spark-expert` with context from:
- `kb/spark/` — PySpark and Spark SQL patterns (agentspec)
- `kb/lakeflow/` — DLT and LakeFlow patterns (agentspec)
- `kb/databricks/` — Databricks-specific patterns
- `kb/fabric/` — Fabric Spark Notebook patterns
- `kb/doma-protocol/` — DOMA orchestration patterns

## Task Routing

| Task | What happens |
|------|-------------|
| PySpark DataFrames | `@databricks-spark-expert` generates optimized PySpark code |
| DLT / LakeFlow | Agent applies `kb/lakeflow/` declarative pipeline patterns |
| Spark SQL | Agent may involve `@databricks-sql-expert` for SQL generation |
| Fabric Notebooks | Agent applies `kb/fabric/` Spark notebook patterns |

## DOMA Protocol

1. KB-First: Read `kb/spark/index.md` → identify patterns for the task type
2. Platform isolation: Never mix Databricks and Fabric code in the same cell
3. Include KB provenance and confidence score in response

## References

- Agent: `agents/data-engineering/databricks-spark-expert.md`
- KB: `kb/spark/`, `kb/lakeflow/`, `kb/databricks/`, `kb/fabric/`
