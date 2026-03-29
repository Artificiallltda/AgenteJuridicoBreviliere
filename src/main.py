import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from config.logging import setup_logging, get_logger

# Setup logging primeiro
try:
    setup_logging()
except Exception as e:
    print(f"⚠️ Erro ao configurar logging: {e}")
    print("Usando logging básico...")
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stdout
    )

logger = get_logger(__name__) if 'get_logger' in dir() else logging.getLogger(__name__)

# Import settings após logging
try:
    from config.settings import get_settings
    settings = get_settings()
    logger.info("configuracao_carregada", app_name=settings.app_name)
except Exception as e:
    logger.error(f"Erro ao carregar settings: {e}")
    # Fallback para settings básicos
    class FallbackSettings:
        app_name = "Agente Juridico Breviliere"
        debug = True
    settings = FallbackSettings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("iniciando_aplicacao", app_name=settings.app_name, debug=settings.debug)
        
        # Importa routers dentro do lifespan para capturar erros
        from api.webhooks import router as webhook_router
        from api.admin import router as admin_router
        from api.dashboard import router as dashboard_router
        from api.notifications import router as notifications_router
        
        # Registrar roteadores
        app.include_router(webhook_router)
        app.include_router(admin_router)
        app.include_router(dashboard_router)
        app.include_router(notifications_router)
        
        logger.info("roteadores_registrados")
        yield
        logger.info("encerrando_aplicacao")
    except Exception as e:
        logger.error(f"Erro no lifespan: {e}", exc_info=True)
        raise

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan
)

@app.get("/health")
async def health_check():
    try:
        logger.info("health_check_solicitado")
        return {"status": "online", "app": settings.app_name, "version": "0.1.0"}
    except Exception as e:
        logger.error(f"Erro no health check: {e}")
        return {"status": "error", "message": str(e)}
