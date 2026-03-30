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
_memory_fallback: dict = {}


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
        Se o Redis falhar, salva na memória RAM (fallback).
        """
        ttl_hours = ttl_hours or settings.session_timeout_hours
        state_dict = state.model_dump() if hasattr(state, "model_dump") else state.dict()
        state_json = json.dumps(state_dict, default=str).encode('utf-8')
        
        try:
            client = await _get_client()
            await client.setex(
                f"session:{session_id}",
                timedelta(hours=ttl_hours),
                state_json
            )
            logger.info("sessao_salva_redis", session_id=session_id, ttl_hours=ttl_hours)
            
        except Exception as e:
            logger.warning("erro_salvar_sessao_redis_usando_fallback", session_id=session_id, error=str(e))
            # Fallback: salva na RAM
            _memory_fallback[session_id] = state_json

    @staticmethod
    async def load(session_id: str) -> Optional[ConversationState]:
        """
        Carrega o estado da sessão do Redis ou do fallback de RAM.
        """
        state_json = None
        try:
            client = await _get_client()
            state_json = await client.get(f"session:{session_id}")
        except Exception as e:
            logger.warning("erro_ler_sessao_redis_usando_fallback", session_id=session_id, error=str(e))
            
        # Se não achou na exception/Redis, tenta no fallback de memória
        if not state_json:
            state_json = _memory_fallback.get(session_id)
            
        if not state_json:
            logger.info("sessao_nao_encontrada", session_id=session_id)
            return None
            
        try:
            state_dict = json.loads(state_json.decode('utf-8'))
            state = ConversationState(**state_dict)
            logger.info("sessao_carregada", session_id=session_id)
            return state
        except Exception as e:
            logger.error("erro_parsear_sessao", session_id=session_id, error=str(e))
            return None

    @staticmethod
    async def delete(session_id: str) -> None:
        """Remove a sessão do Redis e da RAM."""
        try:
            client = await _get_client()
            await client.delete(f"session:{session_id}")
            logger.info("sessao_removida_redis", session_id=session_id)
        except Exception as e:
            logger.warning("erro_remover_sessao_redis_removendo_fallback", session_id=session_id, error=str(e))
            
        if session_id in _memory_fallback:
            del _memory_fallback[session_id]

    @staticmethod
    async def exists(session_id: str) -> bool:
        """Verifica se a sessão existe no Redis ou RAM."""
        try:
            client = await _get_client()
            if await client.exists(f"session:{session_id}"):
                return True
        except Exception as e:
            logger.warning("erro_verificar_sessao_redis_buscando_fallback", session_id=session_id, error=str(e))
            
        return session_id in _memory_fallback

    @staticmethod
    async def close() -> None:
        """Fecha a conexão com o Redis."""
        global _client
        if _client:
            await _client.close()
            logger.info("redis_client_fechado")
            _client = None

