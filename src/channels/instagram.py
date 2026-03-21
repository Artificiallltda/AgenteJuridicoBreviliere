import httpx
from channels.base import ChannelAdapter
from models.conversation import IncomingMessage, ChannelType, MessageType
from config.settings import get_settings
from config.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


class InstagramAdapter(ChannelAdapter):
    def __init__(self):
        api_version = getattr(settings, "meta_api_version", "v18.0")
        self.base_url = f"https://graph.facebook.com/{api_version}/me/messages"
        self.headers = {"Authorization": f"Bearer {settings.instagram_access_token}"}

    async def send_text(self, recipient_id: str, text: str) -> bool:
        """Envia mensagem de texto via Instagram Messaging API."""
        payload = {
            "recipient": {"id": recipient_id},
            "message": {"text": text}
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(self.base_url, json=payload, headers=self.headers)
            return response.status_code == 200

    async def send_document(self, recipient_id: str, file_url: str, caption: str) -> bool:
        """Envia documento via Instagram (como attachment)."""
        payload = {
            "recipient": {"id": recipient_id},
            "message": {
                "attachment": {
                    "type": "file",
                    "payload": {"url": file_url}
                },
                "text": caption
            }
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(self.base_url, json=payload, headers=self.headers)
            return response.status_code == 200

    async def parse_incoming(self, payload: dict) -> IncomingMessage:
        """Converte payload do webhook Instagram em IncomingMessage."""
        entry = payload.get("entry", [{}])[0]
        messaging = entry.get("messaging", [{}])[0]
        sender_id = messaging.get("sender", {}).get("id", "")
        message = messaging.get("message", {})

        if "text" in message:
            msg_type = MessageType.TEXT
            text = message["text"]
            media_url = None
        elif "attachments" in message:
            attachment = message["attachments"][0]
            att_type = attachment.get("type", "")
            if att_type == "audio":
                msg_type = MessageType.AUDIO
            elif att_type == "image":
                msg_type = MessageType.IMAGE
            else:
                msg_type = MessageType.DOCUMENT
            text = None
            media_url = attachment.get("payload", {}).get("url")
        else:
            msg_type = MessageType.TEXT
            text = ""
            media_url = None

        return IncomingMessage(
            channel=ChannelType.INSTAGRAM,
            channel_user_id=sender_id,
            message_type=msg_type,
            text=text,
            media_url=media_url,
            raw_payload=payload
        )
