# Judge

## Purpose

Run an opt-in cross-model second opinion on a file or stdin content. This is the Codex-native port of AgentSpec's Judge Layer V0.

The judge is advisory. Use it for high-stakes files where a second model may catch mistakes the authoring model missed.

## Primary Role

- reviewer

## Inputs

- target file path, or `--stdin`
- optional `--phase generic|define|design|build`
- optional `--context "<task context>"`
- optional `--model <openrouter-model-slug>`

## Procedure

1. Confirm the target does not contain secrets, customer data, payment data, health data, or confidential material.
2. Run `python3 scripts/agentcodex.py judge <file> --context "<context>"`.
3. Use `--phase define`, `--phase design`, or `--phase build` when judging workflow artifacts so the prompt is tuned to the phase.
4. Read the judge evidence before accepting the verdict.
5. Verify concrete claims with local tests or direct file inspection.
6. Record material findings in the relevant review, build, design, or ship artifact.

## Outputs

- markdown verdict in stdout, or JSON with `--json`
- ledger entry in `.agentcodex/storage/judge-ledger.jsonl`
- exit code `0` for PASS, `1` for FAIL, `2` for config/input errors, `3` for exhausted budget, `4` for API/network errors

## Setup

Required:

```bash
export OPENROUTER_API_KEY=sk-or-v1-...
```

Optional:

```bash
export JUDGE_MODEL=openai/gpt-4o
export JUDGE_BUDGET=25
```

Defaults:

- generic: `openai/gpt-4o-mini`
- define/design/build: `openai/gpt-4o`
- daily budget: `10`

## Examples

```bash
python3 scripts/agentcodex.py judge .agentcodex/features/DEFINE_SEARCH.md --phase define
python3 scripts/agentcodex.py judge infra/iam/role.tf --context "least privilege IAM role"
python3 scripts/agentcodex.py judge --ledger
```

## Quality Gate

- [ ] target checked for sensitive content before sending to OpenRouter
- [ ] phase selected when judging workflow artifacts
- [ ] verdict evidence reviewed manually
- [ ] high-severity concerns either fixed or explicitly rejected with rationale
- [ ] local verification remains the source of truth
