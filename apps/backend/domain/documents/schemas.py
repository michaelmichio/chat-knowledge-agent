from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class DocumentBase(BaseModel):
    filename: str
    filetype: str


class DocumentOut(DocumentBase):
    id: UUID
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
