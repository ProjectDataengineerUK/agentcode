# Plan Review

## Purpose

Generate a visual review of an implementation plan against the current codebase.

## Primary Role

- reviewer

## Escalation Roles

- codebase-explorer
- planner

## Inputs

- plan, RFC, design doc, or workflow artifact
- target codebase
- files and APIs referenced by the plan
- optional output directory, default `.agentcodex/reports/visual/`

## Procedure

1. Read the plan in full and extract every proposed change, assumption, file reference, and stated non-goal.
2. Read every referenced file and enough dependent code to understand the current behavior.
3. Verify that the plan's description of current state matches the code.
4. Identify missing tests, docs, migrations, rollback, ordering constraints, and ripple effects.
5. Build a fact sheet with plan claims and code evidence.
6. Generate an HTML review with current architecture, planned architecture, change-by-change breakdown, dependency impact, risks, Good/Bad/Ugly findings, and open questions.
7. Save the output under `.agentcodex/reports/visual/`.

## Outputs

- visual plan review HTML
- verified claim list
- implementation risks and plan gaps

## Quality Gate

- [ ] every plan claim is verified or marked uncertain
- [ ] missing files/functions are explicitly flagged
- [ ] tests, docs, and rollback are assessed
- [ ] assumptions are visible before implementation starts
- [ ] review findings cite source files or plan sections
