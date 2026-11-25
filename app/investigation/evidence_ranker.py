
import re
from datetime import datetime, timezone


class EvidenceRanker:
    """
    Ranks historical incidents using:

    1. Graph dependency relevance
    2. Symptom similarity
    3. Temporal relevance
    4. Explicit incident references
    5. Evidence specificity

    Scores represent investigation priority, not
    probabilities or proof of root cause.
    """

    STOP_WORDS = {
        "the", "a", "an", "and", "or", "to", "of", "in",
        "on", "for", "with", "from", "was", "were", "is",
        "are", "after", "before", "while", "during", "by",
        "it", "its", "this", "that", "as", "at", "be",
        "has", "have", "had", "their", "they", "service",
        "incident", "experienced", "reported"
    }

    MAX_SYMPTOM_SCORE = 3.0

    def _tokenize(self, text: str) -> set[str]:
        words = re.findall(r"[a-zA-Z0-9]+", (text or "").lower())

        return {
            word for word in words
            if len(word) > 2 and word not in self.STOP_WORDS
        }

    def _parse_timestamp(self, value):
        """Convert supported timestamp values to timezone-aware UTC."""

        if not value:
            return None

        try:
            if isinstance(value, datetime):
                parsed = value
            else:
                parsed = datetime.fromisoformat(
                    str(value).replace("Z", "+00:00")
                )

            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)

            return parsed.astimezone(timezone.utc)

        except (ValueError, TypeError):
            return None

    def _get_service_groups(
        self,
        graph_paths: list[dict],
        primary_incident_id: str
    ) -> tuple[set[str], set[str]]:

        direct_services = set()
        downstream_services = set()

        for path in graph_paths:
            nodes = path.get("path_nodes", [])
            relationships = path.get("path_relationships", [])

            if not nodes or nodes[0].get("id") != primary_incident_id:
                continue

            if (
                relationships
                and relationships[0] == "AFFECTED"
                and len(nodes) > 1
                and "Service" in nodes[1].get("labels", [])
            ):
                service_id = nodes[1].get("id")

                if service_id:
                    direct_services.add(service_id)

            for node in nodes[1:]:
                if "Service" in node.get("labels", []):
                    service_id = node.get("id")

                    if service_id:
                        downstream_services.add(service_id)

        downstream_services -= direct_services

        return direct_services, downstream_services

    def _calculate_temporal_score(
        self,
        primary_timestamp,
        candidate_timestamp
    ) -> tuple[float, str]:

        primary_time = self._parse_timestamp(primary_timestamp)
        candidate_time = self._parse_timestamp(candidate_timestamp)

        if not primary_time or not candidate_time:
            return 0.0, "Temporal relevance unavailable"

        difference = abs(
            (primary_time - candidate_time).total_seconds()
        )

        hours = difference / 3600

        if hours <= 1:
            return 4.0, "Occurred within 1 hour"

        if hours <= 6:
            return 3.0, "Occurred within 6 hours"

        if hours <= 24:
            return 2.0, "Occurred within 24 hours"

        if hours <= 168:
            return 1.0, "Occurred within 7 days"

        return 0.0, "Occurred more than 7 days apart"


    def _calculate_direct_relationship_score(
        self,
        incident: dict,
        primary_incident: dict
    ) -> tuple[float, str]:

        primary_id = primary_incident.get("id")
        candidate_id = incident.get("id")

        primary_text = " ".join([
            str(primary_incident.get("title", "")),
            str(primary_incident.get("description", "")),
            str(primary_incident.get("investigation_notes", "")),
            str(primary_incident.get("resolution_summary", ""))
        ])

        candidate_text = " ".join([
            str(incident.get("title", "")),
            str(incident.get("description", "")),
            str(incident.get("investigation_notes", "")),
            str(incident.get("resolution_summary", ""))
        ])

        # Check whether the primary incident references the candidate.
        primary_references_candidate = bool(
            candidate_id and re.search(
                rf"\b{re.escape(candidate_id)}\b",
                primary_text,
                re.IGNORECASE
            )
        )

        # Check whether the candidate references the primary incident.
        candidate_references_primary = bool(
            primary_id and re.search(
                rf"\b{re.escape(primary_id)}\b",
                candidate_text,
                re.IGNORECASE
            )
        )

        if primary_references_candidate and candidate_references_primary:
            return 3.0, "Both incidents explicitly reference each other"

        if primary_references_candidate:
            return 3.0, "Primary incident explicitly references this incident"

        if candidate_references_primary:
            return 3.0, "Historical incident explicitly references primary incident"

        return 0.0, "No explicit incident-to-incident reference"


    def _calculate_evidence_specificity(
        self,
        incident: dict
    ) -> tuple[float, list[str]]:

        incident_text = " ".join([
            str(incident.get("title", "")),
            str(incident.get("description", "")),
            str(incident.get("investigation_notes", "")),
            str(incident.get("resolution_summary", ""))
        ]).lower()

        score = 0.0
        reasons = []

        # Concrete measurements or quantities.
        measurement_pattern = (
            r"\b\d+(?:\.\d+)?\s*"
            r"(?:ms|milliseconds|seconds|minutes|"
            r"percent|%|requests|connections|retries|threads)\b"
        )

        if re.search(measurement_pattern, incident_text):
            score += 1.0
            reasons.append("Contains quantified operational details")

        # Specific technical mechanisms.
        mechanisms = {
            "connection pool",
            "deadlock",
            "retry storm",
            "thread pool",
            "memory exhaustion",
            "cpu saturation",
            "queue backlog",
            "connection exhaustion",
            "cache inconsistency"
        }

        matched_mechanisms = [
            mechanism
            for mechanism in mechanisms
            if mechanism in incident_text
        ]

        if matched_mechanisms:
            score += 1.0
            reasons.append(
                "Documents specific mechanisms: "
                + ", ".join(matched_mechanisms)
            )

        return min(score, 2.0), reasons

    def rank_related_incidents(
        self,
        primary_incident: dict,
        related_incidents: list[dict],
        incident_details: list[dict],
        graph_paths: list[dict]
    ) -> list[dict]:

        if not primary_incident:
            return []

        primary_id = primary_incident.get("id")

        direct_services, downstream_services = (
            self._get_service_groups(graph_paths, primary_id)
        )

        primary_text = (
            f"{primary_incident.get('title', '')} "
            f"{primary_incident.get('description', '')} "
            f"{primary_incident.get('investigation_notes', '')}"
        )

        primary_tokens = self._tokenize(primary_text)

        details_by_id = {
            incident["id"]: incident
            for incident in incident_details
            if incident.get("id")
        }

        # Deduplicate related incidents.
        candidates = {}

        for relationship in related_incidents:
            source_id = relationship.get("source_incident")
            related_id = relationship.get("related_incident")
            shared_service = relationship.get("shared_service")

            candidate_id = None

            if source_id == primary_id:
                candidate_id = related_id
            elif related_id == primary_id:
                candidate_id = source_id

            if not candidate_id or candidate_id == primary_id:
                continue

            candidate = candidates.setdefault(
                candidate_id,
                {"shared_services": set()}
            )

            if shared_service:
                candidate["shared_services"].add(shared_service)

        ranked = []

        for incident_id, relationship in candidates.items():

            incident = details_by_id.get(incident_id)

            if not incident:
                continue

            shared_services = relationship["shared_services"]

            # 1. Graph relevance: maximum 3.
            if shared_services & direct_services:
                graph_score = 3.0
                graph_reason = "Shares a directly affected service"

            elif shared_services & downstream_services:
                graph_score = 2.0
                graph_reason = "Shares a downstream dependency"

            else:
                graph_score = 1.0
                graph_reason = "Connected through the incident graph"

            # 2. Symptom similarity: maximum 3.
            incident_text = (
                f"{incident.get('title', '')} "
                f"{incident.get('description', '')} "
                f"{incident.get('investigation_notes', '')}"
            )

            incident_tokens = self._tokenize(incident_text)

            matching_terms = sorted(
                primary_tokens & incident_tokens
            )

            symptom_score = min(
                len(matching_terms) * 0.5,
                self.MAX_SYMPTOM_SCORE
            )

            # 3. Temporal relevance: maximum 4.
            temporal_score, temporal_reason = (
                self._calculate_temporal_score(
                    primary_incident.get("timestamp"),
                    incident.get("timestamp")
                )
            )

            # 4. Explicit incident relationship: maximum 3.
            direct_relationship_score, relationship_reason = (
            self._calculate_direct_relationship_score(
                incident,
                primary_incident
            )
)

            # 5. Evidence specificity: maximum 2.
            evidence_score, evidence_reasons = (
                self._calculate_evidence_specificity(incident)
            )

            total_score = (
                graph_score
                + symptom_score
                + temporal_score
                + direct_relationship_score
                + evidence_score
            )

            reasons = [
                graph_reason,
                temporal_reason,
                relationship_reason
            ]

            if matching_terms:
                reasons.append(
                    "Shared symptom terms: "
                    + ", ".join(matching_terms)
                )

            reasons.extend(evidence_reasons)

            ranked.append({
                "incident_id": incident_id,
                "title": incident.get("title"),
                "severity": incident.get("severity"),
                "timestamp": incident.get("timestamp"),
                "shared_services": sorted(shared_services),

                "graph_score": graph_score,
                "symptom_score": symptom_score,
                "temporal_score": temporal_score,
                "direct_relationship_score": direct_relationship_score,
                "evidence_specificity_score": evidence_score,

                "total_score": round(total_score, 2),

                "matching_terms": matching_terms,
                "ranking_reasons": reasons
            })

        ranked.sort(
            key=lambda item: (
                -item["total_score"],
                -item["temporal_score"],
                -item["graph_score"],
                item["incident_id"]
            )
        )

        return ranked
