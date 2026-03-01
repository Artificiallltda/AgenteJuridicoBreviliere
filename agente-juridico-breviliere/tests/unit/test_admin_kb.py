import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

@pytest.fixture
def mock_indexer():
    with patch("src.api.admin.indexer") as mock:
        mock.collection = MagicMock()
        yield mock

def test_list_documents(mock_indexer):
    mock_indexer.collection.get.return_value = {
        "ids": ["doc1"],
        "documents": ["conteudo"],
        "metadatas": [{"title": "T1", "category": "faq"}]
    }
    
    response = client.get("/admin/kb/documents")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == "doc1"

@pytest.mark.asyncio
async def test_create_document(mock_indexer):
    mock_indexer.index_documents = AsyncMock()
    
    payload = {
        "title": "Novo Doc",
        "content": "Conteudo do doc",
        "category": "institucional"
    }
    
    response = client.post("/admin/kb/documents", json=payload)
    assert response.status_code == 200
    assert response.json()["title"] == "Novo Doc"
    assert mock_indexer.index_documents.called

def test_delete_document(mock_indexer):
    response = client.delete("/admin/kb/documents/doc123")
    assert response.status_code == 200
    assert response.json()["status"] == "deleted"
    assert mock_indexer.collection.delete.called

@pytest.mark.asyncio
async def test_search_documents(mock_indexer):
    mock_indexer.query = AsyncMock(return_value={
        "ids": [["doc_s1"]],
        "documents": [["resultado busca"]],
        "metadatas": [[{"title": "Busca", "category": "situacoes"}]]
    })
    
    payload = {"query": "como funciona", "n_results": 2}
    response = client.post("/admin/kb/search", json=payload)
    
    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["documents"][0]["id"] == "doc_s1"

def test_get_stats(mock_indexer):
    mock_indexer.collection.get.return_value = {
        "metadatas": [
            {"category": "faq"},
            {"category": "faq"},
            {"category": "modelos"}
        ]
    }
    
    response = client.get("/admin/kb/stats")
    assert response.status_code == 200
    assert response.json()["total_documents"] == 3
    assert response.json()["count_by_category"]["faq"] == 2
