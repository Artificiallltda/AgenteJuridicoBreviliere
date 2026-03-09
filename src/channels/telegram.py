import httpx
from src.channels.base import ChannelAdapter
from src.models.conversation import IncomingMessage, ChannelType, MessageType
from src.config.settings import get_settings
from src.config.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


class TelegramAdapter(ChannelAdapter):
    def __init__(self):
        self.base_url = f"https://api.telegram.org/bot{settings.telegram_bot_token}"

    async def send_text(self, recipient_id: str, text: str) -> bool:
        """Envia mensagem de texto via Telegram Bot API."""
        url = f"{self.base_url}/sendMessage"
        payload = {"chat_id": recipient_id, "text": text, "parse_mode": "Markdown"}
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            return response.status_code == 200

    async def send_document(self, recipient_id: str, file_url: str, caption: str) -> bool:
        """Envia documento via Telegram Bot API."""
        url = f"{self.base_url}/sendDocument"
        payload = {"chat_id": recipient_id, "document": file_url, "caption": caption}
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            return response.status_code == 200

    async def parse_incoming(self, payload: dict) -> IncomingMessage:
        """Converte payload do webhook Telegram em IncomingMessage."""
        message = payload.get("message", {})
        chat_id = str(message.get("chat", {}).get("id", ""))

        if "text" in message:
            msg_type = MessageType.TEXT
            text = message["text"]
            media_url = None
        elif "voice" in message:
            msg_type = MessageType.AUDIO
            text = None
            media_url = message["voice"].get("file_id")
        elif "document" in message:
            msg_type = MessageType.DOCUMENT
            text = None
            media_url = message["document"].get("file_id")
        else:
            msg_type = MessageType.TEXT
            text = ""
            media_url = None

        return IncomingMessage(
            channel=ChannelType.TELEGRAM,
            channel_user_id=chat_id,
            message_type=msg_type,
            text=text,
            media_url=media_url,
            raw_payload=payload
        )
