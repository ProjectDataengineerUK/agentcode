# Sentinel Interpreters

## Purpose

Describe how analyzed signals become contextual explanation and operational action.

Required interpreter names:

- context builder
- genai interpreter
- reporter
- dispatcher

## Required Components

### Context Builder

- assemble context from telemetry, lineage, data quality, contracts, ownership, and local KB
- define the minimum evidence bundle before an explanation is emitted

### GenAI Interpreter

- explain probable causes
- suggest next actions
- express uncertainty explicitly

### Reporter

- output modes: CLI, Markdown, incident note, operator summary
- required sections: summary, severity, confidence, likely cause, next action

### Dispatcher

- approved targets: [slack, storage, ticketing, none]
- dispatch rules: [who receives what and when]
- failure behavior: [fallback path]

## Production Scope

- security incidents
- compute and capacity degradation
- environment instability
- product functionality regressions
- data and AI runtime degradation

## Local Notes

- keep reporter and dispatcher deterministic even when GenAI is used in interpretation
- if external dispatch is not allowed, document the repo-local storage path instead
