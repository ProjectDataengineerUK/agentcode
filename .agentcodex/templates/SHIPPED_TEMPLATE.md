# SHIPPED: {Feature Name}

> Feature shipped on `{DATE}`.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | `{FEATURE}` |
| **Ship Date** | `{DATE}` |
| **Owner** | `{OWNER}` |
| **Authoring Role** | `workflow-shipper` |
| **Status** | Shipped / Archived |

## Ship Readiness

| Check | Status | Evidence |
|-------|--------|----------|
| DEFINE exists | Pass / Fail | `.agentcodex/features/DEFINE_{FEATURE}.md` |
| DESIGN exists | Pass / Fail | `.agentcodex/features/DESIGN_{FEATURE}.md` |
| BUILD_REPORT exists | Pass / Fail | `.agentcodex/reports/BUILD_REPORT_{FEATURE}.md` |
| Build complete | Pass / Fail / Exception | {Evidence} |
| Tests passing | Pass / Fail / Exception | {Command/output/link} |
| Blocking issues | None / Present | {Issue refs or notes} |
| Project readiness | Pass / Fail / N/A | {readiness-report result} |
| Ship gate | Pass / Fail / N/A | {ship-gate result} |

## Summary

{One paragraph describing what was built and the business or operational value delivered.}

## Timeline

| Milestone | Date | Duration |
|-----------|------|----------|
| Brainstorm Started | `{DATE or N/A}` | - |
| Define Started | `{DATE}` | {Duration} |
| Define Complete | `{DATE}` | {Duration} |
| Design Complete | `{DATE}` | {Duration} |
| Build Complete | `{DATE}` | {Duration} |
| **Shipped** | `{DATE}` | **Total: {Duration}** |

## Metrics

| Metric | Value |
|--------|-------|
| **Total Files Created** | {N} |
| **Total Files Modified** | {N} |
| **Lines of Code** | {N or N/A} |
| **Tests Written** | {N} |
| **Test Coverage** | {X% or N/A} |
| **Build Iterations** | {N} |
| **Design Decisions** | {N} |
| **Agents/Roles Used** | {N} |

## What Was Built

### Components

| Component | Description |
|-----------|-------------|
| {Component 1} | {What it does} |
| {Component 2} | {What it does} |

### Files

| File | Purpose |
|------|---------|
| `{path/to/file1}` | {Purpose} |
| `{path/to/file2}` | {Purpose} |

## Success Criteria Verification

| Criterion | Target | Actual | Status |
|-----------|--------|--------|--------|
| {From DEFINE} | {Target} | {Actual} | Pass / Fail / Exception |
| {From DEFINE} | {Target} | {Actual} | Pass / Fail / Exception |
| {From DEFINE} | {Target} | {Actual} | Pass / Fail / Exception |

## Acceptance Review

| Acceptance Test | Result | Evidence |
|-----------------|--------|----------|
| AT-001 | Pass / Fail / Exception | {Command, log, manual note} |
| AT-002 | Pass / Fail / Exception | {Command, log, manual note} |

## Deviations From Design

| Design Item | Deviation | Reason | Impact |
|-------------|-----------|--------|--------|
| {Item} | {What changed} | {Why} | {Impact} |

## Lessons Learned

### Process

- {Specific lesson about process}
- {Specific lesson about what should change next time}

### Technical

- {Specific technical insight}
- {Technical challenge and how it was solved}

### Communication

- {Clarification that prevented rework}
- {Confusion that should be avoided next time}

### Tools & Libraries

- {Tool/library and why it helped}
- {Tool/library limitation or caveat}

## Recommendations for Future Work

| Area | Recommendation |
|------|----------------|
| {Area 1} | {Specific recommendation} |
| {Area 2} | {Specific recommendation} |

## Follow-up Work

| Item | Priority | Owner | Notes |
|------|----------|-------|-------|
| {Follow-up 1} | High/Med/Low | {Owner} | {Notes} |

## Final Risk Notes

| Risk | Status | Mitigation / Owner |
|------|--------|--------------------|
| {Risk 1} | Open / Accepted / Closed | {Mitigation} |

## Project Standard Gate

| Gate | Result | Evidence |
|------|--------|----------|
| readiness-report | Pass / Fail / N/A | {Path or command output summary} |
| ship-gate | Pass / Fail / N/A | {Path or command output summary} |
| blocking blocks | {None or list} | {Notes} |

## Archived Artifacts

| Artifact | Location |
|----------|----------|
| BRAINSTORM | `.agentcodex/archive/{FEATURE}/BRAINSTORM_{FEATURE}.md` or N/A |
| DEFINE | `.agentcodex/archive/{FEATURE}/DEFINE_{FEATURE}.md` |
| DESIGN | `.agentcodex/archive/{FEATURE}/DESIGN_{FEATURE}.md` |
| BUILD_REPORT | `.agentcodex/archive/{FEATURE}/BUILD_REPORT_{FEATURE}.md` |
| SHIPPED | `.agentcodex/archive/{FEATURE}/SHIPPED_{DATE}.md` |

## Working File Retention

| Location | Action | Rationale |
|----------|--------|-----------|
| `.agentcodex/features/` | Keep / Remove / N/A | {Policy or reason} |
| `.agentcodex/reports/` | Keep / Remove / N/A | {Policy or reason} |

## Exit Check

- [ ] all required artifacts verified
- [ ] build completion verified
- [ ] tests passing or exceptions documented
- [ ] acceptance criteria reviewed
- [ ] success criteria verified
- [ ] deviations from design documented
- [ ] at least 2 specific lessons captured
- [ ] follow-up work listed
- [ ] final risk notes recorded
- [ ] project-standard ship gate passed or exception documented
- [ ] archive locations recorded

## Status

**Status:** Shipped / Archived.

*Feature archived on `{DATE}` by `workflow-shipper`.*

