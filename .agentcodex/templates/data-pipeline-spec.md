# Data Pipeline Spec

## Purpose

Define a Codex-first, file-based pipeline specification before implementation.

## Owner

- [owner]

## Local Artifact Paths

- feature root: `.agentcodex/features/[feature]/`
- related context: `.agentcodex/history/`
- related reports: `.agentcodex/reports/`

## Validation Command

```bash
python3 scripts/agentcodex.py validate
```

## Overview

| Field | Value |
|-------|-------|
| Name | [pipeline-name] |
| Objective | [what problem the pipeline solves] |
| Platform | [databricks / fabric / cross-platform / other] |
| Environment | [dev / staging / prod] |
| Owner | [team or person] |

## Source Data

| Source | Format | Ingestion Method | Frequency | Notes |
|--------|--------|------------------|-----------|-------|
| [source] | [csv/json/parquet/api/stream] | [autoload/api/batch/stream] | [cadence] | [notes] |

## Transformations

| Layer | Target | Inputs | Core Transformations | Notes |
|-------|--------|--------|----------------------|-------|
| Bronze | [table] | [sources] | [raw landing only] | [notes] |
| Silver | [table] | [bronze] | [cleaning/typing/dedup] | [notes] |
| Gold | [table] | [silver] | [business aggregation/modeling] | [notes] |

## Quality Controls

| Layer | Rule | Enforcement | Severity |
|-------|------|-------------|----------|
| [layer] | [quality rule] | [warn/drop/fail] | [critical/high/medium] |

## Orchestration

| Field | Value |
|-------|-------|
| Runtime | [airflow / workflows / data factory / other] |
| Trigger | [schedule/event/manual] |
| Retry Policy | [retries/backoff] |
| Alerts | [email/webhook/teams/slack] |

## Architecture Patterns

- [pattern 1]
- [pattern 2]

## Agent Implications

- preferred role: `pipeline-architect`
- escalations: `spark-engineer`, `data-quality-analyst`, `data-platform-engineer`

## MCP Implications

- required MCP surfaces: [if any]
- read-only vs write operations: [notes]

## Tradeoffs

- [tradeoff 1]
- [tradeoff 2]

## References

- [local kb page]
- [decision record]

## Local Notes

- [repo-local implementation notes]
