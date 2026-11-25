
from app.database.neo4j_client import Neo4jClient
from app.ingestion.markdown_loader import MarkdownLoader
from app.ingestion.document_chunker import DocumentChunker
from app.ingestion.entity_linker import EntityLinker


def main():

    client = Neo4jClient()

    try:
        client.verify_connection()

        # Recreate the same deterministic chunks.
        loader = MarkdownLoader(data_dir="data")
        documents = loader.load_documents()

        chunker = DocumentChunker(
            chunk_size=1200,
            chunk_overlap=150
        )

        all_chunks = []

        for document in documents:
            all_chunks.extend(
                chunker.chunk_document(document)
            )

        chunk_records = [
            chunk.model_dump(
                mode="json",
                exclude_none=True
            )
            for chunk in all_chunks
        ]

        # Link chunks to graph entities.
        linker = EntityLinker(client)

        linker.link_chunks(chunk_records)

        print("Entity linking completed successfully")

    finally:
        client.close()


if __name__ == "__main__":
    main()
