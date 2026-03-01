import httpx
from src.channels.base import ChannelAdapter
from src.models.conversation import IncomingMessage, ChannelType, MessageType
from src.config.settings import get_settings
from src.config.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


class WhatsAppAdapter(ChannelAdapter):
    def __init__(self):
        self.base_url = f"https://graph.facebook.com/v18.0/{settings.whatsapp_phone_number_id}/messages"
        self.headers = {"Authorization": f"Bearer {settings.whatsapp_api_token}"}

    async def send_text(self, recipient_id: str, text: str) -> bool:
        """Envia mensagem de texto via WhatsApp."""
        payload = {
            "messaging_product": "whatsapp",
            "to": recipient_id,
            "type": "text",
            "text": {"body": text}
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(self.base_url, json=payload, headers=self.headers)
            return response.status_code == 200

    async def send_document(self, recipient_id: str, file_url: str, caption: str) -> bool:
        """Envia documento (PDF/DOCX) via WhatsApp."""
        payload = {
            "messaging_product": "whatsapp",
            "to": recipient_id,
            "type": "document",
            "document": {"link": file_url, "caption": caption}
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(self.base_url, json=payload, headers=self.headers)
            return response.status_code == 200

    async def parse_incoming(self, payload: dict) -> IncomingMessage:
        """Converte payload do webhook Meta Cloud API em IncomingMessage."""
        entry = payload.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [{}])

        if not messages:
            return None

        message = messages[0]
        msg_type = message.get("type", "text")

        return IncomingMessage(
            channel=ChannelType.WHATSAPP,
            channel_user_id=message.get("from", ""),
            message_type=MessageType(msg_type) if msg_type in MessageType.__members__.values() else MessageType.TEXT,
            text=message.get("text", {}).get("body") if msg_type == "text" else None,
            media_url=message.get(msg_type, {}).get("id") if msg_type in ("audio", "image", "document") else None,
            raw_payload=payload
        )
