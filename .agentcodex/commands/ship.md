# Ship

## Purpose

Archive a completed feature with verification evidence and lessons learned. This is Phase 4 of the AgentCodex workflow and is the Codex-native port of AgentSpec's `ship` procedure.

Use this only when build is complete, verification has passed, and the feature is ready to archive.

If a user asks for `/ship`, treat it as this Codex-native procedure. Do not assume a Claude slash-command runtime exists.

## Primary Role

- workflow-shipper

## Inputs

- `.agentcodex/features/BRAINSTORM_{FEATURE}.md` when Phase 0 was used
- `.agentcodex/features/DEFINE_{FEATURE}.md`
- `.agentcodex/features/DESIGN_{FEATURE}.md`
- `.agentcodex/reports/BUILD_REPORT_{FEATURE}.md`
- acceptance criteria from define
- verification/test results
- readiness and ship-gate results when project-standard blocks apply

## Procedure

### Step 1: Verify Completion

Read and verify:

- `.agentcodex/features/DEFINE_{FEATURE}.md`
- `.agentcodex/features/DESIGN_{FEATURE}.md`
- `.agentcodex/reports/BUILD_REPORT_{FEATURE}.md`
- `.agentcodex/features/BRAINSTORM_{FEATURE}.md` if it exists

Confirm:

- build report shows 100% completion or explicitly justified exceptions
- build report is not an example/scaffold-only artifact
- all tests pass or exceptions are documented and accepted
- no blocking issues remain
- acceptance criteria from define are reviewed
- delivered work matches or explicitly deviates from design

### Step 2: Run Final Gates

When the target is an AgentCodex-standard project, run:

```bash
python3 scripts/agentcodex.py readiness-report <target-project-dir>
python3 scripts/agentcodex.py ship-gate <target-project-dir>
```

Do not mark shipped while required project-standard blocks remain incomplete unless an explicit exception is documented.

If the gates pass but the feature artifacts are not shippable, for example because `BUILD_REPORT_{FEATURE}.md` is marked `status: example` or says no verification commands were executed, do not create a shipped archive. Instead, write a repo-local gate report under `.agentcodex/reports/ship-run-{DATE}.md` explaining:

- commands run
- readiness and ship-gate result
- candidate feature artifacts reviewed
- blocking reason
- follow-up needed before archive

### Step 3: Create Archive Folder

Create:

- `.agentcodex/archive/{FEATURE}/`

### Step 4: Copy Artifacts to Archive

Archive all available workflow artifacts:

- `BRAINSTORM_{FEATURE}.md` when present
- `DEFINE_{FEATURE}.md`
- `DESIGN_{FEATURE}.md`
- `BUILD_REPORT_{FEATURE}.md`
- `SHIPPED_{DATE}.md`

### Step 5: Generate SHIPPED Document

Write:

- `.agentcodex/archive/{FEATURE}/SHIPPED_{DATE}.md`

Use:

- `.agentcodex/templates/SHIPPED_TEMPLATE.md`

Include:

- summary
- timeline
- metrics
- what was built
- success criteria verification
- lessons learned
- future recommendations
- archived artifacts
- readiness and ship-gate results

### Step 6: Update Status and Clean Up

Update archived documents to shipped status when possible.

Clean working files only after archive copies are verified. Do not delete source artifacts if the project policy requires keeping active feature files; document the chosen retention policy in the shipped artifact.

## Outputs

- `.agentcodex/archive/{FEATURE}/SHIPPED_{DATE}.md`
- archived copies of workflow artifacts
- final success criteria verification
- lessons learned
- residual risk and follow-up list

## Quality Gate

Do not mark ship complete until:

- [ ] DEFINE document exists
- [ ] DESIGN document exists
- [ ] BUILD_REPORT exists
- [ ] build report shows completion
- [ ] build report is not example/scaffold-only evidence
- [ ] all required tests pass or accepted exceptions are documented
- [ ] no blocking issues remain
- [ ] acceptance criteria are verified
- [ ] archive directory exists
- [ ] artifacts copied to archive
- [ ] at least 2 specific lessons documented
- [ ] readiness/ship-gate result recorded when applicable
- [ ] working-file retention or cleanup policy documented

## Handoff

After shipping, the next step is either:

- start a new feature with `brainstorm` or `define`
- open follow-up work from the shipped artifact's recommendations

If ship was blocked, the next step is to update the build report with real implementation and verification evidence, then re-run this procedure.
