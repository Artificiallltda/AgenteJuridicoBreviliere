import logging

from langchain_core.messages import HumanMessage
from langgraph.graph import END, StateGraph

from core.agents.admin import admin_node
from core.agents.calendar_agent import calendar_node
from core.agents.email_agent import email_node
from core.agents.gean_clone import gean_clone_node
from core.agents.sdr import sdr_node
from core.memory import get_checkpointer
from core.router import route_intent, router_node
from core.state import AgentState

logger = logging.getLogger(__name__)

_graph = None


def _build_graph():
    workflow = StateGraph(AgentState)

    # Nós
    workflow.add_node("router", router_node)
    workflow.add_node("gean_clone", gean_clone_node)
    workflow.add_node("sdr", sdr_node)
    workflow.add_node("admin", admin_node)
    workflow.add_node("calendar", calendar_node)
    workflow.add_node("email", email_node)

    # Entrada → Router
    workflow.set_entry_point("router")

    # Router → agente correto (roteamento condicional)
    workflow.add_conditional_edges(
        "router",
        route_intent,
        {
            "gean_clone": "gean_clone",
            "sdr": "sdr",
            "admin": "admin",
            "calendar": "calendar",
            "email": "email",
        },
    )

    # Todos os agentes terminam após responder
    for node in ["gean_clone", "sdr", "admin", "calendar", "email"]:
        workflow.add_edge(node, END)

    checkpointer = get_checkpointer()
    return workflow.compile(checkpointer=checkpointer)


def get_graph():
    global _graph
    if _graph is None:
        _graph = _build_graph()
        logger.info("LangGraph compilado com sucesso")
    return _graph


async def process_message(chat_id: str, message: str, channel: str = "telegram") -> str:
    """
    Ponto de entrada principal — channel-agnostic.
    Funciona para Telegram, WhatsApp ou qualquer outro canal.
    """
    graph = get_graph()
    config = {"configurable": {"thread_id": f"{channel}_{chat_id}"}}

    input_state = {
        "messages": [HumanMessage(content=message)],
        "chat_id": chat_id,
        "channel": channel,
        "intent": None,
    }

    result = await graph.ainvoke(input_state, config)

    # Retorna o conteúdo da última mensagem de AI
    for msg in reversed(result["messages"]):
        if hasattr(msg, "content") and getattr(msg, "type", "") == "ai":
            return msg.content

    return "Perae que já vejo isso 🤨"
