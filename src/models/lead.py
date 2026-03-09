from pydantic import BaseModel, ConfigDict, Field
from enum import Enum
from datetime import datetime, UTC
from typing import Optional
from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON
from src.database.connection import Base

class LeadStatus(str, Enum):
    NEW = "new"
    QUALIFIED = "qualified"
    CONVERTED = "converted"
    LOST = "lost"

class Lead(Base):
    __tablename__ = "leads"
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, index=True)
    phone = Column(String, index=True)
    area_juridica = Column(String)
    status = Column(String, default=LeadStatus.NEW)
    score = Column(Integer, default=0)
    triage_data = Column(JSON)
    lgpd_consent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

class LeadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    email: Optional[str] = None
    phone: str
    area_juridica: Optional[str] = None
    status: LeadStatus = LeadStatus.NEW
    score: int = 0
    triage_data: dict = {}
    lgpd_consent: bool = False
