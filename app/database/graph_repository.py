from app.database.neo4j_client import Neo4jClient


class GraphRepository:

    def __init__(self, client: Neo4jClient):
        self.client = client

    def upsert_node(self, label: str, properties: dict):
        if not properties.get("id"):
            raise ValueError("Node must have an id")

        allowed_labels = {
            "Service", "Database", "KafkaTopic", "Team",
            "Incident", "Deployment", "Error",
            "Runbook", "DocumentChunk"
        }

        if label not in allowed_labels:
            raise ValueError(f"Unsupported node label: {label}")

        query = f"""
        MERGE (n:{label} {{id: $id}})
        SET n += $properties
        RETURN n
        """

        return self.client.execute_query(
            query,
            {
                "id": properties["id"],
                "properties": properties
            }
        )

    def create_relationship(
        self,
        source_label: str,
        source_id: str,
        relationship: str,
        target_label: str,
        target_id: str
    ):
        allowed_labels = {
            "Service", "Database", "KafkaTopic", "Team",
            "Incident", "Deployment", "Error",
            "Runbook", "DocumentChunk"
        }

        allowed_relationships = {
            "DEPENDS_ON", "USES", "PRODUCES", "CONSUMES",
            "OWNED_BY", "DEPLOYED_TO", "AFFECTED",
            "OBSERVED", "ASSOCIATED_WITH", "HAS_RUNBOOK",
            "DESCRIBES", "MENTIONS"
        }

        if source_label not in allowed_labels:
            raise ValueError("Unsupported source label")

        if target_label not in allowed_labels:
            raise ValueError("Unsupported target label")

        if relationship not in allowed_relationships:
            raise ValueError("Unsupported relationship type")

        query = f"""
        MATCH (source:{source_label} {{id: $source_id}})
        MATCH (target:{target_label} {{id: $target_id}})
        MERGE (source)-[r:{relationship}]->(target)
        RETURN r
        """

        return self.client.execute_query(
            query,
            {
                "source_id": source_id,
                "target_id": target_id
            }
        )