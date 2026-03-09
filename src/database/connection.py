from sqlalchemy.orm import DeclarativeBase
from src.config.logging import get_logger

logger = get_logger(__name__)

class Base(DeclarativeBase):
    pass

# Lazy engine creation - only connects when actually needed
_engine = None
_session_factory = None

def get_engine():
    global _engine
    if _engine is None:
        from sqlalchemy.ext.asyncio import create_async_engine
        from src.config.settings import get_settings
        settings = get_settings()
        _engine = create_async_engine(settings.database_url, pool_pre_ping=True, echo=False)
    return _engine

def get_session_factory():
    global _session_factory
    if _session_factory is None:
        from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
        _session_factory = async_sessionmaker(bind=get_engine(), class_=AsyncSession, expire_on_commit=False)
    return _session_factory

async def get_db():
    async with get_session_factory()() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error("erro_sessao_banco", error=str(e))
            raise
