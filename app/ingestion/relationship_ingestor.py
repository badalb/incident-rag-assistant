from app.database.neo4j_client import Neo4jClient


class RelationshipIngestor:

    ALLOWED_LABELS = {
        "Service", "Database", "KafkaTopic", "Team",
        "Incident", "Deployment", "Error"
    }

    ALLOWED_RELATIONSHIPS = {
        "DEPENDS_ON", "USES", "PRODUCES", "CONSUMES",
        "OWNED_BY", "DEPLOYED_TO", "AFFECTED",
        "OBSERVED", "ASSOCIATED_WITH"
    }

    def __init__(
        self,
        client: Neo4jClient,
        batch_size: int = 100
    ):
        self.client = client
        self.batch_size = batch_size

    def ingest(
        self,
        source_label: str,
        relationship_type: str,
        target_label: str,
        relationships: list[dict]
    ) -> int:

        if source_label not in self.ALLOWED_LABELS:
            raise ValueError(f"Unsupported source label: {source_label}")

        if target_label not in self.ALLOWED_LABELS:
            raise ValueError(f"Unsupported target label: {target_label}")

        if relationship_type not in self.ALLOWED_RELATIONSHIPS:
            raise ValueError(
                f"Unsupported relationship: {relationship_type}"
            )

        if not relationships:
            return 0

        total = 0

        query = f"""
        UNWIND $relationships AS rel

        MATCH (source:{source_label} {{id: rel.source_id}})
        MATCH (target:{target_label} {{id: rel.target_id}})

        MERGE (source)-[r:{relationship_type}]->(target)

        RETURN count(r) AS processed
        """

        for start in range(0, len(relationships), self.batch_size):
            batch = relationships[start:start + self.batch_size]

            records = self.client.execute_query(
                query,
                {"relationships": batch}
            )

            if records:
                total += records[0]["processed"]

        print(
            f"{source_label}-[{relationship_type}]->"
            f"{target_label}: {total} relationships",
            flush=True
        )

        return total