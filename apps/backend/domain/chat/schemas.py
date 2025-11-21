from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

class ChatSessionOut(BaseModel):
    id: uuid.UUID
    title: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ChatMessageOut(BaseModel):
    id: uuid.UUID
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True
