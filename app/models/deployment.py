from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class Deployment(BaseModel):
    id: str
    service_id: str
    version: str

    timestamp: datetime

    environment: str
    status: str

    change_summary: Optional[str] = None
    change_ticket: Optional[str] = None