
from app.models.rca_report import RCAReport


class RCAValidator:
    """
    Validates LLM-generated RCA reports against retrieved investigation data.

    This is a conservative validation layer, not a causal proof engine.
    """

    # Phrases that may indicate direct confirmation of a failure mechanism.
    # A matching phrase is only a signal; it is not proof by itself.
    DIRECT_CONFIRMATION_MARKERS = (
        "confirmed by metrics",
        "metrics confirmed",
        "trace confirmed",
        "distributed trace showed",
        "resolved after rollback",
        "recovered after rollback",
        "reproduced the failure",
        "root cause confirmed",
        "confirmed root cause",
    )

    def _collect_valid_ids(self, context: dict) -> set[str]:
        valid_ids = set()

        # Incidents
        for incident in context.get("incidents", []):
            if incident.get("id"):
                valid_ids.add(incident["id"])

        # Deployments
        for deployment in context.get("deployments", []):
            if deployment.get("id"):
                valid_ids.add(deployment["id"])

        # Entities found in graph paths
        for path in context.get("graph_paths", []):
            for node in path.get("path_nodes", []):
                if node.get("id"):
                    valid_ids.add(node["id"])

        # Retrieved documents
        for document in context.get("documents", []):
            for key in ("document_id", "chunk_id"):
                if document.get(key):
                    valid_ids.add(document[key])

        # Primary incident
        primary_id = context.get("primary_incident_id")
        if primary_id:
            valid_ids.add(primary_id)

        return valid_ids


    def _collect_service_ids(self, context: dict) -> set[str]:
        service_ids = set()

        # Services present in graph paths
        for path in context.get("graph_paths", []):
            for node in path.get("path_nodes", []):
                if (
                    "Service" in node.get("labels", [])
                    and node.get("id")
                ):
                    service_ids.add(node["id"])

        # Services affected by all loaded incidents
        for incident in context.get("incidents", []):
            for service_id in incident.get("affected_service_ids") or []:
                service_ids.add(service_id)

        # Services associated with deployments
        for deployment in context.get("deployments", []):
            service_id = deployment.get("service_id")
            if service_id:
                service_ids.add(service_id)

        # Services present in the investigation timeline
        for event in context.get("timeline", []):
            service_id = event.get("service_id")
            if service_id:
                service_ids.add(service_id)

        # Primary incident
        primary = context.get("primary_incident") or {}

        for service_id in primary.get("affected_service_ids") or []:
            service_ids.add(service_id)

        return service_ids

    

    def _collect_database_ids(self, context: dict) -> set[str]:
        database_ids = set()

        for path in context.get("graph_paths", []):
            for node in path.get("path_nodes", []):
                if "Database" in node.get("labels", []) and node.get("id"):
                    database_ids.add(node["id"])

        return database_ids


    def _collect_deployment_ids(self, context: dict) -> set[str]:
        return {
            deployment["id"]
            for deployment in context.get("deployments", [])
            if deployment.get("id")
        }

    def _has_direct_confirmation(self, hypothesis) -> bool:
        evidence_text = " ".join(
            [
                hypothesis.description,
                *[
                    evidence.description
                    for evidence in hypothesis.supporting_evidence
                ]
            ]
        ).lower()

        return any(
            marker in evidence_text
            for marker in self.DIRECT_CONFIRMATION_MARKERS
        )

    def _validate_hypothesis(
        self,
        hypothesis,
        valid_ids: set[str],
        service_ids: set[str],
        database_ids: set[str],
        deployments: dict
    ):
        warnings = list(hypothesis.validation_warnings)

        # 1. Validate evidence references
        valid_evidence = []

        for evidence in hypothesis.supporting_evidence:
            if evidence.evidence_id in valid_ids:
                valid_evidence.append(evidence)
            else:
                warnings.append(
                    f"Unsupported evidence reference removed: "
                    f"{evidence.evidence_id}"
                )

        hypothesis.supporting_evidence = valid_evidence

        # 2. Validate service references
        valid_services = []

        for service_id in hypothesis.related_services:
            if service_id in service_ids:
                valid_services.append(service_id)
            else:
                warnings.append(
                    f"Unknown or unsupported service reference: {service_id}"
                )

        hypothesis.related_services = valid_services

        # 3. Validate database references
        valid_databases = []

        for database_id in hypothesis.related_databases:
            if database_id in database_ids:
                valid_databases.append(database_id)
            else:
                warnings.append(
                    f"Unknown or unsupported database reference: {database_id}"
                )

        hypothesis.related_databases = valid_databases

        # 4. Validate deployment references and service associations
        valid_deployments = []

        for deployment_id in hypothesis.related_deployments:
            deployment = deployments.get(deployment_id)

            if not deployment:
                warnings.append(
                    f"Unknown or unsupported deployment reference: "
                    f"{deployment_id}"
                )
                continue

            deployment_service_id = deployment.get("service_id")

            if deployment_service_id not in hypothesis.related_services:
                warnings.append(
                    f"Deployment {deployment_id} removed: its service "
                    f"({deployment_service_id}) is not listed among the "
                    f"hypothesis-related services."
                )
                continue

            valid_deployments.append(deployment_id)

            warnings.append(
                f"{deployment_id} belongs to {deployment_service_id}. "
                "Its association is valid, but its causal contribution "
                "is not established."
            )

        hypothesis.related_deployments = valid_deployments

        # 5. Conservative confidence calibration
        if hypothesis.confidence == "HIGH":
            if not self._has_direct_confirmation(hypothesis):
                hypothesis.confidence = "MEDIUM"

                warnings.append(
                    "Confidence downgraded from HIGH to MEDIUM: "
                    "the supplied evidence does not contain explicit "
                    "confirmation of the proposed failure mechanism."
                )

                hypothesis.confidence_reason += (
                    " Application validation downgraded confidence "
                    "because direct confirmation was not found."
                )

        if not hypothesis.supporting_evidence:
            hypothesis.confidence = "LOW"

            warnings.append(
                "No valid supporting evidence references remain."
            )

        hypothesis.validation_warnings = list(dict.fromkeys(warnings))

        return hypothesis

    
    
    
    def _classify_services(self, report, context):
        primary = context.get("primary_incident") or {}

        # Services directly affected by the primary incident
        direct_services = set(primary.get("affected_service_ids") or [])

        if not direct_services:
            direct_services = set(report.impacted_services)

        # Services identified as suspected contributors by the hypotheses
        candidate_services = set()

        for hypothesis in report.root_cause_hypotheses:
            candidate_services.update(hypothesis.related_services)

        graph_services = self._collect_service_ids(context)

        suspected_services = candidate_services - direct_services

        # Other graph-connected services that still need investigation
        services_requiring_investigation = (
            graph_services - direct_services - suspected_services
        )

        report.directly_impacted_services = sorted(direct_services)
        report.suspected_contributing_services = sorted(suspected_services)
        report.services_requiring_investigation = sorted(
            services_requiring_investigation
        )

        report.impacted_services = sorted(direct_services)

    def _build_investigation_steps(self, report: RCAReport):
        steps = []

        for hypothesis in report.root_cause_hypotheses:
            for step in hypothesis.recommended_validation_steps:
                steps.append({
                    "hypothesis": hypothesis.title,
                    "step": step
                })

        # Deduplicate while preserving order.
        unique_steps = []
        seen = set()

        for item in steps:
            key = item["step"].strip().lower()

            if key not in seen:
                seen.add(key)
                unique_steps.append(
                    f"[{item['hypothesis']}] {item['step']}"
                )

        report.investigation_steps = unique_steps

    def validate(self, report: RCAReport, context: dict) -> RCAReport:

        valid_ids = self._collect_valid_ids(context)
        service_ids = self._collect_service_ids(context)
        database_ids = self._collect_database_ids(context)
        deployments = self._collect_deployments(context)

        for hypothesis in report.root_cause_hypotheses:
            self._validate_hypothesis(
                hypothesis=hypothesis,
                valid_ids=valid_ids,
                service_ids=service_ids,
                database_ids=database_ids,
                deployments=deployments
            )

        self._classify_services(report, context)
        self._build_investigation_steps(report)

        report.validation_warnings = list(
            dict.fromkeys(
                warning
                for hypothesis in report.root_cause_hypotheses
                for warning in hypothesis.validation_warnings
            )
        )

        return report

    def _collect_deployments(self, context: dict) -> dict:
        """
        Return deployment records indexed by deployment ID.
        """
        return {
            deployment["id"]: deployment
            for deployment in context.get("deployments", [])
            if deployment.get("id")
        }
