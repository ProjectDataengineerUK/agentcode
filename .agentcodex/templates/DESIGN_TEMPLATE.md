# DESIGN: {Feature Name}

> Technical design for implementing `{FEATURE}`.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | `{FEATURE}` |
| **Date** | `{DATE}` |
| **Owner** | `{OWNER}` |
| **Authoring Role** | `workflow-designer` |
| **DEFINE** | `.agentcodex/features/DEFINE_{FEATURE}.md` |
| **Status** | Draft / Ready for Build |

## KB Patterns Loaded

| Domain | Files Reviewed | Patterns Applied |
|--------|----------------|------------------|
| {domain-1} | `{path}` | {Pattern or concept} |
| {domain-2} | `{path}` | {Pattern or concept} |

## Architecture Overview

```text
+-----------------------------------------------------+
|                   SYSTEM DIAGRAM                    |
+-----------------------------------------------------+
|                                                     |
|  {ASCII diagram showing components and data flow}   |
|                                                     |
|  [Input] -> [Component A] -> [Component B] -> [Out] |
|                |                 |                  |
|             [Store]        [External API]           |
|                                                     |
+-----------------------------------------------------+
```

## Components

| Component | Purpose | Technology | Owner/Role |
|-----------|---------|------------|------------|
| {Component A} | {What it does} | {Tech stack} | {Role} |
| {Component B} | {What it does} | {Tech stack} | {Role} |
| {Component C} | {What it does} | {Tech stack} | {Role} |

## Key Decisions

### Decision 1: {Decision Name}

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | `{DATE}` |

**Context:** {Why this decision was needed}

**Choice:** {What is being done}

**Rationale:** {Why this approach}

**Alternatives Rejected:**

1. {Option A} - rejected because {reason}
2. {Option B} - rejected because {reason}

**Consequences:**

- {Trade-off accepted}
- {Benefit gained}

### Decision 2: {Decision Name}

{Repeat the structure above when another significant choice exists.}

## File Manifest

| # | File | Action | Purpose | Agent/Role | Dependencies |
|---|------|--------|---------|------------|--------------|
| 1 | `{path/to/file.py}` | Create / Modify | {Purpose} | @{role-name} | None |
| 2 | `{path/to/config.yaml}` | Create / Modify | {Purpose} | @{role-name} | None |
| 3 | `{path/to/handler.py}` | Create / Modify | {Purpose} | @{role-name} | 1, 2 |
| 4 | `{path/to/test.py}` | Create / Modify | {Purpose} | @{role-name} | 3 |

**Total Files:** {N}

## Agent Assignment Rationale

| Agent/Role | Files Assigned | Why This Agent |
|------------|----------------|----------------|
| @{role-1} | 1, 3 | {Specialization match} |
| @{role-2} | 2 | {Specialization match} |
| @{role-3} | 4 | {Specialization match} |
| (general) | {if any} | {No specialist found} |

**Matched By:**

- file type
- purpose keywords
- path patterns
- KB domains
- platform or tool specialization

## Code Patterns

### Pattern 1: {Pattern Name}

```python
# {Brief description of when to use this pattern}

{Copy-paste ready code snippet}
```

### Pattern 2: {Pattern Name}

```python
{Copy-paste ready code snippet}
```

### Pattern 3: Configuration Structure

```yaml
# config.yaml structure
{YAML configuration template}
```

## Data Flow

```text
1. {Step 1}
   |
   v
2. {Step 2}
   |
   v
3. {Step 3}
   |
   v
4. {Step 4}
```

## Integration Points

| External System | Integration Type | Authentication | Failure Mode |
|-----------------|------------------|----------------|--------------|
| {System A} | {REST API / SDK / Queue / DB} | {Method} | {How failures surface} |
| {System B} | {REST API / SDK / Queue / DB} | {Method} | {How failures surface} |

## Testing Strategy

