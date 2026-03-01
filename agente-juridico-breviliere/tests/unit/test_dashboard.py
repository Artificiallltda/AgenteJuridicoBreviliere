import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.api.webhooks import _sessions
from src.models.conversation import ConversationState, ChannelType

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_test_sessions():
    _sessions.clear()
    # Sessao 1: WhatsApp, Ativa, Trabalhista, Score 80
    _sessions["user_wa"] = ConversationState(
        session_id="user_wa",
        channel=ChannelType.WHATSAPP,
        current_step="triage",
        area_juridica="trabalhista",
        score=80,
        history=[{"role": "user", "content": "oi"}]
    )
    # Sessao 2: Telegram, Fechada, Civil, Score 60
    _sessions["user_tg"] = ConversationState(
        session_id="user_tg",
        channel=ChannelType.TELEGRAM,
        current_step="closed",
        area_juridica="civil",
        score=60,
        history=[{"role": "user", "content": "ola"}, {"role": "assistant", "content": "tchau"}]
    )

def test_metrics_returns_correct_counts():
    response = client.get("/admin/dashboard/metrics")
    assert response.status_code == 200
    data = response.json()
    assert data["total_conversations"] == 2
    assert data["active_conversations"] == 1
    assert data["completed_conversations"] == 1
    assert data["average_score"] == 70.0
    assert data["conversations_by_channel"]["whatsapp"] == 1
    assert data["conversations_by_channel"]["telegram"] == 1

def test_conversations_filter_by_channel():
    response = client.get("/admin/dashboard/conversations", params={"channel": "whatsapp"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["session_id"] == "user_wa"

def test_conversation_detail_returns_history():
    response = client.get("/admin/dashboard/conversations/user_wa")
    assert response.status_code == 200
    assert response.json()["session_id"] == "user_wa"
    assert len(response.json()["history"]) == 1

def test_conversation_not_found_returns_404():
    response = client.get("/admin/dashboard/conversations/fake_id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Conversa nao encontrada"
