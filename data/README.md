# Incident RAG Assistant – Synthetic Sample Dataset

This dataset supports a small enterprise Incident Root Cause Analysis Assistant using
Vector RAG, Graph RAG and multi-hop GraphRAG.

## Contents

- `services/services.json`: service catalogue and dependency declarations
- `databases/databases.json`: database catalogue
- `kafka/topics.json`: Kafka topic catalogue
- `teams/teams.json`: team ownership and responsibilities
- `errors/errors.json`: normalized error catalogue
- `incidents/incidents.json`: structured incident records
- `incidents/reports/*.md`: unstructured incident reports for chunking and embeddings
- `deployments/deployments.json`: deployment history
- `runbooks/*.md`: troubleshooting knowledge
- `architecture/*.md`: architecture and dependency documentation
- `metadata/dataset_manifest.json`: dataset summary and suggested relationships

## Suggested ingestion order

1. Load teams, databases, Kafka topics and services.
2. Create service ownership, dependency, database and topic relationships.
3. Load errors and runbooks.
4. Load deployments and connect each deployment to its target service.
5. Load incidents and connect them to affected services, observed errors and associated deployments.
6. Parse Markdown reports and runbooks into chunks.
7. Generate embeddings for chunks and create a Neo4j vector index.
8. Link chunks to graph entities using `MENTIONS` or `DESCRIBES` relationships.

## Important modeling guidance

The `associated_deployment_ids` field means a deployment was included in the incident
investigation context. It does NOT mean that deployment caused the incident.

The dataset intentionally includes incidents that are:
- plausibly related through shared dependencies,
- related through a common event topic or database,
- unrelated control cases,
- correlated in time without proven causation.

Keep facts, observations and hypotheses separate in your application.

## Suggested first questions

1. Which services are downstream of Customer Service?
2. Which incidents affected Customer Service or its dependent services?
3. Which incidents mention database connection pool exhaustion?
4. Which teams own the services on the Payment Service dependency path?
5. Which services could be affected if payment-events processing is delayed?
6. Do multiple incidents share Settlement Database as a dependency?
7. Which deployments occurred before INC-101, and what evidence supports or weakens a causal hypothesis?
8. Compare INC-101 and INC-111. Do they share a service, database or error pattern?

## Data format

All timestamps are ISO-8601 UTC strings. IDs are stable synthetic identifiers.
JSON files use a top-level `source_id` and a collection key.

## Disclaimer

Entirely fictional educational data. Do not use it for operational decisions.
