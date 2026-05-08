# Start

## Purpose

Start a project by scanning the current directory and choosing the correct onboarding path.

Use this as the first command after installation when the operator wants AgentCodex to inspect the repository, generate a context file if needed, and launch the brainstorm workflow.

## Primary Role

- planner

## Escalation Roles

- workflow-brainstormer
- reviewer
- domain-researcher

## KB Domains

- orchestration
- ai-data-engineering
- data-modeling
- observability

## Inputs

- current project directory
- repository files and folder layout
- markdown notes, PDFs, and videos when the project has no clear base scaffold yet

## Procedure

1. Run `agentcodex start` from the target project directory.
2. Scan the project for base files such as `README.md`, `pyproject.toml`, `package.json`, `go.mod`, `Cargo.toml`, `pom.xml`, or `Makefile`.
   - Do not treat an `AGENTS.md` created by lightweight AgentCodex install as project-owned evidence by itself.
3. If base files are present, show a numbered delivery menu:
   - `1. Detailed project report`
   - `2. DataOps / MLOps / LLMOps maturity`
   - `3. Vulnerability report`
   - `4. Project improvement report`
   - `5. All reports`
4. Let the operator select an option by number, then write the selected report before writing the scan summary to `.agentcodex/reports/start-report.md`.
5. If project-owned base files are not present, read all markdown files in the repository, collect any sidecar text for PDFs and videos when available, and create `context.md` at the project root.
   - Treat PDFs as multimodal evidence, not text-only evidence.
   - For each PDF, attempt text extraction first, then render pages as images when diagrams, screenshots, architecture drawings, tables, or low text yield are present.
   - Inspect rendered pages visually and use OCR when useful; summarize text, images, diagrams, and architecture flows separately so visual content is not silently skipped.
6. Write an English brainstorm prompt based on `context.md` to `.agentcodex/reports/start-brainstorm-prompt.md`.
   - Include a compact evidence brief from detected markdown, PDF sidecar/extracted text, PDF visual inspection notes, and video sidecars.
   - Include a sequential question flow so `workflow-brainstormer` can start with Question 1 and proceed one answer at a time.
7. Create a draft brainstorm artifact under `.agentcodex/features/BRAINSTORM_{PROJECT}.md`.
8. Hand the project to `workflow-brainstormer` so the next step can continue from the generated context.
9. Prefer file-based context over chat-only summaries.

## Outputs

- `.agentcodex/reports/start-report.md` when base project files already exist
- `.agentcodex/reports/start-detailed-project-report.md` for option `1`
- `.agentcodex/reports/start-maturity-report.md` for option `2`, with DataOps, MLOps, and LLMOps maturity tracks
- `.agentcodex/reports/start-vulnerability-report.md` for option `3`
- `.agentcodex/reports/start-improvement-report.md` for option `4`
- `context.md` when the project needs raw-context collection first
- `.agentcodex/reports/start-brainstorm-prompt.md`
- `.agentcodex/features/BRAINSTORM_{PROJECT}.md`
