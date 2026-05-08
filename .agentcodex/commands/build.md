# Build

## Purpose

Execute implementation from a validated design with incremental verification. This is Phase 3 of the AgentCodex workflow and is the Codex-native port of AgentSpec's `build` procedure.

Use this only after `DESIGN_{FEATURE}.md` exists and includes a complete file manifest.

## Primary Role

- workflow-builder

## Inputs

- `.agentcodex/features/DESIGN_{FEATURE}.md`
- `.agentcodex/features/DEFINE_{FEATURE}.md`
- file manifest and role assignments from design
- code/config/test patterns from design
- KB domains named in design
- repository state and local tooling

## Procedure

### Step 1: Load Context

Read:

- `AGENTS.md`
- `.agentcodex/features/DESIGN_{FEATURE}.md`
- `.agentcodex/features/DEFINE_{FEATURE}.md`
- `.agentcodex/templates/BUILD_REPORT_TEMPLATE.md`
- relevant `.agentcodex/kb/{domain}/` patterns
- current files that will be created or modified

### Step 2: Extract Tasks

Convert the design file manifest into a task list:

- file path
- action
- purpose
- dependencies
- assigned role
- verification needed

### Step 3: Order by Dependencies

Sequence work in dependency order:

1. config and schemas
2. shared utilities
3. core handlers/jobs/models
4. integrations
5. tests and validation specs
6. docs/runbooks if included in design

### Step 4: Execute Each Task

For each task:

1. implement according to the design patterns
2. keep scope within the design
3. use specialist roles when the manifest indicates domain complexity
4. verify the file or component
5. record attribution and result

Major design gaps must go through `iterate`; do not silently redesign during build.

### Step 5: Verify Incrementally

Run relevant checks after meaningful changes:

- lint
- typecheck
- unit tests
- integration tests
- import/smoke checks
- data-engineering checks when applicable

Retry small fixes locally. If a blocker remains, stop and record it.

### Step 6: Run Full Validation

Run the best available project-level validation commands. If a command cannot run, record why.

### Step 7: Record Verification Commands

Record every verification command in `BUILD_REPORT_{FEATURE}.md`, including:

- exact command
- working directory
- result
- skipped checks and why

### Step 8: Generate Build Report

Write:

- `.agentcodex/reports/BUILD_REPORT_{FEATURE}.md`

Use:

- `.agentcodex/templates/BUILD_REPORT_TEMPLATE.md`

## Outputs

- implemented code/config/test/doc changes
- `.agentcodex/reports/BUILD_REPORT_{FEATURE}.md`
- task execution record
- agent/role attribution
- verification results
- deviations from design
- blockers or residual risks

## Quality Gate

Do not mark build complete until:

- [ ] all manifest files are created/modified or explicitly deferred
- [ ] each file has verification status
- [ ] role/agent attribution is recorded
- [ ] lint/type/test commands pass or exceptions are documented
- [ ] no hardcoded secrets or credentials are introduced
- [ ] error cases from design are handled
- [ ] acceptance tests are verified
- [ ] data-quality checks pass when applicable
- [ ] deviations from design are documented
- [ ] build report is generated

## Handoff

Move to `ship` when intended scope is implemented, verification is complete, and residual risk is understood.

Next artifact:

- `.agentcodex/archive/{FEATURE}/SHIPPED_{DATE}.md`
