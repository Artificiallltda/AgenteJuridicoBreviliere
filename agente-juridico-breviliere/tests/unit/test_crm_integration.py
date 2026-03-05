import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.handoff.manager import HandoffManager
from src.integrations.pipedrive import create_deal
from src.models.conversation import ConversationState, ChannelType

@pytest.fixture
def manager():
    return HandoffManager()

@pytest.fixture
def state():
    return ConversationState(
        session_id="user_123",
        channel=ChannelType.WHATSAPP,
        area_juridica="trabalhista",
        score=85,
        triage_answers=[
            {"id": "nome", "pergunta": "Nome?", "resposta": "Maria Silva"},
            {"id": "motivo", "pergunta": "Motivo?", "resposta": "Fui demitida"}
        ],
        lgpd_consent=True
    )

@pytest.mark.asyncio
async def test_create_crm_lead_success(manager, state):
    with patch("src.integrations.crm.CRMIntegration.create_lead", return_value="person_999"), \
         patch("src.integrations.pipedrive.create_deal", return_value="deal_888"), \
         patch("src.integrations.pipedrive.add_note", return_value=True):
        
        crm_id = await manager.create_crm_lead(state)
        assert crm_id == "person_999"

@pytest.mark.asyncio
async def test_create_crm_lead_error_returns_none(manager, state):
    with patch("src.integrations.crm.CRMIntegration.create_lead", return_value=None):
        crm_id = await manager.create_crm_lead(state)
        assert crm_id is None

@pytest.mark.asyncio
async def test_handoff_includes_crm_id_in_slack(manager, state):
    with patch.object(manager, "create_crm_lead", return_value="deal_123"), \
         patch("src.handoff.manager.send_slack_notification", return_value=True) as mock_slack:
        
        await manager.request_handoff(state, "Briefing teste")
        
        args, _ = mock_slack.call_args
        assert "CRM ID: deal_123" in args[0]

@pytest.mark.asyncio
async def test_handoff_continues_without_crm(manager, state):
    with patch.object(manager, "create_crm_lead", return_value=None), \
         patch("src.handoff.manager.send_slack_notification", return_value=True) as mock_slack:
        
        await manager.request_handoff(state, "Briefing teste")
        
        args, _ = mock_slack.call_args
        assert "CRM: nao foi possivel criar lead" in args[0]
        assert mock_slack.called

@pytest.mark.asyncio
async def test_create_deal(manager):
    mock_crm = MagicMock()
    mock_crm.base_url = "https://api.pipedrive.com/v1"
    mock_crm.api_token = "token_123"
    
    mock_resp = MagicMock()
    mock_resp.status_code = 201
    mock_resp.json.return_value = {"data": {"id": 555}}
    
    with patch("httpx.AsyncClient.post", return_value=mock_resp):
        deal_id = await create_deal(mock_crm, "person_1", "Teste Deal")
        assert deal_id == "555"
