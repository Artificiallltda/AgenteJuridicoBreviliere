from pydantic import BaseModel, ConfigDict
from datetime import datetime, UTC
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, JSON
from database.connection import Base

class JudicialProcess(Base):
    __tablename__ = "judicial_processes"
    id = Column(Integer, primary_key=True, index=True)
    process_number = Column(String, unique=True, index=True)
    client_id = Column(String, index=True)
    court = Column(String)
    status = Column(String)
    last_movement = Column(String)
    last_update = Column(DateTime, default=lambda: datetime.now(UTC))
    metadata_json = Column(JSON)

class ProcessSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    process_number: str
    client_id: str
    court: str
    status: str
    last_movement: str
    last_update: datetime
