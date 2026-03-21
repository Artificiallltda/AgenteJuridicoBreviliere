import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from notifications.proactive import ProactiveNotifier
from models.conversation import ConversationState, ChannelType

@pytest.fixture
def mock_adapters():
    wa = MagicMock()
    wa.send_text = AsyncMock(return_value=True)
    return {"whatsapp": wa}

@pytest.fixture
def notifier(mock_adapters):
    return ProactiveNotifier(mock_adapters)

@pytest.mark.asyncio
async def test_send_followup_success(notifier, mock_adapters):
    success = await notifier.send_followup("user123", "whatsapp", "Ola")
    assert success is True
    assert mock_adapters["whatsapp"].send_text.called

@pytest.mark.asyncio
async def test_send_followup_wrong_channel(notifier):
    success = await notifier.send_followup("user123", "canal_fake", "Ola")
    assert success is False

@pytest.mark.asyncio
async def test_check_abandoned_finds_triage(notifier):
    sessions = {
        "s1": ConversationState(
            session_id="s1", 
            channel=ChannelType.WHATSAPP, 
            current_step="triage", 
            history=[{"r": "u", "c": "1"}, {"r": "a", "c": "2"}, {"r": "u", "c": "3"}]
        ),
        "s2": ConversationState(
            session_id="s2", 
            channel=ChannelType.WHATSAPP, 
            current_step="closed", 
            history=[{"r": "u", "c": "1"}]
        )
    }
    abandoned = await notifier.check_abandoned_sessions(sessions)
    assert "s1" in abandoned
    assert "s2" not in abandoned

def test_get_followup_message_by_step(notifier):
    msg_triage = notifier.get_followup_message("triage")
    assert "pendentes" in msg_triage or "iniciou" in msg_triage

    msg_init = notifier.get_followup_message("init")
    assert "ajudar" in msg_init or "continuar" in msg_init

    msg_unknown = notifier.get_followup_message("unknown")
    assert "ajudar" in msg_unknown or "continuar" in msg_unknown

@pytest.mark.asyncio
async def test_followup_all_sends_to_abandoned(notifier, mock_adapters):
    sessions = {
        "s1": ConversationState(
            session_id="s1", 
            channel=ChannelType.WHATSAPP, 
            current_step="triage", 
            history=[{"r": "u", "c": "1"}, {"r": "a", "c": "2"}, {"r": "u", "c": "3"}]
        )
    }
    with patch.object(notifier, "send_followup", AsyncMock(return_value=True)) as mock_send:
        # Simulando o que a API faria
        ids = await notifier.check_abandoned_sessions(sessions)
        for sid in ids:
            await notifier.send_followup(sid, "whatsapp", "oi")
        
        assert mock_send.call_count == 1
