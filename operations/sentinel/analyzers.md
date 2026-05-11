# Sentinel Analyzers

## Purpose

Describe the sequential analyzer crew that transforms watcher signals into diagnosis.

Required analyzer names:

- z-score detector
- trend regressor
- pattern matcher
- diff analyzer

## Required Analyzers

### Z-Score Detector

- purpose: identify anomalies from monitored metrics
- inputs: [metrics]
- outputs: [anomaly candidates]
- notes: define acceptable baseline windows

### Trend Regressor

- purpose: detect negative regression or directional drift over time
- inputs: [time-series metrics]
- outputs: [trend assessment]
- notes: define review cadence

### Pattern Matcher

- purpose: compare incidents against known failure signatures
- inputs: [signals, KB references]
- outputs: [matched patterns, likely causes]
- notes: define source of known patterns

### Diff Analyzer

- purpose: explain what changed relative to the prior expected state
- inputs: [before/after artifacts, lineage, configs]
- outputs: [delta summary]
- notes: define stable comparison baseline

## Local Notes

- do not overfit the analyzer layer to one platform
- keep the analyzer outputs short and usable by the interpreter crew
