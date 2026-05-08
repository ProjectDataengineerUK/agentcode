# Review Procedure

## Purpose

Codex-native replacement for AgentSpec's `/review` command.

## Primary Role

- `reviewer`

## Escalation Roles

- `domain-researcher`
- `data-quality-analyst`
- `dbt-specialist`
- `spark-engineer`

## KB Domains

- `data-quality`
- `dbt`
- `spark`
- `sql-patterns`

## Use When

- a change set needs bug, regression, or test-risk review before merge
- implementation is complete enough for critical reading but not yet trusted
- the review must produce explicit findings instead of a vague approval

## Inputs

- diff, changed files, or commit range
- related feature, define, or design artifacts when they exist
- testing evidence and known risk areas

## Procedure

1. Route to `reviewer`.
2. Review for correctness, regressions, missing tests, and mismatch against the current workflow artifacts.
3. Read local design and define documents before judging intended behavior.
4. Escalate domain-specific concerns when the risk depends on dbt, Spark, or data-quality semantics.
5. Produce findings first, ordered by severity, with file references and concrete failure modes.
6. Record residual risks and testing gaps even when no blocking defects are found.

## Outputs

- prioritized review findings
- residual risk summary
- testing and validation gaps
- merge-readiness recommendation
