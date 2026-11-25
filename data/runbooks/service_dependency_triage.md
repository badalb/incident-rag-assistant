# Service Dependency Incident Triage

## Purpose

Synthetic operational guidance for the PayFlow Technologies sample environment.

## Investigation checklist

Start from the failing service; traverse direct and transitive dependencies; inspect dependency health and ownership; identify incidents on shared dependencies; distinguish impact propagation from root cause; document each evidence source.

## Evidence to capture

- Timestamped metrics and logs
- Service and dependency names
- Deployment version and change ticket
- Relevant incident identifiers
- Query, consumer group or connection pool measurements where applicable

## Caution

Do not infer causation from temporal proximity alone. Record observations separately
from hypotheses and confirm with telemetry or a reproducible test.
