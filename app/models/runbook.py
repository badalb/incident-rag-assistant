from pydantic import BaseModel
from typing import Optional


class Runbook(BaseModel):
    id: str
    title: str
    file_path: str

    content: Optional[str] = None
    description: Optional[str] = None