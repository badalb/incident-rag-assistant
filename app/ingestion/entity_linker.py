
import re

from app.database.neo4j_client import Neo4jClient


class EntityLinker:

    ALLOWED_LABELS = [
        "Service",
        "Database",
        "KafkaTopic",
        "Team",
        "Incident",
        "Deployment",
        "Error",
    ]

    def __init__(self, client: Neo4jClient):
        self.client = client

    def load_entities(self):
        query = """
        MATCH (e)
        WHERE e.id IS NOT NULL
          AND any(label IN labels(e)
                  WHERE label IN $allowed_labels)
        RETURN e.id AS id,
               labels(e) AS labels,
               coalesce(e.name, e.id) AS name
        """

        records = self.client.execute_query(
            query,
            {"allowed_labels": self.ALLOWED_LABELS}
        )

        return [
            {
                "id": record["id"],
                "name": record["name"],
                "labels": record["labels"],
            }
            for record in records
        ]

    def find_entities(self, content, entities):

        matched_ids = set()

        for entity in entities:

            aliases = [
                entity["id"],
                entity["name"]
            ]

            for alias in aliases:

                if not alias or len(alias.strip()) < 3:
                    continue

                # Match complete IDs or names, not partial words.
                pattern = (
                    r"(?<![A-Za-z0-9])"
                    + re.escape(alias.strip())
                    + r"(?![A-Za-z0-9])"
                )

                if re.search(pattern, content, re.IGNORECASE):
                    matched_ids.add(entity["id"])
                    break

        return sorted(matched_ids)

    def link_chunks(self, chunks):

        entities = self.load_entities()

        print(f"Graph entities loaded: {len(entities)}")

        linked_chunks = []

        for chunk in chunks:

            entity_ids = self.find_entities(
                chunk["content"],
                entities
            )

            linked_chunks.append({
                "chunk_id": chunk["id"],
                "entity_ids": entity_ids
            })

        # Store matched entity IDs on the chunk.
        update_query = """
        UNWIND $items AS item
        MATCH (c:DocumentChunk {id: item.chunk_id})
        SET c.mentioned_entity_ids = item.entity_ids
        RETURN count(c) AS processed
        """

        update_records = self.client.execute_query(
            update_query,
            {"items": linked_chunks}
        )

        # Create actual graph relationships.
        links = [
            {
                "chunk_id": item["chunk_id"],
                "entity_id": entity_id
            }
            for item in linked_chunks
            for entity_id in item["entity_ids"]
        ]

        relationship_count = 0

        if links:

            relationship_query = """
            UNWIND $links AS link

            MATCH (c:DocumentChunk {id: link.chunk_id})
            MATCH (e)
            WHERE e.id = link.entity_id

            MERGE (c)-[r:MENTIONS]->(e)

            RETURN count(r) AS processed
            """

            relationship_records = self.client.execute_query(
                relationship_query,
                {"links": links}
            )

            if relationship_records:
                relationship_count = relationship_records[0]["processed"]

        chunks_with_entities = sum(
            1 for item in linked_chunks if item["entity_ids"]
        )

        processed = (
            update_records[0]["processed"]
            if update_records else 0
        )

        print(f"Chunks processed: {processed}")
        print(f"Chunks with linked entities: {chunks_with_entities}")
        print(f"MENTIONS relationships created: {relationship_count}")

        return relationship_count
