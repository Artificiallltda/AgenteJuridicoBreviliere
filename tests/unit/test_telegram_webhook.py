import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from main import app

client = TestClient(app)

@pytest.fixture
def mock_adapters():
    """Mock dos adapters para testes de webhook."""
    with patch("src.api.webhooks._get_whatsapp") as mock_wa, \
         patch("src.api.webhooks._get_telegram") as mock_tg, \
         patch("src.api.webhooks._get_instagram") as mock_ig, \
         patch("src.api.webhooks._get_transcriber") as mock_transcriber:
        
        # Mock dos adapters
        mock_wa_adapter = MagicMock()
        mock_wa_adapter.parse_incoming = AsyncMock(return_value=None)
        mock_wa.return_value = mock_wa_adapter
        
        mock_tg_adapter = MagicMock()
        mock_tg_adapter.parse_incoming = AsyncMock(return_value=None)
        mock_tg.return_value = mock_tg_adapter
        
        mock_ig_adapter = MagicMock()
        mock_ig_adapter.parse_incoming = MagicMock(return_value=None)
        mock_ig.return_value = mock_ig_adapter
        
        mock_transcriber.return_value = MagicMock()
        
        yield {
            "whatsapp": mock_wa,
            "telegram": mock_tg,
            "instagram": mock_ig
        }

def test_telegram_webhook_ignores_non_text(mock_adapters):
    """Testa que webhook do Telegram ignora mensagens nao-texto."""
    data = {
        "message": {
            "chat": {"id": 123},
            "photo": [{"file_id": "abc123"}]
        }
    }
    
    response = client.post("/webhooks/telegram", json=data)
    assert response.status_code == 200
    assert response.json()["status"] == "ignored"

def test_telegram_health_check(mock_adapters):
    """Testa health check do Telegram."""
    response = client.get("/webhooks/telegram/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["channel"] == "telegram"
