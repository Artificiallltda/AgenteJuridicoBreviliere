import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from src.main import app
from src.api.webhooks import _sessions
from src.models.conversation import ChannelType, IncomingMessage, MessageType

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_sessions():
    _sessions.clear()

@pytest.mark.asyncio
async def test_telegram_webhook_receives_message():
    # Mock do TelegramAdapter.parse_incoming
    mock_incoming = IncomingMessage(
        channel=ChannelType.TELEGRAM,
        channel_user_id="user123",
        message_type=MessageType.TEXT,
        text="Ola Orion",
        raw_payload={}
    )
    
    with patch("src.api.webhooks._get_telegram") as mock_get:
        adapter = mock_get.return_value
        adapter.parse_incoming.return_value = mock_incoming
        adapter.send_text = AsyncMock()
        
        with patch("src.api.webhooks.process_message", return_value="Resposta teste") as mock_proc:
            response = client.post("/webhooks/telegram", json={"message": {"text": "Ola Orion"}})
            
            assert response.status_code == 200
            assert response.json() == {"status": "ok"}
            assert mock_proc.called
            assert adapter.send_text.called

@pytest.mark.asyncio
async def test_telegram_webhook_ignores_non_text():
    with patch("src.api.webhooks._get_telegram") as mock_get:
        adapter = mock_get.return_value
        # Simula parse de algo sem texto
        adapter.parse_incoming.return_value = IncomingMessage(
            channel=ChannelType.TELEGRAM,
            channel_user_id="user123",
            message_type=MessageType.IMAGE,
            text=None,
            raw_payload={}
        )
        
        response = client.post("/webhooks/telegram", json={"message": {"image": "..."}})
        assert response.json() == {"status": "ignored"}

def test_telegram_session_is_created():
    mock_incoming = IncomingMessage(
        channel=ChannelType.TELEGRAM,
        channel_user_id="new_user_456",
        message_type=MessageType.TEXT,
        text="Novo usuario",
        raw_payload={}
    )
    
    with patch("src.api.webhooks._get_telegram") as mock_get, 
         patch("src.api.webhooks.process_message", return_value="..."), 
         patch("src.api.webhooks.WhatsAppAdapter.send_text", new_callable=AsyncMock):
        
        adapter = mock_get.return_value
        adapter.parse_incoming.return_value = mock_incoming
        adapter.send_text = AsyncMock()
        
        client.post("/webhooks/telegram", json={})
        
        assert "new_user_456" in _sessions
        assert _sessions["new_user_456"].channel == ChannelType.TELEGRAM
