# Sentinel Knowledge

## Purpose

Define the final knowledge objects produced by Sentinel monitoring.

## Required Outputs

- explanations: what happened and why it likely happened
- suggested actions: what should be done next
- severity: operational impact level
- confidence: confidence in the diagnosis
- references: links to evidence, docs, KB, and runbooks
- kb auto-update: criteria for creating reviewable KB update candidates

## Output Contract

- keep outputs concise and evidence-backed
- separate facts from inference
- identify missing evidence explicitly
- link to owners and downstream impact where possible

## Continuous Learning

- define when an incident becomes a reusable pattern
- define review criteria before kb auto-update is accepted
- define owner for maintaining known patterns and explanations

## Local Notes

- do not let auto-update write directly into authoritative KB without review
