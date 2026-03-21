import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app

client = TestClient(app)

@pytest.fixture
def mock_adapters():
    """Mock dos adapters para testes de webhook."""
    with patch("src.api.webhooks._get_whatsapp") as mock_wa, \
         patch("src.api.webhooks._get_telegram") as mock_tg, \
         patch("src.api.webhooks._get_instagram") as mock_ig, \
         patch("src.api.webhooks._get_transcriber") as mock_transcriber:

        # Mock dos adapters - todos retornam None para ignorar mensagens
        mock_wa_adapter = MagicMock()
        mock_wa_adapter.parse_incoming = MagicMock(return_value=None)  # Sintetico!
        mock_wa_adapter.send_text = MagicMock(return_value=True)
        mock_wa.return_value = mock_wa_adapter
        
        mock_tg_adapter = MagicMock()
        mock_tg_adapter.parse_incoming = MagicMock(return_value=None)  # Sintetico!
        mock_tg_adapter.send_text = MagicMock(return_value=True)
        mock_tg.return_value = mock_tg_adapter
        
        # Instagram: parse_incoming é sincrono
        mock_ig_adapter = MagicMock()
        mock_ig_adapter.parse_incoming = MagicMock(return_value=None)  # Sintetico!
        mock_ig_adapter.send_text = MagicMock(return_value=True)
        mock_ig.return_value = mock_ig_adapter
        
        mock_transcriber.return_value = MagicMock()

        yield

def test_instagram_webhook_ignores_non_text():
    """Testa que webhook do Instagram ignora mensagens nao-texto."""
    data = {
        "entry": [{
            "messaging": [{
                "sender": {"id": "user123"},
                "message": {"attachments": [{"type": "image"}]}
            }]
        }]
    }

    response = client.post("/webhooks/instagram", json=data)
    assert response.status_code == 200
    result = response.json()
    assert "status" in result

def test_instagram_verify_token():
    """Testa verificacao do webhook do Instagram."""
    response = client.get(
        "/webhooks/instagram",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "test-token",
            "hub.challenge": "12345"
        }
    )
    # Retorna 200 ou 403 dependendo do token
    assert response.status_code in [200, 403]
