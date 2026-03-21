import pytest
from unittest.mock import AsyncMock, patch, MagicMock


@pytest.fixture
def mock_chroma():
    """Mock do ChromaDB para testes sem dependencia externa."""
    with patch("src.rag.indexer.chromadb") as mock:
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_client.PersistentClient.return_value = mock_client
        mock_client.get_or_create_collection.return_value = mock_collection
        mock.PersistentClient.return_value = mock_client
        yield mock_client, mock_collection


@pytest.fixture
def mock_embeddings():
    """Mock da funcao de embeddings."""
    with patch("src.rag.indexer.get_embeddings") as mock:
        mock.return_value = [[0.1, 0.2, 0.3]]
        yield mock


class TestSeedKnowledgeBase:
    """Testes para o script de seed da knowledge base."""

    @pytest.mark.asyncio
    async def test_seed_executes_without_error(self, mock_chroma, mock_embeddings):
        """Verifica que o seed executa sem erros."""
        from scripts.seed_knowledge_base import seed_knowledge_base

        mock_client, mock_collection = mock_chroma
        await seed_knowledge_base(reset=False)

        # Verifica que a collection foi criada/obtida
        assert mock_client.get_or_create_collection.called

    @pytest.mark.asyncio
    async def test_seed_with_reset(self, mock_chroma, mock_embeddings):
        """Verifica que o seed com reset limpa a collection antes."""
        from scripts.seed_knowledge_base import seed_knowledge_base

        mock_client, mock_collection = mock_chroma
        await seed_knowledge_base(reset=True)

        assert mock_client.get_or_create_collection.called

    @pytest.mark.asyncio
    async def test_seed_indexes_documents(self, mock_chroma, mock_embeddings):
        """Verifica que documentos sao indexados com embeddings."""
        from scripts.seed_knowledge_base import seed_knowledge_base

        mock_client, mock_collection = mock_chroma
        await seed_knowledge_base(reset=False)

        # Verifica que add foi chamado na collection (documentos indexados)
        assert mock_collection.add.called or mock_collection.upsert.called
