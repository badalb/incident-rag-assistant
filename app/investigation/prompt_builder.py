
import json


class RCAPromptBuilder:
    """
    Builds a compact, evidence-grounded prompt from the investigation context.
    """

    def _compact_documents(self, documents: list[dict]) -> list[dict]:
        compact = []

        for document in documents[:8]:
            compact.append({
                "document_id": document.get("document_id"),
                "chunk_id": document.get("chunk_id"),
                "document_title": document.get("document_title"),
                "document_type": document.get("document_type"),
                "score": document.get("score"),
                "content": (document.get("content") or "")[:1800]
            })

        return compact

    def _compact_graph_paths(self, paths: list[dict]) -> list[dict]:
        compact = []

        for path in paths[:30]:
            nodes = []

            for node in path.get("path_nodes", []):
                nodes.append({
                    "id": node.get("id"),
                    "labels": node.get("labels", []),
                    "name": node.get("name")
                })

            compact.append({
                "nodes": nodes,
                "relationships": path.get("path_relationships", [])
            })

        return compact

    def _build_evidence_payload(self, context: dict) -> dict:
        return {
            "primary_incident": context.get("primary_incident"),
            "related_incidents": context.get("ranked_evidence", []),
            "incident_details": context.get("incidents", []),
            "deployments": context.get("deployments", []),
            "timeline": context.get("timeline", []),
            "classified_graph_paths": context.get("classified_paths", []),
            "graph_paths": self._compact_graph_paths(
                context.get("graph_paths", [])
            ),
            "retrieved_documents": self._compact_documents(
                context.get("documents", [])
            ),
            "context_summary": context.get("summary", {})
        }

    def build_prompt(self, context: dict) -> str:
        evidence = self._build_evidence_payload(context)

        evidence_json = json.dumps(
            evidence,
            indent=2,
            default=str
        )

        return f"""
You are an experienced Site Reliability Engineer (SRE) performing
an evidence-based enterprise incident root cause investigation.

Your task is to analyze the supplied incident records, deployment history,
service dependencies, historical incidents, and technical documents.

Produce a structured Root Cause Analysis (RCA) report that helps
an on-call engineer understand the incident and investigate its
most plausible explanations.

PRIMARY INVESTIGATION QUESTION:
{context.get("query", "Investigate the primary incident.")}


EVIDENCE:
{evidence_json}


INVESTIGATION RULES:

1. EVIDENCE-GROUNDED ANALYSIS

   Use only the supplied evidence.

   Do not invent:
   - Metrics or measurements.
   - Events or timestamps.
   - Configuration changes.
   - Service behavior.
   - Infrastructure failures.
   - Telemetry observations.
   - Remediation actions.

   If information is unavailable, explicitly identify it as missing.

2. FACTS VS HYPOTHESES

   Clearly distinguish:
   - Observed facts.
   - Plausible explanations.
   - Assumptions.
   - Missing evidence.

   Do not present a hypothesis as an established root cause.

3. GRAPH RELATIONSHIPS

   A graph relationship indicates a known dependency or association.

   It does not prove that one component caused another component's failure.

   A service appearing in a dependency path does not establish that
   the service experienced a failure.

   A shared service between two historical incidents indicates related
   operational context, not necessarily a shared root cause.

4. TEMPORAL CORRELATION

   A deployment occurring before an incident is temporal correlation,
   not proof that the deployment caused the incident.

   Two incidents occurring close together do not automatically establish
   a causal relationship.

5. HYPOTHESIS GENERATION

   Identify multiple plausible explanations when supported by evidence.

   Rank hypotheses by the strength and relevance of the available evidence.

   For every hypothesis:
   - Explain the proposed failure mechanism.
   - Reference supporting evidence using actual IDs.
   - Identify contradicting evidence or missing information.
   - Explain the qualitative confidence level.
   - Suggest concrete validation steps.

   Do not invent a hypothesis merely to reach a target count.

6. CONFIDENCE LEVELS

   Confidence must be exactly LOW, MEDIUM, or HIGH.

   HIGH:
   Direct evidence establishes the failure mechanism, preferably with
   corroborating telemetry or confirmed remediation.

   MEDIUM:
   Multiple relevant pieces of evidence support the hypothesis,
   but the causal mechanism is not fully established.

   LOW:
   The hypothesis is plausible but supported mainly by indirect,
   incomplete, or historical evidence.

   Temporal correlation and graph connectivity alone must never
   justify HIGH confidence.

   Missing telemetry must be reflected in the confidence assessment.

   Confidence is qualitative, not a statistical probability.

7. MISSING TELEMETRY

   Explicitly identify missing telemetry that would help confirm
   or reject each hypothesis.

   Examples include:
   - Service latency.
   - Connection pool utilization.
   - Retry counts.
   - Error rates.
   - CPU utilization.
   - Memory utilization.
   - Database connection metrics.
   - Query latency.
   - Kafka consumer lag.

   Do not claim these measurements exist unless they appear
   in the supplied evidence.

8. ROOT CAUSE CLAIMS

   Do not declare a definitive root cause unless the evidence establishes it.

   If the evidence is insufficient, clearly state that the root cause
   remains unconfirmed.

9. DATABASE AND CONNECTION POOL EVIDENCE

   Distinguish application-side connection pool exhaustion from
   database-side resource saturation.

   Connection pool exhaustion does not automatically establish:
   - Database overload.
   - High database CPU or memory utilization.
   - Slow database queries.
   - Database lock contention.
   - Database-side connection saturation.

   Possible application-side explanations include:
   - Insufficient connection pool capacity.
   - Increased application concurrency.
   - Connections held for an extended duration.
   - Slow database operations.
   - Connections not being released correctly.

   Only state a specific mechanism when supported by supplied evidence.

   If the evidence establishes connection pool exhaustion but does not
   establish its underlying cause, describe the observed condition
   without guessing its cause.

10. EVIDENCE DESCRIPTION

    Every supporting evidence description must accurately summarize
    the source identified by its evidence_id.

    Do not add facts, measurements, causal conclusions, or mechanisms
    that are absent from the source evidence.

    Use only IDs present in the supplied investigation data.

    Use one supporting evidence entry per evidence ID within a hypothesis.

    Do not create multiple entries for the same evidence ID with
    slightly different descriptions.

11. HYPOTHESIS TITLES AND DESCRIPTIONS

    Titles must describe the proposed failure mechanism without
    presenting an unverified explanation as an established fact.

    Prefer:
    "Customer Service Degradation Associated with Connection Pool Exhaustion"

    Avoid:
    "Customer Database Overload"

    unless database overload is explicitly established by the evidence.

    Keep descriptions technically precise and avoid unsupported
    causal statements.

12. HYPOTHESIS COVERAGE

    When at least two plausible explanations are supported by the evidence,
    generate at least two and preferably three competing hypotheses.

    Consider:
    - Downstream service degradation.
    - Retry amplification or traffic spikes.
    - Database or infrastructure bottlenecks.
    - Other relevant service dependencies.

    Do not invent a hypothesis merely to reach a target count.

13. HYPOTHESIS CONSOLIDATION

    Do not generate multiple hypotheses that merely describe different
    stages of the same proposed failure chain.

    For example, Customer Service latency and its documented
    connection pool exhaustion may belong to one hypothesis.

    Keep distinct mechanisms separate, such as:
    - Downstream service degradation.
    - Payment retry amplification.

    Do not merge hypotheses merely because they share a service,
    database, deployment, or historical incident.

    Consolidation must not increase confidence.

14. DEPLOYMENT CAUSALITY

    Distinguish:
    - Deployment associated with the incident.
    - Deployment that changed a potentially relevant configuration.
    - Deployment confirmed to have introduced the failure.

    A deployment preceding an incident is not sufficient to establish
    deployment causality.

    Include a deployment in a hypothesis only when its service and
    change information are relevant to the proposed mechanism.

    A deployment association does not establish causality.

15. SERVICE AND DATABASE REFERENCES

    Use only service and database IDs present in the supplied evidence.

    Include a related database only when the evidence supports its
    relevance to the hypothesis.

    A database appearing in a dependency graph does not establish
    that the database experienced a failure.

    Distinguish:
    - Directly impacted services.
    - Suspected contributing services.
    - Services requiring further investigation.

    Do not describe a downstream dependency as directly impacted
    unless the supplied evidence supports that conclusion.

16. TIMELINE AND REMEDIATION

    Do not infer incident resolution timestamps or remediation sequences
    unless explicitly supported by the supplied evidence.

    Do not describe an incident as resolved because another service
    stabilized unless the source evidence explicitly establishes
    that sequence.

17. ERROR SIGNATURES

    Treat observed error signatures as symptoms unless the source
    evidence explicitly identifies their origin.

    Do not attribute an error to a particular downstream service
    or database merely because that component is connected
    in the dependency graph.

18. REPORT QUALITY

    Keep the report concise, technical, and useful to an on-call engineer.

    Prefer specific validation actions over generic recommendations.

    Every recommendation should help confirm or reject a hypothesis.


SPECIAL INSTRUCTIONS FOR THIS INVESTIGATION:

- The primary incident is the incident selected by the retrieval process.
- Explicitly evaluate INC-112 and DEP-002 as a possible
  retry-amplification hypothesis.
- Do not assume that a retry storm occurred during INC-102.
- Treat INC-112 as historical evidence unless the supplied data
  explicitly establishes that the same retry behavior occurred
  during INC-102.
- Evaluate INC-101 as evidence of Customer Service connection
  pool exhaustion.
- Evaluate INC-102 as evidence of Payment API timeouts and
  slow calls to Customer Service.
- Consider the Customer Service dependency when evaluating
  the Payment API timeouts.
- Do not assume that Customer Database performance degradation
  caused connection pool exhaustion.
- Do not assume that DEP-001 caused INC-101.
- Do not assume that DEP-002 caused INC-102.


OUTPUT REQUIREMENTS:

Return one valid JSON object matching the RCAReport structure.

Use these fields and types:

{{
  "primary_incident_id": "string or null",
  "incident_summary": "string",
  "root_cause_hypotheses": [
    {{
      "title": "string",
      "description": "string",
      "confidence": "LOW | MEDIUM | HIGH",
      "confidence_reason": "string",
      "supporting_evidence": [
        {{
          "evidence_id": "string",
          "description": "string"
        }}
      ],
      "contradicting_or_missing_evidence": ["string"],
      "related_services": ["string"],
      "related_databases": ["string"],
      "related_deployments": ["string"],
      "recommended_validation_steps": ["string"],
      "validation_warnings": ["string"]
    }}
  ],
  "impact_summary": "string",
  "impacted_services": ["string"],
  "directly_impacted_services": ["string"],
  "suspected_contributing_services": ["string"],
  "services_requiring_investigation": ["string"],
  "investigation_steps": ["string"],
  "overall_caveats": ["string"],
  "validation_warnings": ["string"]
}}

IMPORTANT:

- incident_summary must always be a string, never an object.
- impact_summary must always be a string.
- All array fields must always be JSON arrays.
- confidence must be exactly LOW, MEDIUM, or HIGH.
- Use null for primary_incident_id only when it is unavailable.
- Do not invent evidence IDs, entity IDs, or deployment IDs.
- Do not add fields outside the specified structure.
- Do not include Markdown fences or explanatory text.

""".strip()
