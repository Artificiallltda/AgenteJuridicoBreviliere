import json
import logging
import os
from datetime import datetime, timedelta

import pytz
from langchain_core.messages import AIMessage

from core.state import AgentState

# calendar_client está em bots/telegram/ — disponível no sys.path quando bot.py roda
import calendar_client

logger = logging.getLogger(__name__)

TIMEZONE = os.environ.get("TIMEZONE", "America/Sao_Paulo")
GMAIL_USER = os.environ.get("GMAIL_USER_EMAIL", "")


def _get_creds() -> dict:
    raw = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "{}")
    return json.loads(raw)


async def calendar_node(state: AgentState) -> dict:
    last_msg = state["messages"][-1].content.lower() if state["messages"] else ""

    try:
        svc = calendar_client.get_service(_get_creds(), GMAIL_USER)
        tz = pytz.timezone(TIMEZONE)
        today = datetime.now(tz).date()

        if any(w in last_msg for w in ["amanhã", "amanha"]):
            events = calendar_client.get_events(svc, today + timedelta(days=1))
            text = calendar_client.format_events(events, "amanhã")
        elif "semana" in last_msg:
            events = calendar_client.get_events(svc, today, days=7)
            text = calendar_client.format_events(events, "essa semana")
        else:
            events = calendar_client.get_events(svc, today)
            text = calendar_client.format_events(events, "hoje")

    except Exception as e:
        logger.error(f"Calendar error: {e}")
        text = "Perae que já vejo a agenda, deu um problema aqui 🤨"

    return {"messages": [AIMessage(content=text)]}
