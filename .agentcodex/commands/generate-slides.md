# Generate Slides

## Purpose

Generate a self-contained HTML slide deck from verified content. This is the Codex-native port of AgentSpec's `generate-slides` visual explainer flow.

## Primary Role

- code-documenter

## Escalation Roles

- codebase-explorer
- reviewer

## Inputs

- topic, artifact, plan, project recap, or narrative to present
- target audience and desired depth
- source files, docs, metrics, or workflow artifacts
- optional output directory, default `.agentcodex/reports/visual/`

## Procedure

1. Identify the audience and the decision or understanding the deck should support.
2. Gather and verify source facts before designing slides.
3. Draft a slide arc: title, context, evidence, deep dive, risks or tradeoffs, next steps.
4. Keep each slide focused on one point. Prefer diagrams, tables, timelines, and visual hierarchy over dense prose.
5. Use concrete project terms, file paths, commands, and metrics only when verified.
6. Generate a self-contained HTML deck with keyboard-friendly slide navigation.
7. Save the deck under `.agentcodex/reports/visual/`.

## Outputs

- HTML slide deck
- source fact summary
- list of unverified or intentionally omitted claims

## Quality Gate

- [ ] slide narrative has a clear beginning, middle, and close
- [ ] factual claims are verified
- [ ] text fits within slide bounds
- [ ] deck works as a standalone artifact
- [ ] sensitive content was excluded or explicitly approved
