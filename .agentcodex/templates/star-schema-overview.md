# Star Schema Overview

## Purpose

Define a Gold-layer star schema in a way that is explicit, auditable, and implementation-ready.

## Owner

- [owner]

## Local Artifact Paths

- target feature: `.agentcodex/features/[feature]/`
- related reports: `.agentcodex/reports/`

## Validation Command

```bash
python3 scripts/agentcodex.py validate
```

## Overview

| Field | Value |
|-------|-------|
| Model Name | [name] |
| Business Domain | [domain] |
| Platform | [databricks / fabric / both] |
| Consumption Layer | [direct lake / sql / semantic / dashboard] |
| Grain | [grain statement] |

## Source Tables

| Source Table | Entity | Volume | Update Cadence |
|--------------|--------|--------|----------------|
| [silver-table] | [entity] | [estimate] | [cadence] |

## Dimensions

| Dimension | Source | Key Strategy | Notes |
|-----------|--------|--------------|-------|
| `dim_date` | generated | synthetic | required |
| `dim_[name]` | [silver] | [natural/surrogate] | [notes] |

## Facts

| Fact Table | Grain | Dimension Links | Metrics |
|------------|-------|-----------------|---------|
| `fact_[name]` | [grain] | [fk list] | [metric list] |

## Quality Controls

| Target | Rule | Enforcement |
|--------|------|-------------|
| [dim/fact] | [rule] | [warn/fail] |

## Architecture Patterns

- dimensional separation between dimensions and facts
- stable join paths with explicit foreign keys

## Agent Implications

- preferred role: `schema-designer`
- escalations: `sql-optimizer`, `data-quality-analyst`, `semantic-modeler`

## MCP Implications

- semantic/modeling surfaces needed: [if any]
- platform-specific constraints: [notes]

## Tradeoffs

- [tradeoff 1]
- [tradeoff 2]

## References

- [related kb page]
- [related decision record]

## Local Notes

- [repo-local notes]
