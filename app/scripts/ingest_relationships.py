from app.database.neo4j_client import Neo4jClient
from app.ingestion.json_loader import JSONLoader
from app.ingestion.relationship_ingestor import RelationshipIngestor


def build_relationships(entities, source_id_field, target_id_field):
    """
    Convert entity references into source-target pairs.

    Example:
    {
        "id": "SVC-PAY",
        "depends_on": ["SVC-CUS", "SVC-FRA"]
    }

    Becomes:
    [
        {"source_id": "SVC-PAY", "target_id": "SVC-CUS"},
        {"source_id": "SVC-PAY", "target_id": "SVC-FRA"}
    ]
    """

    relationships = []

    for entity in entities:
        source_id = entity.get(source_id_field)

        if not source_id:
            continue

        target_ids = entity.get(target_id_field, [])

        if isinstance(target_ids, str):
            target_ids = [target_ids]

        for target_id in target_ids:
            if target_id:
                relationships.append({
                    "source_id": source_id,
                    "target_id": target_id
                })

    return relationships


def main():

    client = Neo4jClient()
    loader = JSONLoader(data_dir="data")
    ingestor = RelationshipIngestor(client)

    try:
        client.verify_connection()

        # Load source entity files
        services = loader.load_entities(
            "services/services.json", "services"
        )

        databases = loader.load_entities(
            "databases/databases.json", "databases"
        )

        topics = loader.load_entities(
            "kafka/topics.json", "topics"
        )

        incidents = loader.load_entities(
            "incidents/incidents.json", "incidents"
        )

        deployments = loader.load_entities(
            "deployments/deployments.json", "deployments"
        )

        total = 0

        # 1. Service -> Service
        total += ingestor.ingest(
            "Service", "DEPENDS_ON", "Service",
            build_relationships(services, "id", "depends_on")
        )

        # 2. Service -> Database
        total += ingestor.ingest(
            "Service", "USES", "Database",
            build_relationships(services, "id", "uses_databases")
        )

        # 3. Service -> KafkaTopic
        total += ingestor.ingest(
            "Service", "PRODUCES", "KafkaTopic",
            build_relationships(services, "id", "produces_topics")
        )

        total += ingestor.ingest(
            "Service", "CONSUMES", "KafkaTopic",
            build_relationships(services, "id", "consumes_topics")
        )

        # 4. Service -> Team
        total += ingestor.ingest(
            "Service", "OWNED_BY", "Team",
            build_relationships(services, "id", "team_id")
        )

        # 5. Incident -> Service
        total += ingestor.ingest(
            "Incident", "AFFECTED", "Service",
            build_relationships(
                incidents, "id", "affected_service_ids"
            )
        )

        # 6. Incident -> Error
        total += ingestor.ingest(
            "Incident", "OBSERVED", "Error",
            build_relationships(
                incidents, "id", "observed_error_ids"
            )
        )

        # 7. Incident -> Deployment
        total += ingestor.ingest(
            "Incident", "ASSOCIATED_WITH", "Deployment",
            build_relationships(
                incidents, "id", "associated_deployment_ids"
            )
        )

        # 8. Deployment -> Service
        total += ingestor.ingest(
            "Deployment", "DEPLOYED_TO", "Service",
            build_relationships(
                deployments, "id", "service_id"
            )
        )

        print("\n--------------------------------")
        print(f"Total relationships processed: {total}")
        print("Relationship ingestion completed")
        print("--------------------------------")

    finally:
        client.close()


if __name__ == "__main__":
    main()