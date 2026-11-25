
from pydantic import BaseModel, Field


class InvestigationRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=5,
        max_length=1000,
        description="Natural-language incident investigation question"
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of vector search results"
    )

    max_hops: int = Field(
        default=3,
        ge=1,
        le=5,
        description="Maximum graph traversal depth"
    )
