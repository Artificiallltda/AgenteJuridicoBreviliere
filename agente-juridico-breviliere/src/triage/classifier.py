from openai import AsyncOpenAI
from src.config.settings import get_settings
from src.config.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


async def classify_legal_area(case_description: str) -> str:
    """Classifica a area juridica com base na descricao do caso.

    Usa LLM para analisar o texto e retornar a area mais provavel.
    Areas possiveis: trabalhista, civil, familia, criminal, previdenciario, tributario, geral.
    """
    prompt = (
        "Classifique a seguinte situacao juridica em UMA das areas: "
        "trabalhista, civil, familia, criminal, previdenciario, tributario.\n"
        "Responda apenas o nome da area.\n\n"
        f"Caso: {case_description}"
    )

    try:
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        response = await client.chat.completions.create(
            model=settings.openai_model_light,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        area = response.choices[0].message.content.strip().lower()
        logger.info("area_juridica_classificada", area=area)
        return area
    except Exception as e:
        logger.error("erro_classificacao_area", error=str(e))
        return "geral"
