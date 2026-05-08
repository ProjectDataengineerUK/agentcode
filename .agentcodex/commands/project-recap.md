# Project Recap

## Purpose

Generate a visual project recap that rebuilds the current mental model of a repo, including architecture, recent activity, decisions, status, and next steps.

## Primary Role

- codebase-explorer

## Escalation Roles

- code-documenter
- reviewer

## Inputs

- target project directory
- optional time window such as `2w`, `30d`, or `3m`
- README, changelog, package/config files, git history, docs, tests, and local history artifacts
- optional output directory, default `.agentcodex/reports/visual/`

## Procedure

1. Read project identity surfaces: README, package/config files, command docs, and top-level structure.
2. Inspect recent activity with git history and current working tree status when available.
3. Read context history, handoff, ADR, plan, and report artifacts when present.
4. Map current architecture and active subsystems from source and docs.
5. Build a fact sheet with commit counts, changed files, current state, important modules, and explicit next-step evidence.
6. Generate an HTML recap with project identity, architecture snapshot, recent activity, decision log, status dashboard, mental model essentials, cognitive debt hotspots, and next steps.
7. Save the output under `.agentcodex/reports/visual/`.

## Outputs

- visual project recap HTML
- fact sheet or evidence summary
- next-step and cognitive-debt notes

## Quality Gate

- [ ] recap distinguishes verified facts from inference
- [ ] git and status claims match command output
- [ ] architecture summary is based on actual files
- [ ] next steps cite durable artifacts or are labeled inferred
- [ ] page is useful for resuming work later
