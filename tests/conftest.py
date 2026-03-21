import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from config.settings import Settings
from models.conversation import ConversationState, ChannelType
from models.lead import LeadSchema, LeadStatus

@pytest.fixture
def mock_settings():
    return Settings(
        openai_api_key="fake-test-key",
        whatsapp_verify_token="test-token",
        chroma_persist_dir="./test_chroma"
    )

@pytest.fixture
def mock_chroma():
    with patch("chromadb.PersistentClient") as mock:
        client = MagicMock()
        mock.return_value = client
        yield client

@pytest.fixture
def mock_openai():
    with patch("openai.AsyncOpenAI") as mock:
        client = MagicMock()
        client.chat = MagicMock()
        client.chat.completions = MagicMock()
        client.chat.completions.create = AsyncMock()
        mock.return_value = client
        yield client

@pytest.fixture
def sample_conversation_state():
    return ConversationState(
        session_id="test-session-123",
        channel=ChannelType.WHATSAPP,
        lgpd_consent=True,
        current_step="triage"
    )

@pytest.fixture
def sample_lead():
    return LeadSchema(
        id="lead-123",
        name="Joao Silva",
        email="joao@example.com",
        phone="5511999999999",
        area_juridica="trabalhista",
        status=LeadStatus.NEW,
        score=75,
        triage_data={"pergunta1": "resposta1"},
        lgpd_consent=True
    )
