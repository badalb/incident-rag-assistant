
from app.database.neo4j_client import Neo4jClient


class DocumentIngestor:

    def __init__(
        self,
        client: Neo4jClient,
        batch_size: int = 100
    ):
        self.client = client
        self.batch_size = batch_size

    def ingest(self, chunks: list[dict]) -> int:

        if not chunks:
            return 0

        query = """
        UNWIND $chunks AS chunk
        MERGE (n:DocumentChunk {id: chunk.id})
        SET n += chunk
        RETURN count(n) AS processed
        """

        total_processed = 0

        for start in range(0, len(chunks), self.batch_size):
            batch = chunks[start:start + self.batch_size]

            records = self.client.execute_query(
                query,
                {"chunks": batch}
            )

            if records:
                total_processed += records[0]["processed"]

        return total_processed
