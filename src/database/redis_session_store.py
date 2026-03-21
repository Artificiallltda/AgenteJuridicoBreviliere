"""
RedisSessionStore — Persistência de ConversationState no Redis.

Alternativa mais leve e rápida ao SessionStore PostgreSQL,
ideal para sessões temporárias com TTL automático.
"""

import json
from typing import Optional
from datetime import timedelta

import redis.asyncio as redis

from config.settings import get_settings
from config.logging import get_logger
from models.conversation import ConversationState

logger = get_logger(__name__)
settings = get_settings()

# Cliente Redis singleton
_client: Optional[redis.Redis] = None


async def _get_client() -> redis.Redis:
    """Retorna o cliente Redis, criando um novo se necessário."""
    global _client
    if _client is None:
        _client = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=False
        )
        logger.info("redis_client_criado", url=settings.redis_url)
    return _client


class RedisSessionStore:
    """Gerencia a persistência de sessões de conversa no Redis com TTL."""

    @staticmethod
    async def save(session_id: str, state: ConversationState, ttl_hours: int = None) -> None:
        """
        Salva o estado da sessão no Redis com TTL.
        
        Args:
            session_id: ID único da sessão
            state: Estado da conversa
            ttl_hours: Tempo de vida em horas (default: session_timeout_hours do settings)
        """
        try:
            client = await _get_client()
            ttl_hours = ttl_hours or settings.session_timeout_hours
            
            state_dict = state.model_dump() if hasattr(state, "model_dump") else state.dict()
            state_json = json.dumps(state_dict, default=str).encode('utf-8')
            
            await client.setex(
                f"session:{session_id}",
                timedelta(hours=ttl_hours),
                state_json
            )
            
            logger.info("sessao_salva_redis", session_id=session_id, ttl_hours=ttl_hours)
            
        except Exception as e:
            logger.error("erro_salvar_sessao_redis", session_id=session_id, error=str(e))
            # Fallback: loga erro mas não quebra o fluxo

    @staticmethod
    async def load(session_id: str) -> Optional[ConversationState]:
        """
        Carrega o estado da sessão do Redis.
        
        Args:
            session_id: ID único da sessão
            
        Returns:
            ConversationState se existir, None caso contrário
        """
        try:
            client = await _get_client()
            state_json = await client.get(f"session:{session_id}")
            
            if not state_json:
                logger.info("sessao_nao_encontrada_redis", session_id=session_id)
                return None
            
            state_dict = json.loads(state_json.decode('utf-8'))
            state = ConversationState(**state_dict)
            
            logger.info("sessao_carregada_redis", session_id=session_id)
            return state
            
        except Exception as e:
            logger.error("erro_carregar_sessao_redis", session_id=session_id, error=str(e))
            return None

    @staticmethod
    async def delete(session_id: str) -> None:
        """Remove a sessão do Redis."""
        try:
            client = await _get_client()
            await client.delete(f"session:{session_id}")
            logger.info("sessao_removida_redis", session_id=session_id)
        except Exception as e:
            logger.error("erro_remover_sessao_redis", session_id=session_id, error=str(e))

    @staticmethod
    async def exists(session_id: str) -> bool:
        """Verifica se a sessão existe no Redis."""
        try:
            client = await _get_client()
            return await client.exists(f"session:{session_id}")
        except Exception as e:
            logger.error("erro_verificar_sessao_redis", session_id=session_id, error=str(e))
            return False

    @staticmethod
    async def close() -> None:
        """Fecha a conexão com o Redis."""
        global _client
        if _client:
            await _client.close()
            logger.info("redis_client_fechado")
            _client = None
