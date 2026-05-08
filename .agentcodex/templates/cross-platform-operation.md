# Cross-Platform Operation

## Purpose

Define a data operation that spans two platforms with explicit movement, compatibility, and control rules.

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
| Operation Name | [name] |
| Objective | [goal] |
| Direction | [platform A -> platform B / bidirectional] |
| Environment | [dev / staging / prod] |
| Type | [migration / sync / share / replication] |

## Asset Inventory

| Asset | Source Platform | Source Location | Target Platform | Target Location |
|-------|-----------------|-----------------|-----------------|-----------------|
| [asset] | [platform] | [location] | [platform] | [location] |

## Connectivity Strategy

| Option | Selected | Why |
|--------|----------|-----|
| shared storage | [yes/no] | [reason] |
| zero-copy shortcut | [yes/no] | [reason] |
| replication/mirroring | [yes/no] | [reason] |
| api export/import | [yes/no] | [reason] |

## Dialect Compatibility

| Concern | Platform A | Platform B | Action |
|---------|------------|------------|--------|
| DDL | [dialect] | [dialect] | [conversion approach] |
| Querying | [dialect] | [dialect] | [conversion approach] |
| Quality | [mechanism] | [mechanism] | [bridge] |

## Security and Governance

| Concern | Requirement | Action |
|---------|-------------|--------|
| Auth | [requirement] | [action] |
| Authz | [requirement] | [action] |
| PII | [requirement] | [action] |
| Audit | [requirement] | [action] |

## Orchestration

| Field | Value |
|-------|-------|
| Runtime | [tool] |
| Trigger | [trigger] |
| Monitoring | [monitoring path] |
| Alerts | [alert path] |

## Architecture Patterns

- [pattern 1]
- [pattern 2]

## Agent Implications

- preferred role: `data-platform-engineer`
- escalations: `databricks-architect`, `fabric-architect`, `data-governance-architect`

## MCP Implications

- MCP surfaces involved: [if any]
- write permissions needed: [notes]

## Tradeoffs

- [tradeoff 1]
- [tradeoff 2]

## References

- [related kb page]
- [related decision record]

## Local Notes

- [repo-local notes]
