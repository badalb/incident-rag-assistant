from pydantic import BaseModel, Field


class Team(BaseModel):
    id: str
    name: str

    responsibilities: list[str] = Field(
        default_factory=list
    )