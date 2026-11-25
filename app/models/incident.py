from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class Incident(BaseModel):
    id: str
    title: str

    timestamp: datetime
    severity: str
    status: str

    affected_service_ids: list[str] = Field(
        default_factory=list
    )

    observed_error_ids: list[str] = Field(
        default_factory=list
    )

    associated_deployment_ids: list[str] = Field(
        default_factory=list
    )

    description: str

    resolution_summary: Optional[str] = None
    investigation_notes: Optional[str] = None
    source_document: Optional[str] = None