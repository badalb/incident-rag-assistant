from app.database.neo4j_client import Neo4jClient
from app.database.schema import initialize_schema


def main():
    client = Neo4jClient()

    try:
        client.verify_connection()
        initialize_schema(client)

    finally:
        client.close()


if __name__ == "__main__":
    main()