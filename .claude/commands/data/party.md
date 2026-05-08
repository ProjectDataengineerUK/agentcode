# /party — Multi-Perspective Data Analysis

Launch a multi-agent analysis party: get parallel expert perspectives on a data engineering
problem from SQL, Spark, governance, and architecture angles simultaneously.

## Usage

```
/party <problem or artifact>
/party "review this pipeline design"
/party "should we use Delta Lake or Iceberg for this use case?"
/party "audit this Databricks job for quality and governance"
```

## What This Does

Orchestrates parallel analysis by invoking multiple specialists via `@doma-supervisor`:

| Perspective | Agent | Analyzes |
|-------------|-------|---------|
| SQL/Data | `@databricks-sql-expert` | Schema quality, query patterns, catalog impact |
| Pipeline | `@fabric-pipeline-expert` | Orchestration, latency, failure modes |
| Governance | `@data-governance-auditor` | PII exposure, lineage, access controls |
| Architecture | `@lakeflow-architect` (agentspec) | Medallion design, layer ownership |

## Output Format

```
🎉 Party Analysis — {topic}

--- SQL/Data perspective ---
{databricks-sql-expert analysis}

--- Pipeline perspective ---
{fabric-pipeline-expert analysis}

--- Governance perspective ---
{data-governance-auditor analysis}

--- Architecture perspective ---
{lakeflow-architect analysis}

--- Synthesis ---
Consensus recommendation + top 3 action items
```

## When to Use

- Design reviews that span multiple domains
- "What could go wrong?" audits before production deployment
- Architecture decisions where trade-offs exist across SQL, pipeline, and governance
- Getting a second (third, fourth) opinion on a complex data engineering decision

## References

- Supervisor: `agents/data-engineering/doma-supervisor.md`
- KB: `kb/doma-protocol/`, `kb/governance/`, `kb/databricks/`, `kb/fabric/`
