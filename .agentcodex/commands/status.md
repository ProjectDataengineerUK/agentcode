# Status

## Purpose

Generate a project status report from AgentCodex workflow artifacts, git state, command surfaces, and project health indicators. This is the Codex-native port of AgentSpec's `/status` command.

## Primary Role

- codebase-explorer

## Escalation Roles

- reviewer
- planner

## Inputs

- target project directory, default current directory
- optional status context such as sprint review, release check, or resume handoff
- `.agentcodex/features/`, `.agentcodex/reports/`, `.agentcodex/archive/`, and `.agentcodex/history/`
- git status, recent commits, branches, and optional PR data when available
- README, AGENTS.md, tests, config files, and TODO/FIXME signals

## Procedure

1. Scan AgentCodex workflow artifacts under `.agentcodex/features/`, `.agentcodex/reports/`, `.agentcodex/archive/`, and `.agentcodex/history/`.
2. Identify active features, current phase, blockers, recently shipped work, and the latest durable resume point.
3. Check git state with recent commits, current branch, uncommitted changes, and local branches.
4. Detect project health signals: tests, documentation, config files, stack indicators, TODO/FIXME count, and command availability.
5. Compare detected stack and workflow needs against AgentCodex KB domains and routing guidance.
6. Produce a concise status report with active work, recent activity, health checks, recommendations, and suggested next commands.
7. For this repo itself, `python3 scripts/agentcodex.py status [section]` is the preferred executable status surface.

## Outputs

- markdown status report in chat or requested file
- optional generated status snapshot through `python3 scripts/agentcodex.py status`
- recommended next workflow phase, role, and health action

## Quality Gate

- [ ] status distinguishes active work from shipped/archive material
- [ ] git claims match command output
- [ ] next step is grounded in durable artifacts or labeled as inferred
- [ ] health issues are prioritized, not listed without action
- [ ] Claude-only paths and slash-command assumptions are normalized to AgentCodex surfaces
