from pydantic import BaseModel
from typing import Optional


class Database(BaseModel):
    id: str
    name: str
    database_type: str

    owner_team_id: Optional[str] = None
    description: Optional[str] = None