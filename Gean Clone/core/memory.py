import logging
import os

logger = logging.getLogger(__name__)


def get_checkpointer():
    """Retorna RedisSaver se REDIS_URL estiver configurado, senão MemorySaver."""
    redis_url = os.environ.get("REDIS_URL")
    if redis_url:
        try:
            from langgraph.checkpoint.redis import RedisSaver
            logger.info("Usando Redis para persistência de conversas")
            return RedisSaver.from_conn_string(redis_url)
        except ImportError:
            logger.warning("langgraph-checkpoint-redis não instalado — usando memória")
        except Exception as e:
            logger.warning(f"Falha ao conectar Redis ({e}) — usando memória")

    from langgraph.checkpoint.memory import MemorySaver
    logger.info("Usando MemorySaver (sem persistência entre reinicializações)")
    return MemorySaver()
