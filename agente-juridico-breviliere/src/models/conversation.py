from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime, UTC
from typing import Optional, List

class ChannelType(str, Enum):
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    INSTAGRAM = "instagram"

class MessageType(str, Enum):
    TEXT = "text"
    AUDIO = "audio"
    IMAGE = "image"
    DOCUMENT = "document"

class IncomingMessage(BaseModel):
    channel: ChannelType
    channel_user_id: str
    message_type: MessageType
    text: Optional[str] = None
    media_url: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    raw_payload: dict

class ConversationState(BaseModel):
    session_id: str
    channel: ChannelType
    lead_id: Optional[str] = None
    current_step: str = "init"
    triage_answers: List[dict] = []
    area_juridica: Optional[str] = None
    urgency: Optional[str] = None
    score: int = 0
    lgpd_consent: bool = False
    is_existing_client: bool = False
    handoff_requested: bool = False
    history: List[dict] = []
