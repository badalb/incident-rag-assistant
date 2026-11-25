from pydantic import BaseModel
from typing import Optional


class Error(BaseModel):
    id: str
    name: str
    error_type: str

    signature: Optional[str] = None
    description: Optional[str] = None