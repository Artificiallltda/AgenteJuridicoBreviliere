import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from core.llm import LLMClient

# Nota: Estes testes usam mocks para evitar chamadas reais a OpenAI
# Para testes de integracao real, usar API Key valida no .env

@pytest.fixture
def mock_openai_client():
    """Fixture para mock do cliente OpenAI."""
    with patch("core.llm.AsyncOpenAI") as MockOpenAI:
        mock_client = MagicMock()
        MockOpenAI.return_value = mock_client
        
        # Mock da resposta
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Resposta de teste"
        mock_response.usage = MagicMock()
        mock_response.usage.total_tokens = 100
        
        mock_client.chat = MagicMock()
        mock_client.chat.completions = MagicMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        yield mock_client

@pytest.mark.asyncio
async def test_get_response_success(mock_openai_client):
    """Testa chamada bem-sucedida ao LLM."""
    llm = LLMClient()
    messages = [{"role": "user", "content": "teste"}]
    res = await llm.get_response(messages)
    
    assert res == "Resposta de teste"
    assert mock_openai_client.chat.completions.create.called

@pytest.mark.asyncio
async def test_get_response_retry_on_failure(mock_openai_client):
    """Testa retry em caso de falha temporaria."""
    # Primeira chamada falha, segunda tem sucesso
    mock_openai_client.chat.completions.create.side_effect = [
        Exception("API Error"),
        MagicMock(choices=[MagicMock(message=MagicMock(content="Sucesso no retry"))])
    ]
    
    llm = LLMClient()
    messages = [{"role": "user", "content": "teste"}]
    res = await llm.get_response(messages)
    
    assert res == "Sucesso no retry" or res == "Resposta de teste"

@pytest.mark.asyncio
async def test_get_response_max_retries_returns_fallback(mock_openai_client):
    """Testa fallback apos maximo de retries."""
    mock_openai_client.chat.completions.create.side_effect = Exception("API Error")
    
    llm = LLMClient()
    messages = [{"role": "user", "content": "teste"}]
    res = await llm.get_response(messages)
    
    # Deve retornar mensagem de fallback apos 3 tentativas
    assert res is not None
    assert isinstance(res, str)
    assert len(res) > 0
