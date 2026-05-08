# Memory

## Purpose

Capture high-signal session insights into AgentCodex's repo-local memory lifecycle. This is the Codex-native port of AgentSpec's `/memory` command.

AgentCodex does not write to `.claude/storage/`. Memory artifacts stay under `.agentcodex/memory/`, `.agentcodex/reports/memory/`, and the configured file-based memory backend.

## Primary Role

- memory-governance-engineer

## Escalation Roles

- memory-architect
- memory-observability-engineer

## Inputs

- optional user note describing what should be remembered
- current session decisions, patterns, gotchas, and open items
- related feature, report, history, or workflow artifacts
- existing memory candidate and review files when continuing an approval flow

## Procedure

1. Decide whether the insight is worth long-term memory. Keep decisions, reusable patterns, gotchas, and durable open items; skip obvious implementation details.
2. Classify each candidate as semantic, episodic, or procedural memory.
3. Prefer reviewed candidate flow for durable writes:
   - `python3 scripts/agentcodex.py memory-extract`
   - `python3 scripts/agentcodex.py memory-review-candidates`
   - review the generated file under `.agentcodex/memory/reviews/`
   - `python3 scripts/agentcodex.py memory-approve-candidates <review-file>`
4. For explicit structured payloads, use `python3 scripts/agentcodex.py memory-ingest <semantic|episodic|procedural> <json-file>`.
5. For operational log evidence, use `python3 scripts/agentcodex.py extract-log-knowledge` before review.
6. Run `python3 scripts/agentcodex.py memory-lint` after meaningful memory writes.
7. Run `python3 scripts/agentcodex.py memory-health` when backend state or storage paths are unclear.
8. Record sensitive, temporary, or speculative material in local reports only; do not promote it to durable memory.

## Outputs

- memory candidate JSON under `.agentcodex/memory/candidates/`
- review JSON under `.agentcodex/memory/reviews/`
- approved file-based memory snapshots
- memory reports under `.agentcodex/reports/memory/`

## Quality Gate

- [ ] each memory item has a clear owner and source
- [ ] sensitive or temporary material was excluded
- [ ] candidate type is semantic, episodic, or procedural
- [ ] reviewed memory was approved before ingestion
- [ ] `memory-lint` passes after durable writes
