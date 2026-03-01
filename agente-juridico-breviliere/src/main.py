from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.config.settings import get_settings
from src.config.logging import setup_logging, get_logger
from src.api.webhooks import router as webhook_router

setup_logging()
logger = get_logger(__name__)
settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("iniciando_aplicacao", app_name=settings.app_name, debug=settings.debug)
    yield
    logger.info("encerrando_aplicacao")

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan
)

# Registrar roteadores
app.include_router(webhook_router)

@app.get("/health")
async def health_check():
    logger.info("health_check_solicitado")
    return {"status": "online", "app": settings.app_name, "version": "0.1.0"}
