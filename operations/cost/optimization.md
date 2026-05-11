# Cost Optimization

## optimization levers

- reduce unnecessary agent depth for low-risk tasks
- compact logs, summaries, and memory candidates on a schedule
- align compute class with workload criticality
- prefer incremental processing over full recomputation

## tradeoffs

- lower latency often costs more
- more retention improves forensics but increases storage cost
- deeper multi-agent analysis improves quality but raises execution cost

## review cadence

- weekly review for production hot spots
- monthly review for baseline model and platform assumptions

## alert thresholds

- define daily spend threshold
- define abnormal cost spike threshold
- define per-workflow or per-crew anomaly threshold
