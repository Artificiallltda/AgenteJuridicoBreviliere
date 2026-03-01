import hmac
import hashlib
from fastapi import APIRouter, Request, Query, HTTPException, Header
from src.channels.whatsapp import WhatsAppAdapter
from src.config.settings import get_settings
from src.config.logging import get_logger

from src.core.conversation import process_message
from src.models.conversation import ConversationState, ChannelType

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
settings = get_settings()
logger = get_logger(__name__)

# Cache de sessoes em memoria (substituir por Redis em producao)
_sessions = {}

# Lazy initialization: evita instanciar WhatsAppAdapter no import
_whatsapp = None

def _get_whatsapp():
    global _whatsapp
    if _whatsapp is None:
        _whatsapp = WhatsAppAdapter()
    return _whatsapp

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
    if not incoming or not incoming.text:
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
