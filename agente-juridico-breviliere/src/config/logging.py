import logging
import sys
import structlog
from src.config.settings import get_settings

settings = get_settings()

def setup_logging():
    """Configura o structlog para logs JSON estruturados."""
    
    # Processadores padrão para structlog
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    if settings.debug:
        # Em desenvolvimento: Logs bonitos e coloridos no console
        processors.append(structlog.dev.ConsoleRenderer())
    else:
        # Em produção: Logs JSON para ELK/Sentry/Grafana
        processors.append(structlog.processors.JSONRenderer())

    structlog.configure(
        processors=processors,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Redirecionar logs do Python padrão (como os do FastAPI/Uvicorn) para o structlog
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=settings.log_level,
    )

def get_logger(name: str):
    """Retorna um logger estruturado."""
    return structlog.get_logger(name)
