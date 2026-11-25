
from app.database.neo4j_client import Neo4jClient
from app.ingestion.embedding_service import EmbeddingService
from app.retrieval.vector_search import VectorSearch


def main():

    client = Neo4jClient()

    try:
        client.verify_connection()

        embedding_service = EmbeddingService()

        vector_search = VectorSearch(
            client=client,
            embedding_service=embedding_service
        )

        query = "Why are payment requests timing out?"

        results = vector_search.search(
            query_text=query,
            top_k=5
        )

        print(f"\nQuery: {query}\n")

        for index, result in enumerate(results, start=1):

            print(f"\nResult {index}")
            print(f"Chunk ID: {result['chunk_id']}")
            print(f"Document: {result['document_title']}")
            print(f"Source: {result['source_file']}")
            print(f"Score: {result['score']:.4f}")
            print(f"Content: {result['content'][:500]}")
            

    finally:
        client.close()


if __name__ == "__main__":
    main()
