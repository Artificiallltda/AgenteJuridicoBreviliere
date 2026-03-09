import pytest
from pydantic import ValidationError
from src.models.conversation import ConversationState, ChannelType, IncomingMessage, MessageType
from src.models.lead import LeadSchema, LeadStatus

def test_conversation_state_defaults():
    state = ConversationState(session_id="123", channel=ChannelType.WHATSAPP)
    assert state.current_step == "init"
    assert state.lgpd_consent is False
    assert state.triage_answers == []

def test_incoming_message_validates_channel_enum():
    with pytest.raises(ValidationError):
        IncomingMessage(
            channel="invalido",
            channel_user_id="123",
            message_type=MessageType.TEXT,
            raw_payload={}
        )

def test_lead_schema_serialization(sample_lead):
    # Teste de dict() / model_dump()
    data = sample_lead.model_dump()
    assert data["id"] == "lead-123"
    assert data["status"] == "new"
    
    # Teste de criacao a partir de dict
    lead2 = LeadSchema(**data)
    assert lead2.id == sample_lead.id
    assert lead2.status == sample_lead.status
