import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from src.core.llm import LLMClient

@pytest.fixture
def mock_openai_local():
    with patch("src.core.llm.AsyncOpenAI") as mock:
        client = MagicMock()
        client.chat = MagicMock()
        client.chat.completions = MagicMock()
        client.chat.completions.create = AsyncMock()
        mock.return_value = client
        yield client

@pytest.fixture
def llm_client(mock_openai_local):
    return LLMClient()

@pytest.mark.asyncio
async def test_get_response_success(llm_client, mock_openai_local):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Resposta de teste"
    mock_response.usage.total_tokens = 10
    mock_openai_local.chat.completions.create.return_value = mock_response
    
    res = await llm_client.get_response([{"role": "user", "content": "oi"}])
    assert res == "Resposta de teste"
    assert mock_openai_local.chat.completions.create.call_count == 1

@pytest.mark.asyncio
async def test_get_response_retry_on_failure(llm_client, mock_openai_local):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Sucesso no retry"
    mock_response.usage.total_tokens = 10
    
    # Falha 1 vez, depois sucesso
    mock_openai_local.chat.completions.create.side_effect = [Exception("Erro API"), mock_response]
    
    with patch("asyncio.sleep", return_value=None):
        res = await llm_client.get_response([{"role": "user", "content": "oi"}])
        assert res == "Sucesso no retry"
        assert mock_openai_local.chat.completions.create.call_count == 2

@pytest.mark.asyncio
async def test_get_response_max_retries_returns_fallback(llm_client, mock_openai_local):
    mock_openai_local.chat.completions.create.side_effect = Exception("Erro persistente")
    
    with patch("asyncio.sleep", return_value=None):
        res = await llm_client.get_response([{"role": "user", "content": "oi"}])
        assert "No momento não consigo processar" in res
        assert mock_openai_local.chat.completions.create.call_count == 3
