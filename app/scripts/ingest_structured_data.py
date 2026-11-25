from app.database.neo4j_client import Neo4jClient
from app.ingestion.json_loader import JSONLoader
from app.ingestion.entity_ingestor import EntityIngestor

from app.models import (
    Service,
    Database,
    KafkaTopic,
    Team,
    Incident,
    Deployment,
    Error
)


# Dataset file, JSON collection key, Neo4j label, Pydantic model
ENTITY_CONFIG = [
    (
        "services/services.json",
        "services",
        "Service",
        Service
    ),
    (
        "databases/databases.json",
        "databases",
        "Database",
        Database
    ),
    (
        "kafka/topics.json",
        "topics",
        "KafkaTopic",
        KafkaTopic
    ),
    (
        "teams/teams.json",
        "teams",
        "Team",
        Team
    ),
    (
        "errors/errors.json",
        "errors",
        "Error",
        Error
    ),
    (
        "deployments/deployments.json",
        "deployments",
        "Deployment",
        Deployment
    ),
    (
        "incidents/incidents.json",
        "incidents",
        "Incident",
        Incident
    )
]


def main():

    client = Neo4jClient()
    loader = JSONLoader(data_dir="data")
    ingestor = EntityIngestor(client)

    try:
        client.verify_connection()

        total = 0

        for file_path, collection_key, label, model in ENTITY_CONFIG:

            print(f"\nLoading {label}...")

            raw_entities = loader.load_entities(
                file_path,
                collection_key
            )

            count = ingestor.ingest(
                label=label,
                model_class=model,
                raw_entities=raw_entities
            )

            total += count

        print("\n--------------------------------")
        print(f"Total entities processed: {total}")
        print("Structured data ingestion completed")
        print("--------------------------------")

    finally:
        client.close()


if __name__ == "__main__":
    print("Starting structured data ingestion...", flush=True)
    main()