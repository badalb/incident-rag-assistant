
from app.database.neo4j_client import Neo4jClient
from app.ingestion.markdown_loader import MarkdownLoader
from app.ingestion.document_chunker import DocumentChunker
from app.ingestion.document_ingestor import DocumentIngestor


def main():

    client = Neo4jClient()

    try:
        client.verify_connection()

        # Step 1: Load Markdown documents
        loader = MarkdownLoader(data_dir="data")
        documents = loader.load_documents()

        print(f"\nDocuments loaded: {len(documents)}")

        # Step 2: Chunk documents
        chunker = DocumentChunker(
            chunk_size=1200,
            chunk_overlap=150
        )

        all_chunks = []

        for document in documents:
            chunks = chunker.chunk_document(document)
            all_chunks.extend(chunks)

            print(
                f"{document.id}: "
                f"{len(chunks)} chunks generated"
            )

        print(f"\nTotal chunks generated: {len(all_chunks)}")

        # Step 3: Convert Pydantic models to dictionaries
        chunk_records = [
            chunk.model_dump(mode="json", exclude_none=True)
            for chunk in all_chunks
        ]

        # Step 4: Persist chunks in Neo4j
        ingestor = DocumentIngestor(client)

        total_ingested = ingestor.ingest(chunk_records)

        print(f"\nTotal chunks ingested: {total_ingested}")
        print("Document ingestion completed successfully")

    finally:
        client.close()


if __name__ == "__main__":
    main()
