# Schema Procedure

## Purpose

Codex-native replacement for AgentSpec's `/schema` command.

## Primary Role

- `schema-designer`

## Escalation Roles

- `dbt-specialist`
- `sql-optimizer`
- `data-contracts-engineer`

## KB Domains

- `data-modeling`
- `sql-patterns`
- `data-quality`

## Use When

- dimensional modeling or schema boundaries are still unclear
- grain, keys, SCD behavior, or normalization need explicit design
- implementation needs a durable design artifact before SQL or dbt work begins

## Inputs

- source entities or upstream models
- target consumption pattern
- latency, history, and compatibility constraints

## Procedure

1. Route to `schema-designer`.
2. Define grain, keys, cardinality, and lifecycle assumptions before writing DDL.
3. Use `data-modeling` and `sql-patterns` KB material to choose schema shape deliberately.
4. Escalate dbt implementation details to `dbt-specialist` and SQL tuning to `sql-optimizer`.
5. If the schema is externally consumed, escalate contract concerns to `data-contracts-engineer`.
6. Store the result in a design artifact with schema rationale, not only generated SQL.

## Outputs

- schema design and grain definition
- DDL or model structure guidance
- compatibility and evolution notes
- implementation handoff for dbt or SQL work
