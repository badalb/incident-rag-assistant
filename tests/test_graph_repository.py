from app.database.neo4j_client import Neo4jClient
from app.database.graph_repository import GraphRepository

def test_create_service_node():
    client = Neo4jClient()
    repository = GraphRepository(client)

    try:
        repository.upsert_node(
            "Service",
            {
                "id": "TEST-SVC-001",
                "name": "Test Payment Service",
                "description": "Test service"
            }
        )

        records = client.execute_query(
            """
            MATCH (s:Service {id: $id})
            RETURN s.name AS name
            """,
            {"id": "TEST-SVC-001"}
        )

        assert len(records) == 1
        assert records[0]["name"] == "Test Payment Service"

    finally:
        client.execute_query(
            "MATCH (s:Service {id: $id}) DETACH DELETE s",
            {"id": "TEST-SVC-001"}
        )
        client.close()