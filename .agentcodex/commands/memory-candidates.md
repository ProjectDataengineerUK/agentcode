# Memory Candidates Procedure

## Purpose

Codex-native review and approval flow for repo-local memory candidates before ingesting them into active memory snapshots.

## Primary Role

- `memory-architect`

## Escalation Roles

- `memory-governance-engineer`
- `reviewer`

## KB Domains

- `genai`
- `observability`
- `governance`

## Use When

- extracted memory candidates should be reviewed before ingestion
- a project wants an auditable approval step for long-term memory writes
- seed memories were generated from repo-local artifacts
- production logs were converted into reviewable knowledge candidates

## Inputs

- latest or explicit candidate JSON file under `.agentcodex/memory/candidates/`
- candidate files may come from `memory-extract-*` or `log-knowledge-extract-*`
- optional review JSON file under `.agentcodex/memory/reviews/`

## Procedure

1. Run `python3 scripts/agentcodex.py memory-review-candidates [candidate-file]`.
2. Review the generated file in `.agentcodex/memory/reviews/`.
3. Keep `pending`, or set items to `approved` or `rejected` with reasons when manual review is needed.
4. Run `python3 scripts/agentcodex.py memory-approve-candidates [review-file]`.
5. Only approved and valid items are ingested into the active backend snapshots.
6. Treat log-derived candidates as reviewable evidence, not direct KB writes.
7. For approved log-derived items, emit `kb-update-candidate` proposals under `.agentcodex/kb/update-candidates/`.
8. Record the outcome through the generated approval report.

## Outputs

- review file for candidate decisions
- approval report
- ingested memory IDs for approved items
- KB update proposal file for approved log-derived candidates
