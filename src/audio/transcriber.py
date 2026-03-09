import os
import tempfile
import httpx
from openai import AsyncOpenAI
from src.config.settings import get_settings
from src.config.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)

class AudioTranscriber:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.whisper_model = settings.whisper_model

    async def download_whatsapp_media(self, media_id: str) -> bytes:
        """Baixa o binario do audio da Meta Cloud API (WhatsApp)."""
        headers = {"Authorization": f"Bearer {settings.whatsapp_api_token}"}
        
        # Passo 1: Pegar a URL do binario
        url = f"https://graph.facebook.com/v18.0/{media_id}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            media_url = resp.json().get("url")
            
            # Passo 2: Baixar o binario
            audio_resp = await client.get(media_url, headers=headers)
            audio_resp.raise_for_status()
            return audio_resp.content

    async def download_telegram_media(self, file_id: str) -> bytes:
        """Baixa o binario do audio do Telegram Bot API."""
        token = settings.telegram_bot_token
        
        # Passo 1: Pegar o file_path
        url = f"https://api.telegram.org/bot{token}/getFile?file_id={file_id}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
            resp.raise_for_status()
            file_path = resp.json().get("result", {}).get("file_path")
            
            # Passo 2: Baixar o binario
            download_url = f"https://api.telegram.org/file/bot{token}/{file_path}"
            audio_resp = await client.get(download_url)
            audio_resp.raise_for_status()
            return audio_resp.content

    async def transcribe(self, audio_bytes: bytes, file_extension: str = "ogg") -> str:
        """Salva em arquivo temporario e transcreve com Whisper."""
        try:
            with tempfile.NamedTemporaryFile(suffix=f".{file_extension}", delete=False) as tmp:
                tmp.write(audio_bytes)
                tmp_path = tmp.name

            logger.info("iniciando_transcricao_whisper", size=len(audio_bytes))
            
            with open(tmp_path, "rb") as audio_file:
                response = await self.client.audio.transcriptions.create(
                    model=self.whisper_model,
                    file=audio_file
                )
            
            os.unlink(tmp_path)
            return response.text
        except Exception as e:
            logger.error("erro_transcricao_whisper", error=str(e))
            if 'tmp_path' in locals() and os.path.exists(tmp_path):
                os.unlink(tmp_path)
            return "[Audio nao pode ser transcrito]"
