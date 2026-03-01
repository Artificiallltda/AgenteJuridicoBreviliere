import hmac
import hashlib
from fastapi import APIRouter, Request, Query, HTTPException, Header
from src.channels.whatsapp import WhatsAppAdapter
from src.channels.telegram import TelegramAdapter
from src.channels.instagram import InstagramAdapter
from src.audio.transcriber import AudioTranscriber
from src.config.settings import get_settings
from src.config.logging import get_logger

from src.core.conversation import process_message
from src.models.conversation import ConversationState, ChannelType, MessageType

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
settings = get_settings()
logger = get_logger(__name__)

# Cache de sessoes em memoria (substituir por Redis em producao)
_sessions = {}

# Lazy initialization: evita instanciar Adapters no import
_whatsapp = None
_telegram = None
_instagram = None
_transcriber = None

def _get_whatsapp():
    global _whatsapp
    if _whatsapp is None:
        _whatsapp = WhatsAppAdapter()
    return _whatsapp

def _get_telegram():
    global _telegram
    if _telegram is None:
        _telegram = TelegramAdapter()
    return _telegram

def _get_instagram():
    global _instagram
    if _instagram is None:
        _instagram = InstagramAdapter()
    return _instagram

def _get_transcriber():
    global _transcriber
    if _transcriber is None:
        _transcriber = AudioTranscriber()
    return _transcriber

def validate_signature(payload: bytes, signature: str):
    """Valida assinatura X-Hub-Signature-256 da Meta Cloud API."""
    if not signature:
        return False
    expected = hmac.HMAC(
        settings.whatsapp_api_token.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)

@router.get("/whatsapp")
async def verify_whatsapp(
    mode: str = Query(None, alias="hub.mode"),
    token: str = Query(None, alias="hub.verify_token"),
    challenge: str = Query(None, alias="hub.challenge"),
):
    if mode == "subscribe" and token == settings.whatsapp_verify_token:
        logger.info("whatsapp_webhook_verificado_com_sucesso")
        return int(challenge)
    raise HTTPException(status_code=403)

@router.post("/whatsapp")
async def receive_whatsapp(
    request: Request, 
    x_hub_signature_256: str = Header(None)
):
    payload = await request.body()
    if not validate_signature(payload, x_hub_signature_256):
        logger.error("falha_validacao_assinatura_whatsapp")
        # raise HTTPException(status_code=401) # Desabilitado para testes locais sem Meta

    data = await request.json()
    logger.info("webhook_whatsapp_recebido")

    # a) Extrair IncomingMessage
    incoming = _get_whatsapp().parse_incoming(data)
    if not incoming:
        return {"status": "ignored"}

    user_message = incoming.text

    # Logica de audio para WhatsApp
    if not user_message and incoming.message_type == MessageType.AUDIO and incoming.media_url:
        logger.info("transcrevendo_audio_whatsapp", media_id=incoming.media_url)
        audio_bytes = await _get_transcriber().download_whatsapp_media(incoming.media_url)
        user_message = await _get_transcriber().transcribe(audio_bytes)

    if not user_message:
        return {"status": "ignored"}

    session_id = incoming.channel_user_id

    # b) Criar/recuperar ConversationState
    if session_id not in _sessions:
        _sessions[session_id] = ConversationState(
            session_id=session_id,
            channel=ChannelType.WHATSAPP
        )
    
    state = _sessions[session_id]

    # c) Processar mensagem
    response_text = await process_message(state, incoming.text)

    # d) Enviar resposta via WhatsApp
    await _get_whatsapp().send_text(session_id, response_text)

    return {"status": "ok"}

@router.post("/telegram")
async def receive_telegram(request: Request):
    """Recebe mensagens do Telegram Bot API."""
    data = await request.json()
    logger.info("webhook_telegram_recebido")

    # a) Extrair IncomingMessage
    incoming = _get_telegram().parse_incoming(data)
    if not incoming:
        return {"status": "ignored"}

    user_message = incoming.text

    # Logica de audio para Telegram
    if not user_message and incoming.message_type == MessageType.AUDIO and incoming.media_url:
        logger.info("transcrevendo_audio_telegram", file_id=incoming.media_url)
        audio_bytes = await _get_transcriber().download_telegram_media(incoming.media_url)
        user_message = await _get_transcriber().transcribe(audio_bytes)

    if not user_message:
        return {"status": "ignored"}

    session_id = incoming.channel_user_id

    # b) Criar/recuperar ConversationState
    if session_id not in _sessions:
        _sessions[session_id] = ConversationState(
            session_id=session_id,
            channel=ChannelType.TELEGRAM
        )
    
    state = _sessions[session_id]

    # c) Processar mensagem
    response_text = await process_message(state, user_message)

    # d) Enviar resposta via Telegram
    await _get_telegram().send_text(session_id, response_text)

    return {"status": "ok"}

@router.get("/telegram/health")
async def telegram_health():
    """Health check do webhook Telegram."""
    return {"status": "ok", "channel": "telegram"}

@router.get("/instagram")
async def verify_instagram(
    mode: str = Query(None, alias="hub.mode"),
    token: str = Query(None, alias="hub.verify_token"),
    challenge: str = Query(None, alias="hub.challenge"),
):
    """Verificacao do webhook para Instagram (Meta)."""
    if mode == "subscribe" and token == settings.whatsapp_verify_token:
        logger.info("instagram_webhook_verificado_com_sucesso")
        return int(challenge)
    raise HTTPException(status_code=403)

@router.post("/instagram")
async def receive_instagram(request: Request):
    """Recebe mensagens do Instagram Messaging API."""
    data = await request.json()
    logger.info("webhook_instagram_recebido")

    # a) Extrair IncomingMessage
    incoming = _get_instagram().parse_incoming(data)
    if not incoming:
        return {"status": "ignored"}

    user_message = incoming.text

    # Logica de audio para Instagram (usa mesma Meta API)
    if not user_message and incoming.message_type == MessageType.AUDIO and incoming.media_url:
        logger.info("transcrevendo_audio_instagram", media_id=incoming.media_url)
        audio_bytes = await _get_transcriber().download_whatsapp_media(incoming.media_url)
        user_message = await _get_transcriber().transcribe(audio_bytes)

    if not user_message:
        return {"status": "ignored"}

    session_id = incoming.channel_user_id

    # b) Criar/recuperar ConversationState
    if session_id not in _sessions:
        _sessions[session_id] = ConversationState(
            session_id=session_id,
            channel=ChannelType.INSTAGRAM
        )
    
    state = _sessions[session_id]

    # c) Processar mensagem
    response_text = await process_message(state, user_message)

    # d) Enviar resposta via Instagram
    await _get_instagram().send_text(session_id, response_text)

    return {"status": "ok"}

@router.get("/instagram/health")
async def instagram_health():
    """Health check do webhook Instagram."""
    return {"status": "ok", "channel": "instagram"}
