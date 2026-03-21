from pydantic import BaseModel
from typing import Optional, List, Dict

class DashboardMetrics(BaseModel):
    total_conversations: int
    active_conversations: int
    completed_conversations: int
    conversations_by_channel: Dict[str, int]
    conversations_by_area: Dict[str, int]
    average_score: float
    conversations_by_step: Dict[str, int]

class ConversationSummary(BaseModel):
    session_id: str
    channel: str
    area_juridica: Optional[str]
    score: int
    current_step: str
    messages_count: int
    lgpd_consent: bool
    created_at: Optional[str]
