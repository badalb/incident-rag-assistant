
from app.database.neo4j_client import Neo4jClient
from app.investigation.path_classifier import GraphPathClassifier
from app.investigation.evidence_ranker import EvidenceRanker


class InvestigationContextBuilder:
    """
    Builds a structured investigation context by combining:

    1. Vector retrieval results
    2. Primary incident details
    3. Related historical incidents
    4. Deployment information
    5. Multi-hop graph paths
    6. Classified graph evidence
    7. Ranked historical evidence
    8. Chronological investigation timeline
    """

    def __init__(self, client: Neo4jClient):
        self.client = client
        self.path_classifier = GraphPathClassifier()
        self.evidence_ranker = EvidenceRanker()

    # --------------------------------------------------
    # Step 1: Extract incident IDs from retrieval results
    # --------------------------------------------------

    def _extract_incident_ids(
        self,
        retrieval_result: dict
    ) -> set[str]:

        incident_ids = set()

        # Always include the primary incident.
        primary_id = retrieval_result.get("primary_incident_id")

        if primary_id:
            incident_ids.add(primary_id)

        # Include incidents appearing in graph paths.
        for path in retrieval_result.get("graph_paths", []):

            for node in path.get("path_nodes", []):

                if "Incident" in node.get("labels", []):
                    incident_id = node.get("id")

                    if incident_id:
                        incident_ids.add(incident_id)

        # Include incidents connected through shared services.
        for item in retrieval_result.get("related_incidents", []):

            for key in ("source_incident", "related_incident"):

                incident_id = item.get(key)

                if incident_id:
                    incident_ids.add(incident_id)

        return incident_ids

    # --------------------------------------------------
    # Step 2: Load incident details
    # --------------------------------------------------

    def _load_incidents(
        self,
        incident_ids: list[str]
    ) -> list[dict]:

        if not incident_ids:
            return []

        query = """
        MATCH (i:Incident)
        WHERE i.id IN $incident_ids

        RETURN
            i.id AS id,
            i.title AS title,
            i.timestamp AS timestamp,
            i.severity AS severity,
            i.status AS status,
            i.description AS description,
            i.investigation_notes AS investigation_notes,
            i.resolution_summary AS resolution_summary,
            i.affected_service_ids AS affected_service_ids,
            i.observed_error_ids AS observed_error_ids,
            i.associated_deployment_ids AS associated_deployment_ids

        ORDER BY i.timestamp
        """

        records = self.client.execute_query(
            query,
            {"incident_ids": incident_ids}
        )

        return [record.data() for record in records]

    # --------------------------------------------------
    # Step 3: Load deployment details
    # --------------------------------------------------

    def _load_deployments(
        self,
        deployment_ids: list[str]
    ) -> list[dict]:

        if not deployment_ids:
            return []

        query = """
        MATCH (d:Deployment)
        WHERE d.id IN $deployment_ids

        OPTIONAL MATCH (d)-[:DEPLOYED_TO]->(s:Service)

        RETURN
            d.id AS id,
            d.version AS version,
            d.timestamp AS timestamp,
            d.environment AS environment,
            d.status AS status,
            d.change_summary AS change_summary,
            d.change_ticket AS change_ticket,
            s.id AS service_id,
            s.name AS service_name

        ORDER BY d.timestamp
        """

        records = self.client.execute_query(
            query,
            {"deployment_ids": deployment_ids}
        )

        return [record.data() for record in records]

    # --------------------------------------------------
    # Step 4: Build investigation timeline
    # --------------------------------------------------

    def _build_timeline(
        self,
        incidents: list[dict],
        deployments: list[dict]
    ) -> list[dict]:

        timeline = []

        for incident in incidents:

            timeline.append({
                "timestamp": incident["timestamp"],
                "event_type": "INCIDENT",
                "event_id": incident["id"],
                "description": incident["title"],
                "severity": incident.get("severity")
            })

        for deployment in deployments:

            timeline.append({
                "timestamp": deployment["timestamp"],
                "event_type": "DEPLOYMENT",
                "event_id": deployment["id"],
                "description": deployment.get("change_summary"),
                "service_id": deployment.get("service_id"),
                "service_name": deployment.get("service_name"),
                "version": deployment.get("version"),
                "status": deployment.get("status")
            })

        # Chronological ordering.
        timeline.sort(
            key=lambda event: event["timestamp"]
        )

        return timeline

    # --------------------------------------------------
    # Step 5: Build complete investigation context
    # --------------------------------------------------

    def build(
        self,
        retrieval_result: dict
    ) -> dict:

        # Extract incident IDs.
        incident_ids = sorted(
            self._extract_incident_ids(retrieval_result)
        )

        # Load incident details.
        incidents = self._load_incidents(incident_ids)

        # Identify primary incident.
        primary_incident_id = retrieval_result.get(
            "primary_incident_id"
        )

        primary_incident = next(
            (
                incident
                for incident in incidents
                if incident["id"] == primary_incident_id
            ),
            None
        )

        # Collect deployment IDs associated with incidents.
        deployment_ids = set()

        for incident in incidents:

            deployment_ids.update(
                incident.get("associated_deployment_ids") or []
            )

        # Load deployment details.
        deployments = self._load_deployments(
            sorted(deployment_ids)
        )

        # Build timeline.
        timeline = self._build_timeline(
            incidents,
            deployments
        )

        # --------------------------------------------------
        # Step 6: Classify graph paths
        # --------------------------------------------------

        graph_paths = retrieval_result.get(
            "graph_paths", []
        )

        classified_paths = self.path_classifier.classify_all(
            graph_paths=graph_paths,
            primary_incident_id=primary_incident_id
        )

        # --------------------------------------------------
        # Step 7: Rank historical incident evidence
        # --------------------------------------------------

        related_incidents = retrieval_result.get(
            "related_incidents", []
        )

        ranked_evidence = self.evidence_ranker.rank_related_incidents(
            primary_incident=primary_incident,
            related_incidents=related_incidents,
            incident_details=incidents,
            graph_paths=graph_paths
        )

        # --------------------------------------------------
        # Step 8: Return structured investigation context
        # --------------------------------------------------

        return {
            "query": retrieval_result.get("query"),

            "primary_incident_id": primary_incident_id,
            "primary_incident_chunk_id": retrieval_result.get(
                "primary_incident_chunk_id"
            ),
            "primary_incident": primary_incident,

            "documents": retrieval_result.get(
                "documents", []
            ),

            "incidents": incidents,
            "deployments": deployments,

            "graph_paths": graph_paths,
            "classified_paths": classified_paths,

            "related_incidents": related_incidents,
            "ranked_evidence": ranked_evidence,

            "timeline": timeline,

            "summary": {
                "incident_count": len(incidents),
                "deployment_count": len(deployments),
                "graph_path_count": len(graph_paths),
                "classified_path_count": len(classified_paths),
                "related_incident_count": len(related_incidents),
                "ranked_evidence_count": len(ranked_evidence),
                "timeline_event_count": len(timeline)
            }
        }
