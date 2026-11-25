
from app.database.neo4j_client import Neo4jClient
from app.ingestion.embedding_service import EmbeddingService


class VectorSearch:

    def __init__(
        self,
        client: Neo4jClient,
        embedding_service: EmbeddingService
    ):
        self.client = client
        self.embedding_service = embedding_service

    def search(
        self,
        query_text: str,
        top_k: int = 5
    ):

        # Generate embedding for the user's question.
        query_embedding = (
            self.embedding_service.generate_embeddings(
                [query_text]
            )[0]
        )

        query = """
        CALL db.index.vector.queryNodes(
            'document_chunk_embedding',
            $top_k,
            $query_embedding
        )
        YIELD node, score

        RETURN
            node.id AS chunk_id,
            node.document_id AS document_id,
            node.document_title AS document_title,
            node.document_type AS document_type,
            node.source_file AS source_file,
            node.content AS content,
            score

        ORDER BY score DESC
        """

        records = self.client.execute_query(
            query,
            {
                "top_k": top_k,
                "query_embedding": query_embedding
            }
        )

        return [
            record.data()
            for record in records
        ]
