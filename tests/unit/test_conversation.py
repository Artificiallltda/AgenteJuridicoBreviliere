import pytest
from unittest.mock import AsyncMock, patch
from core.conversation import process_message
from models.conversation import ConversationState, ChannelType

@pytest.mark.asyncio
async def test_process_message_consent_flow():
    state = ConversationState(session_id="123", channel=ChannelType.WHATSAPP, lgpd_consent=False)
    
    # 1. Deve pedir consentimento
    res1 = await process_message(state, "oi")
    assert "LGPD" in res1
    assert state.lgpd_consent is False
    
    # 2. Deve aceitar consentimento
    res2 = await process_message(state, "sim")
    assert state.lgpd_consent is True
    assert state.current_step == "triage"

@pytest.mark.asyncio
async def test_process_message_triage_flow():
    """Testa fluxo de triagem."""
    state = ConversationState(session_id="123", channel=ChannelType.WHATSAPP, lgpd_consent=True, current_step="triage")

    with patch("src.core.conversation.TriageFlow.get_next_question", return_value="Qual seu nome?"), \
         patch("src.core.conversation.llm.get_response", return_value="Por favor, me diga seu nome"):

        res = await process_message(state, "quero ajuda")
        # Deve retornar resposta ou iniciar triagem
        assert isinstance(res, str)
        assert len(res) > 0

@pytest.mark.asyncio
async def test_process_message_closed_returns_message():
    state = ConversationState(session_id="123", channel=ChannelType.WHATSAPP, lgpd_consent=True, current_step="closed")
    res = await process_message(state, "oi")
    assert "encaminhado" in res or "advogado" in res
