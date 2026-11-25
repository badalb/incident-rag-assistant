
from app.database.neo4j_client import Neo4jClient


class GraphRetriever:

    def __init__(self, client: Neo4jClient):
        self.client = client

    def retrieve_related_entities(
        self,
        chunk_ids: list[str],
        max_hops: int = 3
    ):

        if not chunk_ids:
            return []

        if not 1 <= max_hops <= 4:
            raise ValueError("max_hops must be between 1 and 4")

        query = f"""
        MATCH (seed:DocumentChunk)-[:MENTIONS]->(start)

        WHERE seed.id IN $chunk_ids
          AND start:Incident

        MATCH p =
            (start)-[
                :AFFECTED
                |DEPENDS_ON
                |USES
                |PRODUCES
                |CONSUMES
                |OBSERVED
                |ASSOCIATED_WITH
                |DEPLOYED_TO
            *1..{max_hops}]->(related)

        RETURN DISTINCT

            seed.id AS seed_chunk_id,

            [
                node IN nodes(p) |
                {{
                    id: node.id,
                    labels: labels(node),
                    name: coalesce(
                        node.name,
                        node.title,
                        node.id
                    )
                }}
            ] AS path_nodes,

            [
                rel IN relationships(p) |
                type(rel)
            ] AS path_relationships

        LIMIT 50
        """

        records = self.client.execute_query(
            query,
            {"chunk_ids": chunk_ids}
        )

        return [
            record.data()
            for record in records
        ]

    def retrieve_related_incidents(
        self,
        chunk_ids: list[str],
        max_hops: int = 3
    ):

        if not chunk_ids:
            return []

        if not 1 <= max_hops <= 4:
            raise ValueError("max_hops must be between 1 and 4")

        query = f"""
        MATCH (seed:DocumentChunk)-[:MENTIONS]->(start:Incident)

        WHERE seed.id IN $chunk_ids

        MATCH p =
            (start)-[:AFFECTED|DEPENDS_ON*1..{max_hops}]->(svc:Service)

        MATCH (related:Incident)-[:AFFECTED]->(svc)

        WHERE related.id <> start.id

        RETURN DISTINCT
            seed.id AS seed_chunk_id,
            start.id AS source_incident,
            svc.id AS shared_service,
            related.id AS related_incident,
            related.title AS related_incident_title

        LIMIT 30
        """

        records = self.client.execute_query(
            query,
            {"chunk_ids": chunk_ids}
        )

        return [
            record.data()
            for record in records
        ]


    def retrieve_related_incidents(
        self,
        chunk_ids: list[str],
        max_hops: int = 3
    ):

        if not chunk_ids:
            return []

        if not 1 <= max_hops <= 4:
            raise ValueError("max_hops must be between 1 and 4")

        query = f"""
        MATCH (seed:DocumentChunk)-[:MENTIONS]->(start:Incident)

        WHERE seed.id IN $chunk_ids

        MATCH p =
            (start)-[:AFFECTED|DEPENDS_ON*1..{max_hops}]->(svc:Service)

        MATCH (related:Incident)-[:AFFECTED]->(svc)

        WHERE related.id <> start.id

        RETURN DISTINCT
            seed.id AS seed_chunk_id,
            start.id AS source_incident,
            svc.id AS shared_service,
            related.id AS related_incident,
            related.title AS related_incident_title

        LIMIT 30
        """

        records = self.client.execute_query(
            query,
            {"chunk_ids": chunk_ids}
        )

        return [
            record.data()
            for record in records
        ]