| Test Type | Scope | Files | Tools | Coverage Goal |
|-----------|-------|-------|-------|---------------|
| Unit | Functions/classes | `{test files}` | {test framework} | {Target} |
| Integration | APIs, DBs, queues, tools | `{test files}` | {framework + mocks/services} | Key paths |
| E2E / Smoke | Full user/data flow | `{test files or manual}` | {tool} | Happy path and critical failure |
| Data Quality | Contracts/freshness/completeness | `{test files/specs}` | {dbt / GE / custom} | Required gates |

## Error Handling

| Error Type | Handling Strategy | Retry? | User/Operator Signal |
|------------|-------------------|--------|----------------------|
| {Error A} | {How to handle} | Yes/No | {Message, log, alert} |
| {Error B} | {How to handle} | Yes/No | {Message, log, alert} |
| {Error C} | {How to handle} | Yes/No | {Message, log, alert} |

## Configuration

| Config Key | Type | Default | Description |
|------------|------|---------|-------------|
| `{key_1}` | string | `{default}` | {What it controls} |
| `{key_2}` | int | `{default}` | {What it controls} |
| `{key_3}` | bool | `{default}` | {What it controls} |

## Security Considerations

- {Authentication/authorization consideration}
- {Secrets handling consideration}
- {PII/data classification consideration}
- {Input validation or file/path handling consideration}

## Observability

| Aspect | Implementation |
|--------|----------------|
| Logging | {Structured logs, key fields, retention} |
| Metrics | {Counters, gauges, SLIs/SLOs} |
| Tracing | {Trace/span plan or N/A with reason} |
| Alerts | {Failure/latency/freshness alerts} |
| Runbook | {Operator response or link} |

## Pipeline Architecture (if applicable)

> Include this section when the feature involves data pipelines, ETL, analytics, freshness, lineage, schemas, contracts, or data quality.

### DAG Diagram

```text
[Source A] --extract--> [Raw Layer] --transform--> [Staging] --model--> [Marts]
[Source B] --extract--^       |                       |              |
                           [Archive]            [Quality Gate]   [Consumer]
```

### Partition Strategy

| Table | Partition Key | Granularity | Rationale |
|-------|---------------|-------------|-----------|
| {table_1} | {column} | {daily / monthly / none} | {Query patterns, volume} |

### Incremental Strategy

| Model | Strategy | Key Column | Lookback |
|-------|----------|------------|----------|
| {model_1} | {incremental_by_time / unique_key / full_refresh} | {column} | {N days} |

### Schema Evolution Plan

| Change Type | Handling | Rollback |
|-------------|----------|----------|
| New column | {Add with default, backfill async} | {Drop column or ignore} |
| Type change | {Dual-write period, then migrate} | {Revert type} |
| Column removal | {Deprecate in contract, remove after N days} | {Re-add column} |

### Data Quality Gates

| Gate | Tool | Threshold | Action on Failure |
|------|------|-----------|-------------------|
| {Null check on PKs} | {dbt test / GE / custom} | {0 nulls} | {Block pipeline} |
| {Row count delta} | {dbt test / GE / custom} | {<10% variance} | {Alert + continue/block} |
| {Freshness check} | {dbt source freshness / custom} | {< N hours} | {Alert/block} |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| {Risk 1} | Low/Med/High | Low/Med/High | {Mitigation} |
| {Risk 2} | Low/Med/High | Low/Med/High | {Mitigation} |

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | `{DATE}` | workflow-designer | Initial version |

## Exit Check

- [ ] KB patterns loaded from define's domains
- [ ] architecture diagram is clear
- [ ] components are listed
- [ ] major decisions documented with rationale
- [ ] file manifest is complete
- [ ] role assigned to each file or marked `(general)`
- [ ] code patterns are concrete enough to implement
- [ ] testing strategy covers acceptance tests
- [ ] error handling is explicit
- [ ] configuration is explicit
- [ ] security considerations are documented
- [ ] observability is documented
- [ ] pipeline architecture included when applicable
- [ ] no circular dependencies introduced

## Next Step

**Ready for:** `build` using `.agentcodex/features/DESIGN_{FEATURE}.md`.

