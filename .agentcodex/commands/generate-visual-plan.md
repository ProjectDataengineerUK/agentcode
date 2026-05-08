# Generate Visual Plan

## Purpose

Create a visual implementation plan as a self-contained HTML artifact. This ports AgentSpec's `generate-visual-plan` flow into a Codex-native, evidence-first procedure.

## Primary Role

- planner

## Escalation Roles

- codebase-explorer
- reviewer

## Inputs

- feature request, problem statement, or implementation goal
- target repository or subsystem
- relevant code, docs, tests, ADRs, and prior workflow artifacts
- optional output directory, default `.agentcodex/reports/visual/`

## Procedure

1. Parse the requested feature into problem, desired behavior, constraints, and explicit non-goals.
2. Read the relevant codebase before planning. Identify existing extension points, types, APIs, tests, and naming patterns.
3. Build a fact sheet with files to modify, files to create, functions, commands, state variables, assumptions, and unknowns.
4. Design the plan before writing HTML: current behavior, target behavior, state transitions, implementation sequence, tests, edge cases, rollback, and risks.
5. Render the plan as HTML with sections for problem, current architecture, planned architecture, change breakdown, test plan, edge cases, and execution order.
6. Mark unverified assumptions clearly instead of presenting them as facts.
7. Save the result under `.agentcodex/reports/visual/`.

## Outputs

- visual implementation plan HTML
- fact sheet or assumptions list
- recommended build sequence and verification checklist

## Quality Gate

- [ ] referenced files and functions exist or are marked as planned
- [ ] implementation order is explicit
- [ ] tests and rollback are included
- [ ] assumptions and open questions are visible
- [ ] visual page can be understood without reading the chat
