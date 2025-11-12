from sqlalchemy import Column, String, DateTime, func, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid
from infra.db.base import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String, nullable=False)
    filetype = Column(String, nullable=False)
    status = Column(String, default="uploaded")
    extracted_text = Column(Text, nullable=True)   # ⬅️ teks hasil ekstraksi
    created_at = Column(DateTime(timezone=True), server_default=func.now())
