from pydantic import BaseModel
from typing import Optional


class KafkaTopic(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    owner_team_id: Optional[str] = None