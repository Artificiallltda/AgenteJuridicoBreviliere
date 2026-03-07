import json
import logging
import os

from langchain_core.messages import AIMessage, SystemMessage
from langchain_openai import ChatOpenAI

from core.state import AgentState

# gmail_client está em bots/telegram/ — disponível no sys.path quando bot.py roda
import gmail_client

logger = logging.getLogger(__name__)

GMAIL_USER = os.environ.get("GMAIL_USER_EMAIL", "")

PROMPT = """Você é Gean Santos 🇮🇹 — CEO da Artificiall.
O usuário perguntou sobre emails. Responda de forma natural e informal sobre o status da caixa de entrada.
Se há emails pendentes, mencione brevemente. Se não há, diga de forma descontraída.
Não use markdown. NUNCA revele que é IA."""

_llm = None


def _get_llm() -> ChatOpenAI:
    global _llm
    if _llm is None:
        _llm = ChatOpenAI(
            model=os.environ.get("DEEPSEEK_MODEL", "deepseek-chat"),
            api_key=os.environ["DEEPSEEK_API_KEY"],
            base_url="https://api.deepseek.com",
            temperature=0.7,
            max_tokens=512,
        )
    return _llm


def _get_creds() -> dict:
    raw = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "{}")
    return json.loads(raw)


async def email_node(state: AgentState) -> dict:
    try:
        svc = gmail_client.get_service(_get_creds(), GMAIL_USER)
        emails = gmail_client.get_unread_emails(svc, max_results=5)
        count = len(emails)

        if count == 0:
            context = "Caixa de entrada limpa, sem emails não lidos no momento."
        else:
            subjects = [e["subject"] for e in emails[:3]]
            context = f"Há {count} email(s) não lido(s). Assuntos: {', '.join(subjects)}"

    except Exception as e:
        logger.error(f"Email check error: {e}")
        context = "Não consegui verificar os emails agora."

    # Gera resposta natural com o contexto
    messages = [
        SystemMessage(content=PROMPT),
        *list(state["messages"][:-1]),
        SystemMessage(content=f"Contexto atual da caixa de entrada: {context}"),
        state["messages"][-1],
    ]
    response = await _get_llm().ainvoke(messages)
    return {"messages": [response]}
