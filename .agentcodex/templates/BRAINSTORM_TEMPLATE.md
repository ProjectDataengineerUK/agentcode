# BRAINSTORM: {Feature Name}

> Exploratory session to clarify intent and approach before requirements capture.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | `{FEATURE}` |
| **Date** | `{DATE}` |
| **Owner** | `{OWNER}` |
| **Authoring Role** | `workflow-brainstormer` |
| **Status** | Exploring / Approaches Identified / Ready for Define |

## Initial Idea

**Raw Input:** {Original idea or request as stated by user}

**Context Gathered:**

- {Project state observation 1}
- {Project state observation 2}
- {Relevant existing code, data, docs, or patterns found}

**Technical Context Observed for Define:**

| Aspect | Observation | Implication |
|--------|-------------|-------------|
| Likely Location | {src/ \| functions/ \| gen/ \| deploy/ \| docs/ \| N/A} | {Where work should live} |
| Relevant KB Domains | {domain-1, domain-2, etc.} | {Patterns to consult} |
| Existing Patterns | {Existing code/docs/IaC/tooling or N/A} | {Reuse or divergence notes} |

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|----------|--------|--------|
| 1 | {Question about purpose} | {User answer} | {How this shapes the solution} |
| 2 | {Question about users/stakeholders} | {User answer} | {How this shapes the solution} |
| 3 | {Question about constraints or success} | {User answer} | {How this shapes the solution} |
| 4 | {Optional follow-up question} | {User answer} | {How this shapes the solution} |

**Minimum Questions:** 3.

## Sample Data Inventory

> Samples improve LLM accuracy through in-context learning and few-shot prompting.

| Type | Location | Count | Notes |
|------|----------|-------|-------|
| Input files | {Path or N/A} | {N} | {Format, size, patterns} |
| Output examples | {Path or N/A} | {N} | {Schema, structure} |
| Ground truth | {Path or N/A} | {N} | {Verified correct values} |
| Requirements or reference docs | {Path or N/A} | {N} | {Rules, constraints, examples} |
| Related code | {Path or N/A} | {N} | {Patterns to reuse} |

**How samples will be used:**

- {e.g., few-shot examples in extraction prompts}
- {e.g., schema validation reference}
- {e.g., test fixtures for validation}

**If no samples exist:** record the confidence impact and what should be collected before `define` or `design`.

## Candidate Approaches

### Approach A: {Name} - Recommended

**Description:** {Brief description of approach}

**Pros:**

- {Advantage 1}
- {Advantage 2}

**Cons:**

- {Trade-off 1}
- {Trade-off 2}

**Operational Cost:** {Runtime, maintenance, data, model, or team cost}

**Evidence:** {KB pattern, codebase precedent, sample evidence, or user constraint}

**Confidence:** {0.70-0.95 with reason}

**Why Recommended:** {Clear reasoning for why this is the suggested path}

### Approach B: {Name}

**Description:** {Brief description of approach}

**Pros:**

- {Advantage 1}
- {Advantage 2}

**Cons:**

- {Trade-off 1}
- {Trade-off 2}

**Operational Cost:** {Runtime, maintenance, data, model, or team cost}

**Why Not Recommended:** {Reasoning or condition where it would become better}

### Approach C: {Name} (Optional)

**Description:** {Brief description of approach}

**Pros:**

- {Advantage 1}

**Cons:**

- {Trade-off 1}

**When to Choose:** {Condition where this approach is appropriate}

## Data Engineering Context (if applicable)

> Include this section when the feature involves data pipelines, ETL, analytics, warehouses, lakehouse, streaming, data quality, contracts, or data infrastructure.

### Source Systems

| Source | Type | Volume Estimate | Current Freshness | Notes |
|--------|------|-----------------|-------------------|-------|
| {Source 1} | {Postgres / Kafka / S3 / API / file / app} | {rows/day or GB} | {real-time / daily / unknown} | {Known constraint} |

### Data Flow Sketch

```text
[Source A] -> [Ingestion] -> [Raw] -> [Transform] -> [Quality Gate] -> [Consumer]
```

### Key Data Questions Explored

| # | Question | Answer | Impact |
|---|----------|--------|--------|
| 1 | What is the expected data volume? | {Answer} | {Affects tool choice} |
| 2 | What freshness SLA is needed? | {Answer} | {Batch vs streaming} |
| 3 | Who consumes the output? | {Answer} | {Modeling or serving approach} |
| 4 | Which contracts or lineage expectations exist? | {Answer} | {Define/design gate} |

## Selected Approach

| Attribute | Value |
|-----------|-------|
| **Chosen** | Approach {A/B/C} |
| **User Confirmation** | {Date/time or conversation reference} |
| **Reasoning** | {Why user selected this approach} |

## Recommendation

Recommended direction and rationale, including confidence, main tradeoffs, and why the rejected alternatives are not the first choice.

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|----------|-----------|----------------------|
| 1 | {Decision made during brainstorm} | {Why} | {What was not chosen} |
| 2 | {Decision made during brainstorm} | {Why} | {What was not chosen} |

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed | Can Add Later? |
|-------------------|----------------|----------------|
| {Feature that seemed useful but unnecessary now} | {YAGNI reasoning} | Yes/No |
| {Another deferred feature} | {Why not needed now} | Yes/No |

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---------|-----------|---------------|-----------|
| Problem framing | Yes/No | {Feedback} | Yes/No |
| Approach comparison | Yes/No | {Feedback} | Yes/No |
| Data flow or architecture concept | Yes/No | {Feedback} | Yes/No |
| Scope and YAGNI | Yes/No | {Feedback} | Yes/No |

**Minimum Validations:** 2.

## Suggested Requirements for Define

Based on this brainstorm session, capture the following in `DEFINE_{FEATURE}.md`.

### Problem Statement (Draft)

{One clear sentence describing the problem to solve}

### Target Users (Draft)

| User | Pain Point |
|------|------------|
| {User 1} | {Pain} |

### Success Criteria (Draft)

- [ ] {Measurable criterion 1}
- [ ] {Measurable criterion 2}

### Constraints Identified

- {Constraint 1}
- {Constraint 2}

### Out of Scope (Confirmed)

- {Item 1 explicitly excluded during brainstorm}
- {Item 2 explicitly excluded during brainstorm}

## Session Summary

| Metric | Value |
|--------|-------|
| Questions Asked | {N} |
| Approaches Explored | {2-3} |
| Features Removed (YAGNI) | {N} |
| Validations Completed | {N} |
| Samples Reviewed | {N or none} |
| Duration | {Approximate time} |

## Exit Check

- [ ] minimum 3 discovery questions asked
- [ ] sample collection question asked
- [ ] at least 2 approaches explored
- [ ] relevant KB domains identified for define
- [ ] YAGNI applied and removed/deferred features documented
- [ ] minimum 2 validation checkpoints completed
- [ ] selected approach confirmed by user
- [ ] draft requirements included for define

## Next Step

**Ready for:** `define` using `.agentcodex/features/BRAINSTORM_{FEATURE}.md`.
