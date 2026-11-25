
from app.ingestion.embedding_service import EmbeddingService
from app.database.neo4j_client import Neo4jClient


class EmbeddingIngestor:

    def __init__(
        self,
        client: Neo4jClient,
        embedding_service: EmbeddingService,
        batch_size: int = 50
    ):
        self.client = client
        self.embedding_service = embedding_service
        self.batch_size = batch_size

    def ingest(self, chunks: list[dict]) -> int:

        if not chunks:
            return 0

        total_updated = 0

        query = """
        UNWIND $chunks AS chunk
        MATCH (n:DocumentChunk {id: chunk.id})
        SET n.embedding = chunk.embedding
        RETURN count(n) AS processed
        """

        for start in range(0, len(chunks), self.batch_size):

            batch = chunks[start:start + self.batch_size]

            texts = [
                chunk["content"]
                for chunk in batch
            ]

            embeddings = (
                self.embedding_service.generate_embeddings(texts)
            )

            if len(embeddings) != len(batch):
                raise RuntimeError(
                    "Embedding count does not match chunk count"
                )

            records_to_update = []

            for chunk, embedding in zip(batch, embeddings):

                records_to_update.append({
                    "id": chunk["id"],
                    "embedding": embedding
                })

            records = self.client.execute_query(
                query,
                {"chunks": records_to_update}
            )

            if records:
                total_updated += records[0]["processed"]

            print(
                f"Embedded and stored "
                f"{total_updated}/{len(chunks)} chunks",
                flush=True
            )

        return total_updated
