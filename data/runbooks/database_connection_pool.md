# Database Connection Pool Exhaustion

## Purpose

Synthetic operational guidance for the PayFlow Technologies sample environment.

## Investigation checklist

Check active, idle and waiting connections; compare pool limits with database max_connections; inspect connection leaks and long-running transactions; correlate pool metrics with deployments; validate recovery after rollback or pool tuning.

## Evidence to capture

- Timestamped metrics and logs
- Service and dependency names
- Deployment version and change ticket
- Relevant incident identifiers
- Query, consumer group or connection pool measurements where applicable

## Caution

Do not infer causation from temporal proximity alone. Record observations separately
from hypotheses and confirm with telemetry or a reproducible test.
