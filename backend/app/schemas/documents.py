from datetime import datetime

from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    id: int
    title: str
    document_type: str
    original_filename: str
    incident_id: int | None
    service: str | None
    chunk_count: int
    sections: list[str]
    created_at: datetime