# Database Deadlock Troubleshooting

## Purpose

Synthetic operational guidance for the PayFlow Technologies sample environment.

## Investigation checklist

Capture deadlock logs and transaction statements; inspect lock ordering and transaction duration; identify hot rows; review recent query or schema changes; use bounded retries only when operations are safe to retry.

## Evidence to capture

- Timestamped metrics and logs
- Service and dependency names
- Deployment version and change ticket
- Relevant incident identifiers
- Query, consumer group or connection pool measurements where applicable

## Caution

Do not infer causation from temporal proximity alone. Record observations separately
from hypotheses and confirm with telemetry or a reproducible test.
