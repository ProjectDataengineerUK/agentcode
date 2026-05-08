# /sql — Databricks & Fabric SQL Expert

Activate the SQL specialist for Databricks (Spark SQL / Unity Catalog) and Microsoft Fabric
(T-SQL / Fabric RTI / KQL).

## Usage

```
/sql <query-or-problem>
/sql "optimize this Delta table query"
/sql "write a Unity Catalog schema discovery script"
/sql "convert this T-SQL to Spark SQL"
```

## What This Does

Delegates to `@databricks-sql-expert` with context from:
- `kb/sql-patterns/` — Cross-platform SQL patterns (agentspec)
- `kb/databricks/` — Databricks-specific patterns (Unity Catalog, Delta Lake, SQL Warehouse)
- `kb/fabric/` — Microsoft Fabric patterns (T-SQL, Lakehouse, Eventhouse/KQL)
- `kb/doma-protocol/` — DOMA workflow integration

## Platform Detection

The agent will detect the target platform from your query context:

| Keywords | Platform detected | Dialect |
|----------|-------------------|---------|
| Databricks, Unity Catalog, dbx, hive_metastore | Databricks | Spark SQL |
| Fabric, Lakehouse, bronze/silver/gold (Fabric) | Fabric | T-SQL |
| RTI, Eventhouse, KQL, Kusto | Fabric RTI | KQL |
| No platform specified | Ask or default to Spark SQL | — |

## DOMA Protocol

1. KB-First: Read `kb/sql-patterns/index.md` → identify relevant patterns
2. Validate table/schema names before generating DDL
3. Include KB provenance in response

## References

- Agent: `agents/data-engineering/databricks-sql-expert.md`
- KB: `kb/sql-patterns/`, `kb/databricks/`, `kb/fabric/`
