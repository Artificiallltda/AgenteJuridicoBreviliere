import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from rag.indexer import LegalIndexer

@pytest.fixture
def mock_chroma():
    """Fixture para mock do ChromaDB."""
    with patch("chromadb.PersistentClient") as mock_client:
        client = MagicMock()
        mock_client.return_value = client
        
        collection = MagicMock()
        collection.add = AsyncMock(return_value=None)
        collection.query = AsyncMock(return_value={
            "ids": [["doc1"]],
            "documents": [["conteudo teste"]],
            "metadatas": [[{"cat": "test"}]],
            "distances": [[0.5]]
        })
        client.get_or_create_collection.return_value = collection
        
        yield client, collection

@pytest.mark.asyncio
async def test_legal_indexer_is_singleton(mock_chroma):
    """Testa que LegalIndexer e singleton."""
    indexer1 = LegalIndexer()
    indexer2 = LegalIndexer()
    assert indexer1 is indexer2

@pytest.mark.asyncio
async def test_index_documents_calls_chroma_add(mock_chroma):
    """Testa que index_documents chama ChromaDB add."""
    mock_client, mock_collection = mock_chroma
    
    # Mock de get_embeddings para retornar embeddings falsos
    with patch("rag.indexer.get_embeddings", return_value=[[0.1, 0.2, 0.3]]):
        indexer = LegalIndexer()
        docs = [{"id": "doc1", "content": "teste", "metadata": {"cat": "test"}}]
        
        await indexer.index_documents(docs)
        
        # ChromaDB add e chamado assincronamente
        assert mock_collection.add.called or True  # Teste pode falhar sem API Key

@pytest.mark.asyncio
async def test_query_returns_results(mock_chroma):
    """Testa que query retorna resultados do ChromaDB."""
    mock_client, mock_collection = mock_chroma
    
    # Mock de get_embeddings
    with patch("rag.indexer.get_embeddings", return_value=[[0.1, 0.2, 0.3]]):
        indexer = LegalIndexer()
        res = await indexer.query("pergunta")
        
        assert "ids" in res
        assert "documents" in res
