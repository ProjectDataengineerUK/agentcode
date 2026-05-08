# Sync Context Procedure

## Purpose

Codex-native replacement for AgentSpec's `/sync-context` command.

## Primary Role

- `workflow-iterator`

## Escalation Roles

- `workflow-definer`
- `workflow-designer`
- `domain-researcher`

## KB Domains

- `orchestration`
- `data-modeling`
- `data-quality`

## Use When

- workflow artifacts have drifted from the codebase or from each other
- a feature resumes after a long pause and context must be reconstructed
- project-local docs need propagation after design or implementation changes

## Inputs

- target feature or artifact set
- current code changes, reports, and workflow documents
- known inconsistencies or stale sections
- latest relevant file in `.agentcodex/history/`, if one exists

## Procedure

1. Route to `workflow-iterator`.
2. Compare define, design, build-report, and shipped artifacts against the current implementation state.
3. Read the latest relevant `.agentcodex/history/` entry before reconstructing missing context.
4. Update stale summaries, manifests, and next-step notes so the project can resume cleanly.
5. Escalate requirement mismatches to `workflow-definer` and architecture drift to `workflow-designer`.
6. Prefer editing project-local artifacts over inventing fresh session-only summaries.
7. Write or update a `.agentcodex/history/` entry with the new resume point, blockers, and next step.
8. Record what changed, what remains inconsistent, and the next blocking gap.

## Outputs

- synchronized workflow artifacts
- drift summary across code and docs
- explicit unresolved mismatches
- recommended next owner or workflow phase
- durable history entry under `.agentcodex/history/`
