
class GraphPathClassifier:
    """
    Classifies graph paths into investigation evidence categories.

    A path can also carry a historical-context flag when it
    starts from or passes through an incident other than
    the primary incident.
    """

    def classify(self, path: dict, primary_incident_id: str = None) -> dict:
        nodes = path.get("path_nodes", [])
        relationships = path.get("path_relationships", [])

        node_labels = [
            label
            for node in nodes
            for label in node.get("labels", [])
        ]

        node_ids = [node.get("id") for node in nodes]

        is_historical_context = any(
            "Incident" in node.get("labels", [])
            and node.get("id") != primary_incident_id
            for node in nodes
        )

        # Deployment association
        if (
            "ASSOCIATED_WITH" in relationships
            or "DEPLOYED_TO" in relationships
        ):
            evidence_type = "DEPLOYMENT_ASSOCIATION"

        # Directly affected service
        elif relationships == ["AFFECTED"]:
            evidence_type = "DIRECT_IMPACT"

        # Database dependency
        elif (
            "USES" in relationships
            and "Database" in node_labels
        ):
            evidence_type = "DATABASE_DEPENDENCY"

        # Kafka dependency
        elif (
            any(
                relationship in relationships
                for relationship in ("PRODUCES", "CONSUMES")
            )
            and "KafkaTopic" in node_labels
        ):
            evidence_type = "KAFKA_DEPENDENCY"

        # Service-to-service dependency
        elif "DEPENDS_ON" in relationships:
            evidence_type = "SERVICE_DEPENDENCY"

        elif "Error" in node_labels:
            evidence_type = "ERROR_SIGNATURE"

        # Historical incident context
        elif is_historical_context:
            evidence_type = "HISTORICAL_INCIDENT"
            

        else:
            evidence_type = "OTHER"

        return {
            "seed_chunk_id": path.get("seed_chunk_id"),
            "path_nodes": nodes,
            "path_relationships": relationships,
            "node_ids": node_ids,
            "evidence_type": evidence_type,
            "is_historical_context": is_historical_context
        }

    def classify_all(
        self,
        graph_paths: list[dict],
        primary_incident_id: str = None
    ) -> list[dict]:

        return [
            self.classify(path, primary_incident_id)
            for path in graph_paths
        ]
