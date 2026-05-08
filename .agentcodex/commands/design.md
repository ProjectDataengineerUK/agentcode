# Design

## Purpose

Create architecture and technical specification from validated requirements. This is Phase 2 of the AgentCodex workflow and is the Codex-native port of AgentSpec's `design` procedure.

Use this only after a `DEFINE_{FEATURE}.md` artifact exists and has passed the clarity gate.

## Primary Role

- workflow-designer

## Inputs

- `.agentcodex/features/DEFINE_{FEATURE}.md`
- related `.agentcodex/features/BRAINSTORM_{FEATURE}.md`
- repository evidence
- `.agentcodex/kb/` domains named in define
- system, platform, security, and operational constraints

## Procedure

### Step 1: Load Context

Read:

- `AGENTS.md`
- `.agentcodex/templates/DESIGN_TEMPLATE.md`
- `.agentcodex/features/DEFINE_{FEATURE}.md`
- relevant `.agentcodex/kb/{domain}/` concepts, patterns, specs, and quick references
- current code/docs/tests related to the feature
- available role docs under `docs/roles/`

Do not design from scratch when local KB or codebase patterns exist.

### Step 2: Create Architecture

Design the solution with:

- ASCII system diagram
- component table
- system or data flow
- integration points
- deployment/runtime boundaries

### Step 3: Document Decisions

For every significant design choice, write an inline ADR:

- context
- choice
- rationale
- alternatives rejected
- consequences

### Step 4: Create File Manifest

List every file or module to create or modify:

- file path
- action
- purpose
- recommended role/agent
- dependencies

Each major file needs a purpose and dependency context. Build should not start without this manifest.

### Step 5: Assign Roles

Match work to available AgentCodex roles based on:

- file type
- path pattern
- purpose keywords
- KB domains
- platform/tool specialization

Use `(general)` only when no specialized role is appropriate.

### Step 6: Define Code Patterns

Provide implementation patterns that are ready to reuse:

- handler or service structure
- config structure
- data/model/schema pattern
- testing fixtures or validation pattern

Patterns should be grounded in `.agentcodex/kb/` and current repo conventions.

### Step 7: Plan Testing and Operations

Define:

- unit tests
- integration tests
- E2E or smoke tests
- data-quality checks when applicable
- error handling
- configuration
- security considerations
- observability

### Step 8: Add Pipeline Architecture When Applicable

If define contains data engineering context, include:

- DAG diagram
- partition strategy
- incremental strategy
- schema evolution plan
- data quality gates

### Step 9: Save the Artifact

Write:

- `.agentcodex/features/DESIGN_{FEATURE}.md`

Use:

- `.agentcodex/templates/DESIGN_TEMPLATE.md`

## Outputs

- `.agentcodex/features/DESIGN_{FEATURE}.md`
- architecture diagram
- inline ADRs
- complete file manifest
- role assignment rationale
- code patterns
- testing strategy
- security, configuration, error handling, and observability notes
- pipeline architecture when applicable

## Quality Gate

Do not mark design complete until:

- [ ] KB patterns loaded from define's domains
- [ ] architecture diagram is clear
- [ ] components are listed
- [ ] at least one decision has full rationale
- [ ] file manifest is complete
- [ ] role assigned to each file or explicitly marked `(general)`
- [ ] code patterns are concrete enough to implement
- [ ] testing strategy covers acceptance tests
- [ ] error handling is explicit
- [ ] configuration is explicit
- [ ] security considerations are documented
- [ ] observability is documented
- [ ] pipeline architecture is included when data engineering context exists
- [ ] no circular dependencies are introduced

## Handoff

Move to `build` only when the file manifest, design decisions, and verification expectations are complete.

Next artifact:

- `.agentcodex/reports/BUILD_REPORT_{FEATURE}.md`

