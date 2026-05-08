# Iterate

## Purpose

Update an existing AgentCodex workflow artifact when requirements, constraints, design assumptions, or implementation findings change mid-stream. This is the Codex-native port of AgentSpec's `iterate` procedure.

Use `iterate` to preserve traceability. To change code during build, update `DESIGN_{FEATURE}.md` first, then rebuild from the updated design.

## Primary Role

- workflow-iterator

## Inputs

- target artifact path:
  - `.agentcodex/features/BRAINSTORM_{FEATURE}.md`
  - `.agentcodex/features/DEFINE_{FEATURE}.md`
  - `.agentcodex/features/DESIGN_{FEATURE}.md`
  - `.agentcodex/reports/BUILD_REPORT_{FEATURE}.md`
- change description
- downstream artifacts, if they already exist
- current repository state when design changes affect implementation

## Procedure

### Step 1: Load Target Document

Read the target artifact and identify its phase:

- `BRAINSTORM_*.md`: Phase 0
- `DEFINE_*.md`: Phase 1
- `DESIGN_*.md`: Phase 2
- `BUILD_REPORT_*.md`: Phase 3 evidence

Do not update a shipped archive as the first source of truth. If shipped work needs revision, update the earliest affected live artifact and record follow-up work.

### Step 2: Classify the Change

Classify the request before editing:

| Change Type | Impact | Example |
|---|---|---|
| additive | low | add PDF input support |
| modifying | medium | change exact search to fuzzy search |
| removing | medium | remove OCR from scope |
| architectural | high | replace the storage or orchestration pattern |

### Step 3: Identify Downstream Documents

Find existing downstream artifacts for the same feature:

- `BRAINSTORM` changes may affect `DEFINE`
- `DEFINE` changes may affect `DESIGN`
- `DESIGN` changes may affect code and `BUILD_REPORT`
- build findings may require updating `DESIGN` before another build

### Step 4: Analyze Cascade Impact

For each downstream artifact, determine whether the change creates:

- stale requirements
- stale success criteria
- stale out-of-scope decisions
- stale architecture decisions
- stale file manifest entries
- stale verification or acceptance evidence

Architectural changes and scope changes require explicit cascade handling before the workflow proceeds.

### Step 5: Choose Cascade Handling

When cascade impact is material, ask the user how to proceed:

```text
This change to {DOCUMENT} affects {DOWNSTREAM}. Choose one:
(a) update the downstream artifact now
(b) update only the target artifact and record the downstream follow-up
(c) show the downstream changes first
```

If the change is additive and no downstream conflict exists, apply it directly and record that no cascade was required.

### Step 6: Apply the Change

Update the earliest affected artifact first.

Record:

- what changed
- why it changed
- who/what requested it
- the change classification
- downstream impact
- follow-up owner when applicable

### Step 7: Bump Revision History

Each updated artifact must include or update:

```markdown
## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | YYYY-MM-DD | workflow-definer | Initial version |
| 1.1 | YYYY-MM-DD | workflow-iterator | Added PDF support |
```

Use `workflow-iterator` as the author for iteration changes unless a specialized role applied the downstream update.

### Step 8: Apply Cascade Updates

If cascade handling is selected, update downstream artifacts in order:

1. `BRAINSTORM`
2. `DEFINE`
3. `DESIGN`
4. code/build report
5. ship follow-up notes

Do not patch code directly for a design change without first updating `DESIGN_{FEATURE}.md`.

## Outputs

- updated target artifact
- updated downstream artifacts, when selected
- revision history entry
- cascade impact note
- explicit follow-up items for unresolved downstream work

## Cascade Rules

| Source | Cascade Target | Typical Impact |
|---|---|---|
| `BRAINSTORM` | `DEFINE` | selected approach, YAGNI, users, constraints |
| `DEFINE` | `DESIGN` | requirements, success criteria, scope, constraints |
| `DESIGN` | code/build | file manifest, patterns, architecture, tests |
| build finding | `DESIGN` | corrected implementation plan before rebuild |

## Quality Gate

Do not mark iteration complete until:

- [ ] target document is loaded and phase is identified
- [ ] change is classified
- [ ] downstream documents are identified
- [ ] cascade impact is assessed
- [ ] user decision is recorded when cascade is material
- [ ] target artifact is updated
- [ ] revision history is bumped
- [ ] downstream updates or follow-ups are recorded
- [ ] code changes, if needed, are routed through updated design and build

## Handoff

Return to the earliest workflow phase that became stale.

Typical handoffs:

- updated `BRAINSTORM`: rerun or refresh `define`
- updated `DEFINE`: rerun or refresh `design`
- updated `DESIGN`: rerun `build`
- updated build evidence: review `ship` readiness again
