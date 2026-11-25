from pydantic import BaseModel, Field
from typing import Optional


class Service(BaseModel):
    id: str
    name: str
    description: Optional[str] = None

    team_id: Optional[str] = None

    depends_on: list[str] = Field(default_factory=list)
    uses_databases: list[str] = Field(default_factory=list)

    produces_topics: list[str] = Field(default_factory=list)
    consumes_topics: list[str] = Field(default_factory=list)