# Data Quality Procedure

## Purpose

Codex-native replacement for AgentSpec's `/data-quality` command.

## Primary Role

- `data-quality-analyst`

## Escalation Roles

- `dbt-specialist`
- `data-contracts-engineer`
- `schema-designer`

## KB Domains

- `data-quality`
- `dbt`
- `data-modeling`

## Use When

- a model, table, or dataset needs explicit checks
- test severity and rule coverage are still undefined
- quality enforcement must be derived from schema, SLAs, or business rules

## Inputs

- model SQL, schema definition, or dataset description
- critical columns and business rules
- SLA or contract expectations when they exist

## Procedure

1. Route to `data-quality-analyst`.
2. Identify key fields, referential assumptions, freshness needs, and volume expectations.
3. Build checks from the local `data-quality` KB before selecting implementation format.
4. Escalate dbt-specific test encoding to `dbt-specialist`.
5. Escalate formal SLA or contract work to `data-contracts-engineer`.
6. Store severity, ownership, and enforcement notes with the generated checks.

## Outputs

- quality rule set
- severity and ownership notes
- dbt, SQL, or framework-specific enforcement handoff
- validation plan for ongoing monitoring
