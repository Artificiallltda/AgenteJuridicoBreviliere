from typing import Annotated, Literal, Optional

from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    chat_id: str
    channel: Literal["telegram", "whatsapp"]
    intent: Optional[str]
