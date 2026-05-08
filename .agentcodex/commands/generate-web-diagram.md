# Generate Web Diagram

## Purpose

Generate a self-contained HTML diagram or visual explanation from verified project evidence. This is the Codex-native port of AgentSpec's visual explainer `generate-web-diagram` flow.

## Primary Role

- code-documenter

## Escalation Roles

- codebase-explorer
- reviewer

## Inputs

- topic, system, workflow, architecture, or concept to explain
- relevant source files, docs, plans, or command outputs
- optional output directory, default `.agentcodex/reports/visual/`
- optional target audience and visual style

## Procedure

1. Clarify the visual question: what must the reader understand after viewing the page?
2. Gather repo evidence before drawing. Read the relevant files and command outputs directly.
3. Build a fact sheet with every file path, command, number, component name, and behavior claim that will appear in the page.
4. Choose a rendering mode: Mermaid for topology and flows, HTML tables for comparisons, CSS cards for rich component descriptions.
5. Use a restrained visual system with clear hierarchy, responsive layout, and overflow protection.
6. Keep the HTML self-contained unless the user explicitly wants external assets.
7. Write the output to `.agentcodex/reports/visual/<descriptive-name>.html` or a requested path.
8. Report the output path and the verification evidence used.

## Outputs

- self-contained HTML visual explanation
- fact sheet or verification notes in the response or adjacent report
- list of uncertain claims, if any

## Quality Gate

- [ ] every factual claim is backed by a file, command, or explicit user input
- [ ] generated page is self-contained or external dependencies are justified
- [ ] layout handles long file paths, code snippets, and small screens
- [ ] diagrams are readable without relying on chat context
- [ ] uncertain claims are labeled as uncertain
