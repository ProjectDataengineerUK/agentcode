# /pipeline — Data Pipeline Design Assistant

Design and implement data pipelines for Databricks (DLT/LakeFlow, Jobs) and Microsoft Fabric
(Data Factory, Notebooks), following the Medallion architecture and DOMA protocol.

## Usage

```
/pipeline <pipeline description>
/pipeline "ingest raw CSV from ADLS into Bronze Delta table with Auto Loader"
/pipeline "build Silver transformation for orders with SCD Type 2"
/pipeline "orchestrate a 5-step Databricks Jobs workflow with error handling"
/pipeline "create a Fabric Data Factory pipeline to sync from Azure SQL to Lakehouse"
```

## What This Does

Delegates to `@fabric-pipeline-expert` with full DOMA context:

1. **Platform detection** — Databricks (DLT/LakeFlow/Jobs) vs Fabric (Data Factory/Notebooks)
2. **KB-First** — Reads `kb/doma-protocol/patterns/medallion-patterns.md` for the relevant layer
3. **Design** — Generates pipeline code, YAML, or JSON with error handling patterns
4. **Validation** — Checks against `kb/guardrails/constitution.md` before output

## Layer-Specific Guidance

| Layer | Databricks | Fabric |
|-------|-----------|--------|
| Bronze (raw) | Auto Loader + DLT streaming table | Data Factory Copy + Lakehouse |
| Silver (clean) | DLT with APPLY CHANGES (CDC) | Fabric Notebook + Delta |
| Gold (aggregated) | Spark SQL materializations | Fabric SQL Analytics Endpoint |

## Output Includes

- Pipeline code (DLT Python / Data Factory JSON / Databricks Jobs YAML)
- Schema of input/output tables
- Error handling and retry patterns
- Monitoring/alerting recommendations
- KB provenance + confidence score

## References

- Agent: `agents/data-engineering/fabric-pipeline-expert.md`
- KB: `kb/doma-protocol/`, `kb/lakeflow/`, `kb/databricks/`, `kb/fabric/`
