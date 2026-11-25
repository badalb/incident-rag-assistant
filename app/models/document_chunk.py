
from pydantic import BaseModel, Field
from typing import Optional


class DocumentChunk(BaseModel):
    id: str
    document_id: str
    document_title: str
    document_type: str
    chunk_index: int
    content: str
    embedding: Optional[list[float]] = None
    source_file: Optional[str] = None
    mentioned_entity_ids: list[str] = Field(default_factory=list)
