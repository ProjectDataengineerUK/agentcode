# Diff Review

## Purpose

Generate a visual review of a git diff, including scope, architecture impact, tests, documentation impact, risks, and decision rationale.

## Primary Role

- reviewer

## Escalation Roles

- codebase-explorer
- code-documenter

## Inputs

- git reference, commit, range, PR diff, or working tree
- changed files and surrounding code paths
- test output, docs, changelog, and relevant workflow artifacts
- optional output directory, default `.agentcodex/reports/visual/`

## Procedure

1. Resolve the diff scope. Default to working tree versus the main branch when no scope is provided.
2. Gather `git diff --stat`, `git diff --name-status`, and full diffs for changed files.
3. Read changed files and enough surrounding code to verify behavior and impact.
4. Check tests, docs, changelog, and command surfaces affected by the diff.
5. Build a fact sheet with counts, file names, public APIs, behavior changes, and verification commands.
6. Write the visual review with executive summary, KPI dashboard, file map, architecture impact, test coverage, Good/Bad/Ugly findings, questions, and re-entry context.
7. Save the HTML output under `.agentcodex/reports/visual/`.

## Outputs

- visual diff review HTML
- fact sheet or verification summary
- prioritized findings and open questions

## Quality Gate

- [ ] findings are tied to file paths or command output
- [ ] quantitative claims match git output
- [ ] docs and tests impact was checked
- [ ] uncertain rationale is labeled as inferred
- [ ] review does not replace local tests
