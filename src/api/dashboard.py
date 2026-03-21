from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from models.metrics import DashboardMetrics, ConversationSummary
from models.conversation import ConversationState
from config.logging import get_logger

router = APIRouter(prefix="/admin/dashboard", tags=["dashboard"])
logger = get_logger(__name__)

# Nota: Para producao, implementar um DashboardStore que mantenha metricas em cache (Redis/Memcached)
# ou use um banco de dados analitico. Este endpoint retorna dados basicos por enquanto.

@router.get("/metrics", response_model=DashboardMetrics)
async def get_metrics():
    """
    Calcula metricas gerais.
    
    NOTA: Para producao, implementar armazenamento de metricas em Redis ou banco.
    Este endpoint retorna placeholders ate que um DashboardStore seja implementado.
    """
    logger.warning("dashboard_metrics_placeholder", reason="DashboardStore nao implementado")
    
    return DashboardMetrics(
        total_conversations=0,
        active_conversations=0,
        completed_conversations=0,
        conversations_by_channel={},
        conversations_by_area={},
        average_score=0.0,
        conversations_by_step={}
    )

@router.get("/conversations", response_model=List[ConversationSummary])
async def list_conversations(
    channel: Optional[str] = None,
    step: Optional[str] = None,
    min_score: Optional[int] = Query(None, ge=0)
):
    """
    Lista resumos das conversas com filtros.
    
    NOTA: Para producao, implementar DashboardStore ou usar banco de dados.
    """
    logger.warning("dashboard_conversations_placeholder", reason="DashboardStore nao implementado")
    return []

@router.get("/conversations/{session_id}", response_model=ConversationState)
async def get_conversation_detail(session_id: str):
    """Retorna o estado completo de uma conversa."""
    # Tenta carregar do Redis
    from database.redis_session_store import RedisSessionStore
    
    state = await RedisSessionStore.load(session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Conversa nao encontrada")
    return state

@router.get("/conversations/{session_id}/history")
async def get_conversation_history(session_id: str):
    """Retorna apenas o historico de mensagens."""
    from database.redis_session_store import RedisSessionStore
    
    state = await RedisSessionStore.load(session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Conversa nao encontrada")
    return state.history
