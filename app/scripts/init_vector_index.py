from app.database.neo4j_client import Neo4jClient
from app.config.settings import settings


def main():

    client = Neo4jClient()

    try:
        client.verify_connection()

        dimension = int(settings.EMBEDDING_DIMENSION)

        query = f"""
        CREATE VECTOR INDEX document_chunk_embedding
        IF NOT EXISTS
        FOR (c:DocumentChunk)
        ON (c.embedding)
        OPTIONS {{
            indexConfig: {{
                `vector.dimensions`: {dimension},
                `vector.similarity_function`: 'cosine'
            }}
        }}
        """

        client.execute_query(query)

        client.execute_query(
            "CALL db.awaitIndexes(300)"
        )

        print("Vector index initialized successfully")

    finally:
        client.close()


if __name__ == "__main__":
    main()