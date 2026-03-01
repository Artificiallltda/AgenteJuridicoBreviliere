import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.rag.indexer import LegalIndexer

@pytest.fixture
def indexer_instance(mock_chroma):
    with patch("src.rag.indexer.get_embeddings", return_value=AsyncMock()):
        # Reinicia o singleton para o teste
        LegalIndexer._instance = None
        return LegalIndexer()

def test_legal_indexer_is_singleton(mock_chroma):
    LegalIndexer._instance = None
    idx1 = LegalIndexer()
    idx2 = LegalIndexer()
    assert idx1 is idx2

@pytest.mark.asyncio
async def test_index_documents_calls_chroma_add(indexer_instance):
    with patch("src.rag.indexer.get_embeddings", return_value=AsyncMock(return_value=[[0.1]*1536])):
        docs = [{"id": "doc1", "content": "texto", "metadata": {"source": "test"}}]
        await indexer_instance.index_documents(docs)
        assert indexer_instance.collection.add.called

@pytest.mark.asyncio
async def test_query_returns_results(indexer_instance):
    with patch("src.rag.indexer.get_embeddings", return_value=AsyncMock(return_value=[[0.1]*1536])):
        indexer_instance.collection.query.return_value = {"documents": [["resultado"]]}
        res = await indexer_instance.query("pergunta")
        assert "resultado" in res["documents"][0]
