from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query, Body
from src.api.webhooks import _sessions, _get_whatsapp, _get_telegram, _get_instagram
from src.notifications.proactive import ProactiveNotifier
from src.config.logging import get_logger

router = APIRouter(prefix="/admin/notifications", tags=["notifications"])
logger = get_logger(__name__)

def _get_notifier():
    """Inicializa o ProactiveNotifier com os adaptadores reais."""
    adapters = {
        "whatsapp": _get_whatsapp(),
        "telegram": _get_telegram(),
        "instagram": _get_instagram()
    }
    return ProactiveNotifier(adapters)

@router.post("/followup")
async def send_followup_manual(
    session_id: str = Body(..., embed=True),
    message: Optional[str] = Body(None, embed=True)
):
    """Envia um followup manual para uma sessao especifica."""
    if session_id not in _sessions:
        raise HTTPException(status_code=404, detail="Sessao nao encontrada")
    
    state = _sessions[session_id]
    notifier = _get_notifier()
    
    channel = state.channel.value if hasattr(state.channel, "value") else str(state.channel)
    followup_msg = message or notifier.get_followup_message(state.current_step, state.area_juridica)
    
    success = await notifier.send_followup(session_id, channel, followup_msg)
    
    if success:
        return {"status": "sent", "session_id": session_id, "channel": channel}
    else:
        raise HTTPException(status_code=500, detail="Falha ao enviar mensagem de followup")

@router.post("/followup-all")
async def send_followup_to_all_abandoned(
    timeout_minutes: int = Body(30, embed=True),
    message: Optional[str] = Body(None, embed=True)
):
    """Envia followup para todas as sessoes que atendem ao criterio de abandono."""
    notifier = _get_notifier()
    abandoned_ids = await notifier.check_abandoned_sessions(_sessions, timeout_minutes)
    
    sent_count = 0
    failed_count = 0
    details = []
    
    for sid in abandoned_ids:
        state = _sessions[sid]
        channel = state.channel.value if hasattr(state.channel, "value") else str(state.channel)
        followup_msg = message or notifier.get_followup_message(state.current_step, state.area_juridica)
        
        success = await notifier.send_followup(sid, channel, followup_msg)
        if success:
            sent_count += 1
            details.append({"session_id": sid, "status": "sent"})
        else:
            failed_count += 1
            details.append({"session_id": sid, "status": "failed"})
            
    return {
        "sent": sent_count,
        "failed": failed_count,
        "sessions": details
    }

@router.get("/abandoned")
async def list_abandoned(
    timeout_minutes: int = Query(30)
):
    """Lista sessoes detectadas como abandonadas."""
    notifier = _get_notifier()
    abandoned_ids = await notifier.check_abandoned_sessions(_sessions, timeout_minutes)
    
    results = []
    for sid in abandoned_ids:
        state = _sessions[sid]
        results.append({
            "session_id": sid,
            "channel": state.channel.value if hasattr(state.channel, "value") else str(state.channel),
            "step": state.current_step,
            "messages_count": len(state.history)
        })
        
    return results
