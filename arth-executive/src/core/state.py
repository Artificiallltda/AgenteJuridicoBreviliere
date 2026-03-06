from typing import TypedDict, Annotated, List
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    """
    O estado global do Arth.
    messages: Lista de mensagens (Human, AI, Tool) trocadas na sess\'E3o.
    user_id: Identificador do usu\'E1rio no WhatsApp/Telegram.
    channel: Canal de origem.
    """
    messages: Annotated[list[BaseMessage], add_messages]
    user_id: str
    channel: str
