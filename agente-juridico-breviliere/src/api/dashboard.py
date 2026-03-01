from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from src.api.webhooks import _sessions
from src.models.metrics import DashboardMetrics, ConversationSummary
from src.models.conversation import ConversationState
from src.config.logging import get_logger

router = APIRouter(prefix="/admin/dashboard", tags=["dashboard"])
logger = get_logger(__name__)

@router.get("/metrics", response_model=DashboardMetrics)
async def get_metrics():
    """Calcula metricas gerais a partir das sessoes em memoria."""
    total = len(_sessions)
    active = 0
    completed = 0
    by_channel = {}
    by_area = {}
    by_step = {}
    total_score = 0
    
    for state in _sessions.values():
        # Active vs Completed
        if state.current_step == "closed":
            completed += 1
        else:
            active += 1
            
        # Channels
        channel = state.channel.value if hasattr(state.channel, "value") else str(state.channel)
        by_channel[channel] = by_channel.get(channel, 0) + 1
        
        # Areas
        area = state.area_juridica or "nao_identificada"
        by_area[area] = by_area.get(area, 0) + 1
        
        # Steps
        step = state.current_step
        by_step[step] = by_step.get(step, 0) + 1
        
        total_score += state.score
        
    avg_score = (total_score / total) if total > 0 else 0.0
    
    return DashboardMetrics(
        total_conversations=total,
        active_conversations=active,
        completed_conversations=completed,
        conversations_by_channel=by_channel,
        conversations_by_area=by_area,
        average_score=round(avg_score, 2),
        conversations_by_step=by_step
    )

@router.get("/conversations", response_model=List[ConversationSummary])
async def list_conversations(
    channel: Optional[str] = None,
    step: Optional[str] = None,
    min_score: Optional[int] = Query(None, ge=0)
):
    """Lista resumos das conversas com filtros."""
    summaries = []
    
    for state in _sessions.values():
        state_channel = state.channel.value if hasattr(state.channel, "value") else str(state.channel)
        
        # Filtros
        if channel and state_channel != channel:
            continue
        if step and state.current_step != step:
            continue
        if min_score is not None and state.score < min_score:
            continue
            
        created_at = None
        if state.history:
            # Assume que o primeiro item do history e a criacao (user ou assistant)
            # Como nao temos campo timestamp explicito no history do model, 
            # retornaremos None ou um placeholder
            created_at = "Indisponivel"

        summaries.append(ConversationSummary(
            session_id=state.session_id,
            channel=state_channel,
            area_juridica=state.area_juridica,
            score=state.score,
            current_step=state.current_step,
            messages_count=len(state.history),
            lgpd_consent=state.lgpd_consent,
            created_at=created_at
        ))
        
    return summaries

@router.get("/conversations/{session_id}", response_model=ConversationState)
async def get_conversation_detail(session_id: str):
    """Retorna o estado completo de uma conversa."""
    if session_id not in _sessions:
        raise HTTPException(status_code=404, detail="Conversa nao encontrada")
    return _sessions[session_id]

@router.get("/conversations/{session_id}/history")
async def get_conversation_history(session_id: str):
    """Retorna apenas o historico de mensagens."""
    if session_id not in _sessions:
        raise HTTPException(status_code=404, detail="Conversa nao encontrada")
    return _sessions[session_id].history
