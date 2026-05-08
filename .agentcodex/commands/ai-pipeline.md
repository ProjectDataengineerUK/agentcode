# AI Pipeline Procedure

## Purpose

Codex-native replacement for AgentSpec's `/ai-pipeline` command.

## Primary Role

- `ai-data-engineer`

## Escalation Roles

- `streaming-engineer`
- `data-quality-analyst`
- `pipeline-architect`

## KB Domains

- `ai-data-engineering`
- `streaming`
- `data-quality`

## Use When

- the project needs RAG, embedding, vector-store, feature-store, or text-to-SQL architecture
- retrieval and indexing design are still implicit
- AI data movement must be turned into a reproducible project artifact

## Inputs

- retrieval use case or AI workflow description
- source data types and volume assumptions
- target vector store, feature store, or serving environment when known

## Procedure

1. Route to `ai-data-engineer`.
2. Make retrieval, chunking, indexing, and versioning decisions explicit.
3. Load `ai-data-engineering` KB material before choosing tools or libraries.
4. Escalate real-time ingestion concerns to `streaming-engineer`.
5. Escalate generic orchestration concerns to `pipeline-architect`.
6. Record quality, evaluation, and cost assumptions alongside the design.

## Outputs

- AI data pipeline architecture
- retrieval and indexing decisions
- quality and evaluation notes
- implementation handoff for build work
