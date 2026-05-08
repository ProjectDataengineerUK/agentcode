# Project Structure Procedure

## Purpose

Codex-native procedure for explaining and auditing the AgentCodex folder taxonomy so project state does not sprawl across mixed-purpose directories.

## Primary Role

- `codebase-explorer`

## Escalation Roles

- `architect`
- `workflow-designer`

## KB Domains

- `governance`
- `orchestration`

## Use When

- the `.agentcodex/` tree feels messy or overloaded
- operators need to distinguish control-plane state from delivery artifacts
- project-local Databricks or other platform work is landing in the wrong place

## Inputs

- current repository layout
- optional `--json`

## Procedure

1. Route to `codebase-explorer`.
2. Run `python3 scripts/agentcodex.py project-structure [--json]`.
3. Group the layout into control plane, project runtime, knowledge/routing, bootstrap/distribution, and source reference.
4. Write the report to `.agentcodex/reports/project-structure.md`.
5. Use `docs/PROJECT-STRUCTURE.md` as the canonical taxonomy when relocating or judging new artifacts.
6. Escalate structural changes that affect workflow semantics to `workflow-designer` and broader taxonomy changes to `architect`.

## Outputs

- repo-local structure report
- explicit structure categories for the current repository
- canonical pointer to the layout taxonomy
