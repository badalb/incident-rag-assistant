# Infrastructure Overview

The sample platform uses PostgreSQL databases and Kafka topics. No actual infrastructure,
credentials, logs or telemetry are included.

Suggested graph relationships:
- (Service)-[:DEPENDS_ON]->(Service)
- (Service)-[:USES]->(Database)
- (Service)-[:PRODUCES]->(KafkaTopic)
- (Service)-[:CONSUMES]->(KafkaTopic)
- (Service)-[:OWNED_BY]->(Team)
- (Incident)-[:AFFECTED]->(Service)
- (Incident)-[:OBSERVED]->(Error)
- (Incident)-[:ASSOCIATED_WITH]->(Deployment)
- (Deployment)-[:DEPLOYED_TO]->(Service)
- (Error)-[:HAS_RUNBOOK]->(Runbook)

For evidence traceability, create DocumentChunk nodes and connect them to incidents,
services, errors and deployments mentioned in each source document.
