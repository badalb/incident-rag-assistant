from app.database.neo4j_client import Neo4jClient


NODE_LABELS = [
    "Service",
    "Database",
    "KafkaTopic",
    "Team",
    "Incident",
    "Deployment",
    "Error",
    "Runbook",
    "DocumentChunk"
]


def create_constraints(client: Neo4jClient):
    for label in NODE_LABELS:
        query = f"""
        CREATE CONSTRAINT {label.lower()}_id_unique IF NOT EXISTS
        FOR (n:{label})
        REQUIRE n.id IS UNIQUE
        """

        client.execute_query(query)

        print(f"Created constraint for {label}")


def initialize_schema(client: Neo4jClient):
    create_constraints(client)
    print("Neo4j schema initialization completed")