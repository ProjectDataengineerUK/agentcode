# Brainstorm

## Purpose

Explore an idea through collaborative dialogue before formal requirements capture. This is Phase 0 of the AgentCodex workflow and is the Codex-native port of AgentSpec's `brainstorm` procedure.

Use this when the problem is fuzzy, the user is unsure about scope, multiple approaches are possible, or sample material is needed to ground an LLM/data-engineering solution.

## Primary Role

- workflow-brainstormer

## Inputs

- a short feature request
- notes from a meeting
- a problem statement
- a business objective
- an existing rough architecture idea
- a file containing raw notes or examples

## Procedure

### Step 1: Gather Context

Read the local instruction and workflow surfaces before proposing an approach:

- `AGENTS.md`
- `.agentcodex/templates/BRAINSTORM_TEMPLATE.md`
- `.agentcodex/kb/README.md`
- `.agentcodex/kb/index.yaml`
- relevant code, docs, and recent feature artifacts

Identify the likely feature name, current project patterns, and KB domains that may matter in the `define` phase.

### Step 2: Ask Discovery Questions

Ask questions one at a time. Prefer multiple choice when the options are clear, and use open-ended questions only when the space is unknown.

Minimum before proposing approaches:

- 3 discovery questions answered or explicitly marked unavailable
- purpose, user/stakeholder, and constraint/success dimensions covered

Do not bundle several questions into one message.

### Step 3: Collect Grounding Samples

Ask whether the user has sample material that can ground the solution:

```text
Do you have samples that can ground this work?
(a) sample input files
(b) expected output examples
(c) ground truth or verified data
(d) requirements, schemas, or reference docs
(e) none available
```

If samples exist, inspect and document them in the brainstorm artifact. If none exist, record that explicitly and note the impact on confidence.

### Step 4: Explore Approaches

Present 2-3 distinct approaches. Lead with a recommendation, but include alternatives and why they are weaker.

For each approach, document:

- description
- pros
- cons
- operational cost or complexity
- confidence and evidence
- KB/codebase patterns used

### Step 5: Apply YAGNI

List candidate features and remove anything that is not needed for the first useful version.

For each removed or deferred feature, record:

- feature
- reason removed
- whether it can be added later

### Step 6: Validate Incrementally

Validate the emerging understanding in sections. Keep each section small enough for the user to correct.

Minimum before completion:

- 2 validation checkpoints
- selected approach confirmed by the user
- major rejected alternatives documented

### Step 7: Generate the Artifact

Write:

- `.agentcodex/features/BRAINSTORM_{FEATURE}.md`

Use:

- `.agentcodex/templates/BRAINSTORM_TEMPLATE.md`

The artifact must include draft requirements that are ready to feed `define`.

## Outputs

- `.agentcodex/features/BRAINSTORM_{FEATURE}.md`
- selected approach with rationale
- sample inventory or explicit note that samples are unavailable
- features removed by YAGNI
- draft problem statement, target users, success criteria, constraints, and out-of-scope items for `define`

## Quality Gate

Do not mark brainstorm complete until:

- [ ] minimum 3 discovery questions asked
- [ ] sample collection question asked
- [ ] at least 2 approaches explored with tradeoffs
- [ ] relevant KB domains identified for define
- [ ] YAGNI applied and removed/deferred features documented
- [ ] minimum 2 validation checkpoints completed
- [ ] selected approach confirmed by user
- [ ] draft requirements included for `define`

## Handoff

Move to `define` when the recommended direction is accepted, the user goal is understandable, and major ambiguity is reduced enough to write measurable requirements.

Next artifact:

- `.agentcodex/features/DEFINE_{FEATURE}.md`

