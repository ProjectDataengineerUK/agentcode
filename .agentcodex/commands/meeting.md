# Meeting Procedure

## Purpose

Codex-native replacement for AgentSpec's `/meeting` command.

## Primary Role

- `workflow-definer`

## Escalation Roles

- `workflow-brainstormer`
- `workflow-designer`
- `domain-researcher`

## KB Domains

- `orchestration`
- `data-modeling`

## Use When

- a call, workshop, or stakeholder discussion must be turned into actionable project artifacts
- requirements are spread across notes and need decisions, owners, and follow-ups
- the team needs a durable summary instead of ephemeral chat memory

## Inputs

- meeting notes, transcript, or bullet summary
- participants and decision owners when known
- links to affected features, designs, or reports

## Procedure

1. Route to `workflow-definer`.
2. Extract explicit decisions, unresolved questions, action items, and owner assignments.
3. Normalize ambiguous notes into durable requirements and constraints.
4. Escalate ideation-heavy ambiguity to `workflow-brainstormer` and architecture impacts to `workflow-designer`.
5. Write outputs into project artifacts under `.agentcodex/features/` or `.agentcodex/reports/`, not only into chat.
6. Call out contradictions, missing owners, and date-sensitive follow-ups explicitly.

## Outputs

- meeting summary with decisions and open questions
- action-item list with owners
- workflow artifact updates or follow-up drafts
- recommended next workflow phase
