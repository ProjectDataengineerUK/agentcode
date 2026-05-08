# DEFINE: {Feature Name}

> Validated requirements for `{FEATURE}`.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | `{FEATURE}` |
| **Date** | `{DATE}` |
| **Owner** | `{OWNER}` |
| **Authoring Role** | `workflow-definer` |
| **Status** | Draft / In Progress / Needs Clarification / Ready for Design |
| **Clarity Score** | `{X}/15` |

## Input Classification

| Attribute | Value |
|-----------|-------|
| **Input Type** | brainstorm_document / meeting_notes / email_thread / conversation / direct_requirement / mixed_sources |
| **Source Artifact(s)** | {Paths or conversation reference} |
| **Brainstorm Source** | `.agentcodex/features/BRAINSTORM_{FEATURE}.md` or N/A |
| **Preserved Decision** | {Selected approach from brainstorm or N/A} |

## Problem Statement

{1-2 sentences describing the pain point. Be specific about who has the problem and what the impact is.}

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| {User 1} | {Their role} | {What frustrates them} |
| {User 2} | {Their role} | {What frustrates them} |

## Goals

What success looks like, prioritized:

| Priority | Goal |
|----------|------|
| **MUST** | {Primary goal, non-negotiable for MVP} |
| **MUST** | {Another critical goal} |
| **SHOULD** | {Important but deferrable if timeline is tight} |
| **COULD** | {Nice-to-have, cut first if needed} |

**Priority Guide:**

- **MUST** = MVP fails without this
- **SHOULD** = Important, but a workaround exists
- **COULD** = Nice-to-have, cut first if needed

## Success Criteria

Measurable outcomes. Use numbers, percentages, thresholds, SLAs, or explicit observable states:

- [ ] {Metric 1: e.g., handle 1000 requests per minute}
- [ ] {Metric 2: e.g., achieve 99.9% uptime}
- [ ] {Metric 3: e.g., response time under 200ms}

## Acceptance Tests

| ID | Scenario | Given | When | Then |
|----|----------|-------|------|------|
| AT-001 | {Happy path} | {Initial state} | {Action} | {Expected result} |
| AT-002 | {Error case} | {Initial state} | {Action} | {Expected result} |
| AT-003 | {Edge case} | {Initial state} | {Action} | {Expected result} |

## Out of Scope

Explicitly not included in this feature:

- {Item 1: what is not being done}
- {Item 2: what is deferred}
- {Item 3: what is explicitly excluded}

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Technical | {e.g., must use existing database schema} | {How this affects design} |
| Timeline | {e.g., must ship by Q1} | {How this affects scope} |
| Resource | {e.g., no additional infrastructure budget} | {How this affects approach} |
| Security/Compliance | {e.g., PII restrictions} | {Controls needed} |

## Technical Context

> Essential context for design. This prevents misplaced files and missed infrastructure work.

| Aspect | Value | Notes |
|--------|-------|-------|
| **Deployment Location** | {src/ \| functions/ \| gen/ \| deploy/ \| custom path} | {Why this location} |
| **KB Domains** | {Domains from `.agentcodex/kb/` relevant to this feature} | {Which patterns to consult} |
| **IaC Impact** | {New resources \| modify existing \| none \| TBD} | {Infrastructure changes needed} |
| **Runtime/Platform** | {Local / cloud / Databricks / Fabric / Snowflake / other} | {Operational implication} |

**Why This Matters:**

- **Location** -> Design uses the correct project structure.
- **KB Domains** -> Design pulls the correct local patterns from `.agentcodex/kb/`.
- **IaC Impact** -> Infrastructure planning starts before build.

## Data Contract (if applicable)

> Include this section when the feature involves data pipelines, ETL, analytics, warehouses, schemas, data quality, lineage, or contracts.

### Source Inventory

| Source | Type | Volume | Freshness | Owner |
|--------|------|--------|-----------|-------|
| {source_1} | {Postgres / Kafka / S3 / API / file} | {rows/day or GB} | {SLA} | {Team} |

### Schema Contract

| Column | Type | Constraints | PII? |
|--------|------|-------------|------|
| {column_1} | {INT / VARCHAR / DECIMAL} | {NOT NULL, UNIQUE} | Yes/No |

### Freshness SLAs

| Layer | Target | Measurement |
|-------|--------|-------------|
| Raw / Staging | {Within X minutes of source change} | {Timestamp comparison} |
| Marts | {Refreshed by HH:MM UTC daily} | {DAG completion time} |

### Completeness Metrics

- {e.g., 99.9% of source records present within SLA}
- {e.g., zero null primary keys across all models}

### Lineage Requirements

- {e.g., column-level lineage from source to mart}
- {e.g., impact analysis before schema changes}

## Assumptions

Assumptions that could invalidate the design if wrong:

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|------------------|------------|
| A-001 | {e.g., database can handle expected load} | {Would need caching or partitioning} | [ ] |
| A-002 | {e.g., request volume stays under 1000/hour} | {Would need rate limiting or scaling} | [ ] |
| A-003 | {e.g., source schema is stable} | {Would need schema evolution plan} | [ ] |

**Note:** Validate critical assumptions before design. Unvalidated assumptions become design risks.

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | {0-3} | {Why this score} |
| Users | {0-3} | {Why this score} |
| Goals | {0-3} | {Why this score} |
| Success | {0-3} | {Why this score} |
| Scope | {0-3} | {Why this score} |
| **Total** | **{X}/15** | |

**Scoring Guide:**

- 0 = Missing entirely
- 1 = Vague or incomplete
- 2 = Clear but missing details
- 3 = Crystal clear, actionable

**Minimum to proceed:** `12/15`

## Open Questions

{List any remaining questions that need answers before design. If none, state `None - ready for design.`}

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | `{DATE}` | workflow-definer | Initial version |

## Exit Check

- [ ] problem statement is clear and specific
- [ ] at least one user persona has a pain point
- [ ] goals use MoSCoW priorities
- [ ] success criteria are measurable
- [ ] acceptance tests are testable
- [ ] constraints are explicit
- [ ] out of scope is explicit
- [ ] assumptions documented with impact if wrong
- [ ] KB domains identified for design
- [ ] technical context gathered
- [ ] clarity score >= 12/15

## Next Step

**Ready for:** `design` using `.agentcodex/features/DEFINE_{FEATURE}.md`.

