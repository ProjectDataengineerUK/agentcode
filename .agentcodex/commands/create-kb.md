# Create KB Procedure

## Purpose

Codex-native replacement for AgentSpec's `/create-kb` command.

## Primary Role

- `domain-researcher`

## Escalation Roles

- `schema-designer`
- `pipeline-architect`
- `data-quality-analyst`

## KB Domains

- `data-modeling`
- `orchestration`
- `data-quality`

## Use When

- a recurring domain is missing from `.agentcodex/kb/`
- a project keeps re-solving the same platform or pattern questions
- local reference material is needed to reduce repeated external lookup

## Inputs

- target domain name
- expected consumers and typical task shapes
- seed notes, source docs, or imported upstream material when available

## Procedure

1. Route to `domain-researcher`.
2. Define the KB domain scope before writing content so it stays narrow and reusable.
3. Create or update domain `index.md`, `quick-reference.md`, and supporting `concepts/` or `patterns/` directories when warranted.
4. Prefer normalizing imported upstream material into concise local guidance instead of copying large raw text.
5. Escalate schema, orchestration, or quality specifics to the matching specialist role when deeper synthesis is needed.
6. Add the new domain to `.agentcodex/kb/index.yaml` and verify references from roles or command procedures.

## Outputs

- new or expanded KB domain
- concise quick reference
- concept and pattern notes where needed
- manifest updates for local discovery
