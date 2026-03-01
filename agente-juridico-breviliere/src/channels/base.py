from abc import ABC, abstractmethod
from src.models.conversation import IncomingMessage


class ChannelAdapter(ABC):
    @abstractmethod
    async def send_text(self, recipient_id: str, text: str) -> bool:
        """Envia mensagem de texto."""
        pass

    @abstractmethod
    async def send_document(self, recipient_id: str, file_url: str, caption: str) -> bool:
        """Envia documento (PDF/DOCX)."""
        pass

    @abstractmethod
    async def parse_incoming(self, payload: dict) -> IncomingMessage:
        """Converte payload do webhook em IncomingMessage."""
        pass
