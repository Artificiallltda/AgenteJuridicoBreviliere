from typing import List
from openai import AsyncOpenAI
from src.config.settings import get_settings
from src.config.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)

# Cliente instanciado via função para garantir que o .env esteja carregado
def get_openai_client():
    return AsyncOpenAI(api_key=settings.openai_api_key)

async def get_embeddings(texts: List[str]) -> List[List[float]]:
    """Gera embeddings para uma lista de textos usando OpenAI."""
    try:
        client = get_openai_client()
        response = await client.embeddings.create(
            input=texts,
            model=settings.embedding_model
        )
        return [data.embedding for data in response.data]
    except Exception as e:
        logger.error("erro_geracao_embeddings", error=str(e))
        raise
