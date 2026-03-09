import time
import asyncio
from openai import AsyncOpenAI
from src.config.settings import get_settings
from src.config.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)

class LLMClient:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.provider = getattr(settings, "llm_provider", "openai")

    async def get_response(self, messages: list, temperature: float = 0.7) -> str:
        """
        Gera uma resposta do LLM com retry e logging de latencia.
        """
        if self.provider != "openai":
            logger.error("provider_nao_suportado", provider=self.provider)
            return "Desculpe, estou passando por uma instabilidade técnica. Pode tentar novamente em instantes?"

        max_retries = 3
        delays = [1, 2, 4]

        for attempt in range(max_retries):
            start_time = time.perf_counter()
            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                )
                
                latency = time.perf_counter() - start_time
                tokens_used = response.usage.total_tokens
                
                logger.info(
                    "llm_request_sucesso",
                    latency=f"{latency:.2f}s",
                    tokens=tokens_used,
                    model=self.model,
                    attempt=attempt + 1
                )
                
                return response.choices[0].message.content

            except Exception as e:
                latency = time.perf_counter() - start_time
                logger.warning(
                    "llm_request_falha",
                    attempt=attempt + 1,
                    error=str(e),
                    latency=f"{latency:.2f}s"
                )
                
                if attempt < max_retries - 1:
                    await asyncio.sleep(delays[attempt])
                else:
                    logger.error("llm_request_max_retries_atingido")
                    return "No momento não consigo processar sua solicitação. Por favor, tente novamente em instantes."

        return "Houve um erro inesperado. Por favor, tente novamente."
