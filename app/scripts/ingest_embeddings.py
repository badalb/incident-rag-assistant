
from app.database.neo4j_client import Neo4jClient

from app.ingestion.markdown_loader import MarkdownLoader
from app.ingestion.document_chunker import DocumentChunker
from app.ingestion.embedding_service import EmbeddingService
from app.ingestion.embedding_ingestor import EmbeddingIngestor


def main():

    client = Neo4jClient()

    try:
        client.verify_connection()

        # Step 1: Load documents
        loader = MarkdownLoader(data_dir="data")
        documents = loader.load_documents()

        print(f"Documents loaded: {len(documents)}")

        # Step 2: Generate chunks
        chunker = DocumentChunker(
            chunk_size=1200,
            chunk_overlap=150
        )

        all_chunks = []

        for document in documents:
            chunks = chunker.chunk_document(document)
            all_chunks.extend(chunks)

        print(f"Total chunks generated: {len(all_chunks)}")

        # Step 3: Convert chunks to dictionaries
        chunk_records = [
            chunk.model_dump(mode="json", exclude_none=True)
            for chunk in all_chunks
        ]

        # Step 4: Generate and persist embeddings
        embedding_service = EmbeddingService()

        embedding_ingestor = EmbeddingIngestor(
            client=client,
            embedding_service=embedding_service,
            batch_size=50
        )

        total_updated = embedding_ingestor.ingest(
            chunk_records
        )

        print(f"\nTotal embeddings stored: {total_updated}")

    finally:
        client.close()


if __name__ == "__main__":
    main()
