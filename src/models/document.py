from pydantic import BaseModel, ConfigDict
from datetime import datetime, UTC
from sqlalchemy import Column, Integer, String, DateTime
from database.connection import Base

class GeneratedDocument(Base):
    __tablename__ = "generated_documents"
    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(String, index=True)
    doc_type = Column(String)
    file_path = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

class DocumentSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    lead_id: str
    doc_type: str
    file_path: str
    created_at: datetime
