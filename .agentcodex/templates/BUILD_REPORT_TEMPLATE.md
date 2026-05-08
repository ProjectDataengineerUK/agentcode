# BUILD REPORT: {Feature Name}

> Implementation report for `{FEATURE}`.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | `{FEATURE}` |
| **Date** | `{DATE}` |
| **Owner** | `{OWNER}` |
| **Authoring Role** | `workflow-builder` |
| **DEFINE** | `.agentcodex/features/DEFINE_{FEATURE}.md` |
| **DESIGN** | `.agentcodex/features/DESIGN_{FEATURE}.md` |
| **Status** | In Progress / Complete / Blocked |

## Summary

| Metric | Value |
|--------|-------|
| **Tasks Completed** | {X}/{Y} |
| **Files Created** | {N} |
| **Files Modified** | {N} |
| **Lines of Code** | {N or N/A} |
| **Build Time** | {Duration} |
| **Tests Passing** | {X}/{Y} |
| **Agents/Roles Used** | {N} |

## Build Order

| # | File/Task | Dependencies | Reason for Order |
|---|-----------|--------------|------------------|
| 1 | `{path}` | None | {Why first} |
| 2 | `{path}` | 1 | {Why next} |

## Task Execution with Agent Attribution

| # | Task | Agent/Role | Status | Duration | Notes |
|---|------|------------|--------|----------|-------|
| 1 | {Task description} | @{role-name} | Complete / In Progress / Blocked | {Duration} | {Notes} |
| 2 | {Task description} | (direct) | Complete / In Progress / Blocked | {Duration} | {Notes} |

**Agent Key:**

- `@{role-name}` = implemented with specialist role guidance
- `(direct)` = implemented directly by builder using design patterns

## Agent Contributions

| Agent/Role | Files | Specialization Applied |
|------------|-------|------------------------|
| @{role-1} | {N} | {Patterns/KB used} |
| (direct) | {N} | DESIGN patterns only |

## Files Created

| File | Lines | Agent/Role | Verified | Notes |
|------|-------|------------|----------|-------|
| `{path/to/file1.py}` | {N} | @{role-name} | Pass / Fail / N/A | {Notes} |

## Files Modified

| File | Lines Changed | Agent/Role | Verified | Notes |
|------|---------------|------------|----------|-------|
| `{path/to/file2.py}` | {N} | @{role-name} | Pass / Fail / N/A | {Notes} |

## Verification Results

## Verification Commands

```bash
# command list with exact commands run
```

### Lint Check

```text
{Output from linter or "All checks passed" or "N/A - not configured"}
```

**Status:** Pass / Fail / Skipped

### Type Check

```text
{Output from type checker or "All checks passed" or "N/A - not configured"}
```

**Status:** Pass / Fail / Skipped

### Tests

```text
{Output from test runner or summary}
```

| Test | Result |
|------|--------|
| `{test_name}` | Pass / Fail / Skipped |

**Status:** {X}/{Y} Pass / Fail / Skipped

### Additional Verification Commands

| Command | Result | Notes |
|---------|--------|-------|
| `{command}` | Pass / Fail / Skipped | {Notes} |

## Issues Encountered

| # | Issue | Resolution | Time Impact |
|---|-------|------------|-------------|
| 1 | {Description} | {Resolution} | {Impact} |

## Deviations from Design

| Deviation | Reason | Impact | Follow-up Needed? |
|-----------|--------|--------|-------------------|
| {What changed from DESIGN} | {Why it changed} | {Effect} | Yes/No |

## Blockers (if any)

| Blocker | Required Action | Owner |
|---------|-----------------|-------|
| {Description} | {What needs to happen} | {Owner} |

## Acceptance Test Verification

| ID | Scenario | Status | Evidence |
|----|----------|--------|----------|
| AT-001 | {From DEFINE} | Pass / Fail / Exception | {How verified} |
| AT-002 | {From DEFINE} | Pass / Fail / Exception | {How verified} |

## Performance Notes

| Metric | Expected | Actual | Status |
|--------|----------|--------|--------|
| {Metric 1} | {From DEFINE} | {Measured} | Pass / Fail / N/A |

## Security Review

| Check | Result | Notes |
|-------|--------|-------|
| Hardcoded secrets | Pass / Fail / N/A | {Notes} |
| Input validation | Pass / Fail / N/A | {Notes} |
| Access control impact | Pass / Fail / N/A | {Notes} |
| File/path handling | Pass / Fail / N/A | {Notes} |

## Data Quality Results (if applicable)

> Include this section when the build involves data pipelines, dbt models, SQL files, Spark jobs, contracts, or data infrastructure.

### dbt Build Results

```text
{Output from dbt build or "N/A"}
```

**Status:** Pass / Fail / N/A

### SQL Lint Results

```text
{Output from sqlfluff lint or "N/A"}
```

**Status:** Pass / Fail / N/A

### Data Quality Checks

| Check | Tool | Result | Details |
|-------|------|--------|---------|
| {Null PK check} | {dbt test / GE / custom} | Pass / Fail / N/A | {Details} |
| {Freshness} | {dbt source freshness / custom} | Pass / Fail / N/A | {Details} |

### Pipeline Metrics

| Metric | Value |
|--------|-------|
| Models built | {N} |
| Tests passed | {X}/{Y} |
| SQL lint violations | {N} |
| Avg model build time | {Duration} |
| Data freshness | Within SLA / Exceeded / N/A |

## Residual Risks

| Risk | Severity | Owner | Mitigation |
|------|----------|-------|------------|
| {Risk} | Low/Med/High | {Owner} | {Mitigation} |

## Final Status

### Overall: Complete / In Progress / Blocked

## Exit Check

**Completion Checklist:**

- [ ] all tasks from manifest completed or explicitly deferred
- [ ] all files verified
- [ ] all verification checks pass or exceptions documented
- [ ] all tests pass or exceptions documented
- [ ] no blocking issues
- [ ] acceptance tests verified
- [ ] deviations from design documented
- [ ] ready for ship

## Next Step

**If Complete:** `ship` using `.agentcodex/features/DEFINE_{FEATURE}.md`.

**If Blocked:** resolve blockers, then resume `build`.

**If Design Change Needed:** run `iterate` against `DESIGN_{FEATURE}.md`.
