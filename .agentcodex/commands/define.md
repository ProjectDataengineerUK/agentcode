# Define

## Purpose

Capture and validate requirements in one pass. This is Phase 1 of the AgentCodex workflow and is the Codex-native port of AgentSpec's `define` procedure.

Use this after `brainstorm` when a validated direction exists, or directly when the user already has sufficiently clear requirements.

## Primary Role

- workflow-definer

## Inputs

- `.agentcodex/features/BRAINSTORM_{FEATURE}.md`
- meeting notes
- stakeholder email or conversation notes
- direct requirement text
- existing project docs
- multiple source files that must be consolidated

## Procedure

### Step 1: Load Context

Read the local instruction and requirement surfaces:

- `AGENTS.md`
- `.agentcodex/templates/DEFINE_TEMPLATE.md`
- `.agentcodex/kb/README.md`
- `.agentcodex/kb/index.yaml`
- the provided input file or request
- related brainstorm, feature, history, and project-standard artifacts

### Step 2: Input Classification

Identify the input type:

| Input Type | Pattern | Focus |
|------------|---------|-------|
| `brainstorm_document` | `BRAINSTORM_*.md` | pre-validated approach, extract directly |
| `meeting_notes` | bullet points or action items | decisions and requirements |
| `email_thread` | request, reply, forward, signatures | requests and constraints |
| `conversation` | informal language | core problem and users |
| `direct_requirement` | structured request | completeness check |
| `mixed_sources` | multiple formats | consolidate and deduplicate |

When the input is a brainstorm artifact, preserve its chosen approach, YAGNI removals, sample inventory, KB domains, and draft requirements.

### Step 3: Extract Entities

Extract:

- problem
- target users and pain points
- goals prioritized with MoSCoW
- measurable success criteria
- acceptance tests
- constraints
- technical context
- out of scope
- assumptions
- applicable KB domains

### Step 4: Add Data Contract When Applicable

If requirements mention data pipelines, ETL, analytics, warehouses, schemas, freshness, lineage, contracts, or quality gates, add the data contract section.

Capture:

- source inventory
- volumes
- freshness SLAs
- schema contracts
- completeness metrics
- lineage requirements
- ownership

### Step 5: Calculate Clarity Score

Score each element from 0-3:

| Element | Meaning |
|---------|---------|
| Problem | clear, specific, actionable |
| Users | identified with pain points |
| Goals | measurable and prioritized |
| Success | testable criteria |
| Scope | explicit boundaries |

Minimum to proceed:

- `12/15`

If score is below `12/15`, do not move to design. Ask targeted clarification questions with concrete options where possible.

### Step 6: Generate the Artifact

Write:

- `.agentcodex/features/DEFINE_{FEATURE}.md`

Use:

- `.agentcodex/templates/DEFINE_TEMPLATE.md`

## Outputs

- `.agentcodex/features/DEFINE_{FEATURE}.md`
- clarity score breakdown
- measurable success criteria
- testable acceptance tests
- explicit out-of-scope list
- assumptions with impact if wrong
- technical context and KB domains for design
- data contract section when applicable

## Quality Gate

Do not mark define complete until:

- [ ] problem statement is clear and specific
- [ ] at least one user persona has a pain point
- [ ] goals use MoSCoW priorities
- [ ] success criteria are measurable
- [ ] acceptance tests are testable
- [ ] constraints are explicit
- [ ] out of scope is explicit and not empty
- [ ] assumptions are documented with impact if wrong
- [ ] KB domains are identified for design
- [ ] technical context includes location and IaC impact
- [ ] clarity score is at least `12/15`

## Handoff

Move to `design` only when the clarity score is at least `12/15`, acceptance tests are testable, and scope boundaries are explicit.

Next artifact:

- `.agentcodex/features/DESIGN_{FEATURE}.md`
