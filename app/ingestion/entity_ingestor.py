from typing import Type
from pydantic import BaseModel

from app.database.neo4j_client import Neo4jClient


class EntityIngestor:

    ALLOWED_LABELS = {
        "Service",
        "Database",
        "KafkaTopic",
        "Team",
        "Incident",
        "Deployment",
        "Error"
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
        label: str,
        model_class: Type[BaseModel],
        raw_entities: list[dict]
    ) -> int:

        if label not in self.ALLOWED_LABELS:
            raise ValueError(f"Unsupported label: {label}")

        validated_entities = []

        # Validate and convert entities into JSON-safe dictionaries
        for raw_entity in raw_entities:
            entity = model_class.model_validate(raw_entity)
            validated_entities.append(
                entity.model_dump(mode="json")
            )

        total_ingested = 0

        # Process entities in batches
        for start in range(
            0,
            len(validated_entities),
            self.batch_size
        ):
            batch = validated_entities[
                start:start + self.batch_size
            ]

            query = f"""
            UNWIND $entities AS entity
            MERGE (n:{label} {{id: entity.id}})
            SET n += entity
            RETURN count(n) AS processed
            """

            records = self.client.execute_query(
                query,
                {"entities": batch}
            )

            if records:
                total_ingested += records[0]["processed"]

        print(
            f"{label}: processed {total_ingested} entities",
            flush=True
        )

        return total_ingested