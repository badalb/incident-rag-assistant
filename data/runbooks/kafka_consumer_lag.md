# Kafka Consumer Lag

## Purpose

Synthetic operational guidance for the PayFlow Technologies sample environment.

## Investigation checklist

Inspect consumer group lag by partition; compare producer throughput and consumer throughput; review rebalance frequency, processing latency and error rates; check partition assignment and downstream dependencies; scale consumers only after checking partition count and downstream capacity.

## Evidence to capture

- Timestamped metrics and logs
- Service and dependency names
- Deployment version and change ticket
- Relevant incident identifiers
- Query, consumer group or connection pool measurements where applicable

## Caution

Do not infer causation from temporal proximity alone. Record observations separately
from hypotheses and confirm with telemetry or a reproducible test.
