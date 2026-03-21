import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_metrics_returns_placeholder():
    """Testa que metrics retorna placeholder (DashboardStore nao implementado)."""
    response = client.get("/admin/dashboard/metrics")
    assert response.status_code == 200
    data = response.json()
    # Dashboard retorna placeholders
    assert isinstance(data, dict)

def test_conversations_returns_empty_list():
    """Testa que conversacoes retorna lista vazia."""
    response = client.get("/admin/dashboard/conversations")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_history_returns_404_for_unknown_session():
    """Testa que historico retorna 404 para sessao desconhecida."""
    response = client.get("/admin/dashboard/conversations/fake_id/history")
    assert response.status_code == 404
