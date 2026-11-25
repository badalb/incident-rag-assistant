
import json
from typing import Literal

from pydantic import BaseModel, Field, field_validator


ConfidenceLevel = Literal["LOW", "MEDIUM", "HIGH"]


def normalize_string_list(value):
    if value is None:
        return []

    if isinstance(value, str):
        return [value] if value.strip() else []

    if isinstance(value, list):
        return [
            item if isinstance(item, str) else str(item)
            for item in value
        ]

    return [str(value)]


class EvidenceReference(BaseModel):
    evidence_id: str
    description: str


class RootCauseHypothesis(BaseModel):
    title: str
    description: str

    confidence: ConfidenceLevel
    confidence_reason: str

    supporting_evidence: list[EvidenceReference] = Field(
        default_factory=list
    )

    contradicting_or_missing_evidence: list[str] = Field(
        default_factory=list
    )

    related_services: list[str] = Field(default_factory=list)
    related_databases: list[str] = Field(default_factory=list)
    related_deployments: list[str] = Field(default_factory=list)

    recommended_validation_steps: list[str] = Field(
        default_factory=list
    )

    validation_warnings: list[str] = Field(default_factory=list)

    
    @field_validator(
        "contradicting_or_missing_evidence",
        "related_services",
        "related_databases",
        "related_deployments",
        "recommended_validation_steps",
        "validation_warnings",
        mode="before"
    )
    @classmethod
    def normalize_list_fields(cls, value):
        return normalize_string_list(value)


class RCAReport(BaseModel):
    primary_incident_id: str | None = None
    incident_summary: str

    root_cause_hypotheses: list[RootCauseHypothesis] = Field(
        default_factory=list
    )

    impact_summary: str

    # Retained for compatibility with earlier reports.
    impacted_services: list[str] = Field(default_factory=list)

    directly_impacted_services: list[str] = Field(default_factory=list)
    suspected_contributing_services: list[str] = Field(default_factory=list)
    services_requiring_investigation: list[str] = Field(default_factory=list)

    investigation_steps: list[str] = Field(default_factory=list)
    overall_caveats: list[str] = Field(default_factory=list)
    validation_warnings: list[str] = Field(default_factory=list)

    @field_validator("incident_summary", mode="before")
    @classmethod
    def normalize_incident_summary(cls, value):
        if isinstance(value, dict):
            title = value.get("title")
            description = value.get("description")

            if title and description:
                return f"{title}: {description}"

            if title:
                return str(title)

            if description:
                return str(description)

            return json.dumps(value, default=str)

        return value

    @field_validator(
        "impacted_services",
        "directly_impacted_services",
        "suspected_contributing_services",
        "services_requiring_investigation",
        "investigation_steps",
        "overall_caveats",
        "validation_warnings",
        mode="before"
    )
    @classmethod
    def normalize_report_lists(cls, value):
        return normalize_string_list(value)
