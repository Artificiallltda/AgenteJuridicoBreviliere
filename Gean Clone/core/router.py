import logging
import os

from langchain_openai import ChatOpenAI

from core.state import AgentState

logger = logging.getLogger(__name__)

_llm = None


def _get_llm() -> ChatOpenAI:
    global _llm
    if _llm is None:
        _llm = ChatOpenAI(
            model=os.environ.get("DEEPSEEK_MODEL", "deepseek-chat"),
            api_key=os.environ["DEEPSEEK_API_KEY"],
            base_url="https://api.deepseek.com",
            temperature=0,
            max_tokens=20,
        )
    return _llm


ROUTER_PROMPT = """Classifique a mensagem em UMA categoria. Responda APENAS com o nome da categoria, nada mais.

Categorias:
- gean_clone: chat geral, assuntos pessoais, gastronomia, tecnologia, redes sociais, apresentação
- sdr: vendas, parceria, proposta comercial, produto da Artificiall, interesse em contratar, cotação, demo
- admin: equipe interna, RH, contratos, pagamentos, férias, benefícios, processos administrativos
- calendar: agenda, reunião, horário, evento, compromisso, disponibilidade, calendário
- email: usuário menciona email, mensagem pendente, correspondência explicitamente

Mensagem: {message}
Categoria:"""

VALID_INTENTS = {"gean_clone", "sdr", "admin", "calendar", "email"}


async def router_node(state: AgentState) -> dict:
    last_msg = state["messages"][-1].content if state["messages"] else ""
    try:
        response = await _get_llm().ainvoke(ROUTER_PROMPT.format(message=last_msg))
        # Pega apenas a primeira palavra para evitar ruído
        intent = response.content.strip().lower().split()[0]
        intent = intent if intent in VALID_INTENTS else "gean_clone"
    except Exception as e:
        logger.error(f"Router error: {e}")
        intent = "gean_clone"

    logger.info(f"Intent classificado: {intent} | msg: {last_msg[:60]}")
    return {"intent": intent}


def route_intent(state: AgentState) -> str:
    return state.get("intent", "gean_clone")
