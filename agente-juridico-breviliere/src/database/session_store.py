"""
SessionStore — Persistência de ConversationState no PostgreSQL.

Salva e carrega o estado da conversa entre mensagens,
garantindo que o bot não perde contexto após reinicializações do servidor.
"""

import json
from datetime import datetime, timedelta, timezone
from typing import Optional

import asyncpg

from src.config.settings import get_settings
from src.config.logging import get_logger
from src.models.conversation import ConversationState, ChannelType

logger = get_logger(__name__)
settings = get_settings()

# Pool de conexão reutilizável
_pool: Optional[asyncpg.Pool] = None


async def _get_pool() -> asyncpg.Pool:
    """Retorna o pool de conexões, criando um novo se necessário."""
    global _pool
    if _pool is None:
        # Converte URL SQLAlchemy → asyncpg
        url = settings.database_url.replace("postgresql+asyncpg://", "postgresql://")
        _pool = await asyncpg.create_pool(url, min_size=1, max_size=5)
        logger.info("session_store_pool_criado")
    return _pool


class SessionStore:
    """Gerencia a persistência de sessões de conversa no PostgreSQL."""

    @staticmethod
    async def save(session_id: str, state: ConversationState) -> None:
        """Salva ou atualiza o estado da sessão no banco."""
        try:
            pool = await _get_pool()
            state_dict = state.model_dump() if hasattr(state, "model_dump") else state.dict()
            state_json = json.dumps(state_dict, default=str)

            async with pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO sessions (session_id, channel, state_json, updated_at)
                    VALUES ($1, $2, $3::jsonb, NOW())
                    ON CONFLICT (session_id) DO UPDATE
                        SET state_json = EXCLUDED.state_json,
                            updated_at = NOW()
                    """,
                    session_id,
                    state.channel.value if hasattr(state.channel, "value") else str(state.channel),
                    state_json,
                )
            logger.info("sessao_salva", session_id=session_id)
        except Exception as e:
            logger.error("erro_salvar_sessao", session_id=session_id, error=str(e))

    @staticmethod
    async def load(session_id: str) -> Optional[ConversationState]:
        """Carrega o estado da sessão do banco. Retorna None se não existir ou expirada."""
        try:
            pool = await _get_pool()
            timeout_hours = settings.session_timeout_hours

            async with pool.acquire() as conn:
                row = await conn.fetchrow(
                    """
                    SELECT state_json
                    FROM sessions
                    WHERE session_id = $1
                      AND updated_at > NOW() - ($2 || ' hours')::interval
                    """,
                    session_id,
                    str(timeout_hours),
                )

            if not row:
                logger.info("sessao_nao_encontrada_ou_expirada", session_id=session_id)
                return None

            state_dict = json.loads(row["state_json"])
            state = ConversationState(**state_dict)
            logger.info("sessao_carregada", session_id=session_id)
            return state
        except Exception as e:
            logger.error("erro_carregar_sessao", session_id=session_id, error=str(e))
            return None

    @staticmethod
    async def delete(session_id: str) -> None:
        """Remove a sessão do banco."""
        try:
            pool = await _get_pool()
            async with pool.acquire() as conn:
                await conn.execute(
                    "DELETE FROM sessions WHERE session_id = $1",
                    session_id,
                )
            logger.info("sessao_removida", session_id=session_id)
        except Exception as e:
            logger.error("erro_remover_sessao", session_id=session_id, error=str(e))

    @staticmethod
    async def cleanup_expired(hours: int = 24) -> int:
        """Remove sessões inativas há mais de `hours` horas. Retorna quantidade removida."""
        try:
            pool = await _get_pool()
            async with pool.acquire() as conn:
                result = await conn.execute(
                    """
                    DELETE FROM sessions
                    WHERE updated_at < NOW() - ($1 || ' hours')::interval
                    """,
                    str(hours),
                )
            count = int(result.split()[-1]) if result else 0
            logger.info("sessoes_expiradas_removidas", count=count, hours=hours)
            return count
        except Exception as e:
            logger.error("erro_cleanup_sessoes", error=str(e))
            return 0
