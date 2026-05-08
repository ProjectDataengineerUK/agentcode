# Failure Pattern Promote Procedure

## Purpose

Codex-native procedure for clustering recurrent failure signals and promoting them into guardrail and memory candidates.

## Primary Role

- `data-observability-engineer`

## Escalation Roles

- `memory-governance-engineer`
- `reviewer`
- `architect`

## KB Domains

- `observability`
- `governance`
- `genai`

## Use When

- the same failure class appears in logs or failure ledgers more than once
- a project wants stable lessons learned promoted into product behavior
- operators need explicit suggestions for validators, runbooks, or preflight rules

## Inputs

- optional target project directory
- observability logs under `.agentcodex/observability/logs/`
- structured failure ledgers under `.agentcodex/observability/failures/`
- optional `--json`

## Procedure

1. Route to `data-observability-engineer`.
2. Run `python3 scripts/agentcodex.py failure-pattern-promote [target-project-dir] [--json]`.
3. Cluster repeated failure reasons by script and normalized error pattern.
4. Map each cluster to recommended actions such as preflight, validation, runbook, or regression promotion.
5. Write the report to `.agentcodex/reports/failure-pattern-promotion.md`.
6. For repeated patterns, emit procedural memory candidates under `.agentcodex/memory/candidates/`.
7. Persist the machine-readable summary to `.agentcodex/state/project-state.json`.
8. Escalate memory-governance questions to `memory-governance-engineer`, verification questions to `reviewer`, and design-level fixes to `architect`.

## Outputs

- repo-local failure-pattern report
- procedural memory candidates for recurrent failures
- canonical summary of promoted patterns in project state
