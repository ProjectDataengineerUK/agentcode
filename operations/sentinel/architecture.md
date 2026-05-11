# Sentinel Architecture

## Purpose

Define a file-based monitoring layer for the project using the Sentinel pattern:

- watcher crew
- analyzer crew
- interpreter crew
- knowledge layer

This layer is intended for production operations and should monitor the full product lifecycle:

- security posture
- computational resources
- environments
- user-facing functionality
- data and AI runtime health

## Overview

The expected flow is:

`data input -> watcher signals -> analytical diagnosis -> contextual interpretation -> actionable knowledge`

## Watcher Crew

- lambda watcher: monitor runtime errors, duration, memory, retry signals
- parser watcher: monitor schema drift, parsing failures, malformed payloads
- s3 flow watcher: monitor arrival, delay, duplication, and missing log batches
- pipeline watcher: monitor freshness, failed updates, broken dependencies, schedule misses
- quality watcher: monitor anomalies, validation failures, threshold violations
- medallion watcher: monitor bronze/silver/gold progression, contract enforcement, layer-specific degradation

## Analyzer Crew

- z-score detector: detect statistical anomalies from monitored metrics
- trend regressor: detect directional degradation and regression over time
- pattern matcher: map current signals to known failure patterns
- diff analyzer: compare current state against prior stable baselines and expected deltas

## Interpreter Crew

- context builder: assemble context from telemetry, lineage, quality evidence, and local KB
- genai interpreter: explain probable causes and propose next actions
- reporter: render CLI and Markdown outputs for operators and feature owners
- dispatcher: route alerts or persisted outputs to approved destinations

## Knowledge Layer

The final output should produce:

- explanations
- suggested actions
- severity
- confidence
- references
- kb auto-update candidates

## Supervision And Guardrails

- supervision-first: no production action should be treated as autonomous by default
- quarantine-first for critical uncertainty: containment is preferred over unsafe auto-remediation
- human-in-the-loop: approval is required for destructive, customer-visible, or privilege-expanding actions
- auditable output: every diagnosis and recommendation should leave repo-local or system-local evidence

## Event Model

- event-driven state: monitoring should react to runtime events, freshness signals, and quality violations
- autonomous agent team: watcher, analyzer, and interpreter roles should be separable and composable
- agent = role + goal + tools: each monitoring role should have a bounded purpose and explicit evidence sources

## Local Notes

- document concrete project mappings under the companion Sentinel files in this directory
- keep vendor-specific implementation details in platform-specific docs, not here
