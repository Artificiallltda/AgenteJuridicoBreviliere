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

def test_instagram_verify_webhook():
    # Meta envia os mesmos parametros que o WhatsApp
    params = {
        "hub.mode": "subscribe",
        "hub.verify_token": "test-token", # Assume que mock_settings retorna isso
        "hub.challenge": "12345"
    }
    
    with patch("src.api.webhooks.settings.whatsapp_verify_token", "test-token"):
        response = client.get("/webhooks/instagram", params=params)
        assert response.status_code == 200
        assert response.text == "12345"

@pytest.mark.asyncio
async def test_instagram_webhook_receives_message():
    mock_incoming = IncomingMessage(
        channel=ChannelType.INSTAGRAM,
        channel_user_id="insta_user_1",
        message_type=MessageType.TEXT,
        text="Olá Orion",
        raw_payload={}
    )
    
    with patch("src.api.webhooks._get_instagram") as mock_get:
        adapter = mock_get.return_value
        adapter.parse_incoming = AsyncMock(return_value=mock_incoming)
        adapter.send_text = AsyncMock()
        
        with patch("src.api.webhooks.process_message", return_value="Resposta IG") as mock_proc:
            response = client.post("/webhooks/instagram", json={"object": "instagram", "entry": []})
            
            assert response.status_code == 200
            assert response.json() == {"status": "ok"}
            assert mock_proc.called
            assert adapter.send_text.called

@pytest.mark.asyncio
async def test_instagram_webhook_ignores_non_text():
    with patch("src.api.webhooks._get_instagram") as mock_get:
        adapter = mock_get.return_value
        adapter.parse_incoming = AsyncMock(return_value=IncomingMessage(
            channel=ChannelType.INSTAGRAM,
            channel_user_id="u1",
            message_type=MessageType.IMAGE,
            text=None,
            raw_payload={}
        ))
        
        response = client.post("/webhooks/instagram", json={})
        assert response.json() == {"status": "ignored"}

def test_instagram_session_created_with_correct_channel():
    mock_incoming = IncomingMessage(
        channel=ChannelType.INSTAGRAM,
        channel_user_id="insta_789",
        message_type=MessageType.TEXT,
        text="Oi",
        raw_payload={}
    )
    
    with patch("src.api.webhooks._get_instagram") as mock_get, \
         patch("src.api.webhooks.process_message", return_value="..."), \
         patch("src.api.webhooks.WhatsAppAdapter.send_text", new_callable=AsyncMock):
        
        adapter = mock_get.return_value
        adapter.parse_incoming = AsyncMock(return_value=mock_incoming)
        adapter.send_text = AsyncMock()
        
        client.post("/webhooks/instagram", json={})
        
        assert "insta_789" in _sessions
        assert _sessions["insta_789"].channel == ChannelType.INSTAGRAM
