# Data Contract Procedure

## Purpose

Codex-native replacement for AgentSpec's `/data-contract` command.

## Primary Role

- `data-contracts-engineer`

## Escalation Roles

- `data-quality-analyst`
- `schema-designer`
- `dbt-specialist`

## KB Domains

- `data-quality`
- `data-modeling`

## Use When

- a producer-consumer agreement must be documented explicitly
- SLAs, freshness, completeness, or change policy need a formal contract
- downstream consumers need stable expectations for schema and data behavior

## Inputs

- dataset or model name
- owners and consuming teams
- schema expectations and SLA targets
- known breaking-change constraints

## Procedure

1. Route to `data-contracts-engineer`.
2. Define ownership, versioning, and compatibility policy before drafting rules.
3. Specify measurable SLAs for freshness, completeness, volume, or latency.
4. Escalate rule enforcement to `data-quality-analyst` and schema redesign to `schema-designer`.
5. If the contract must be implemented as dbt tests, escalate that step to `dbt-specialist`.
6. Store the contract as a project artifact, with change policy and migration notes.

## Outputs

- contract draft
- SLA and quality commitments
- breaking-change policy
- implementation handoff for enforcement
