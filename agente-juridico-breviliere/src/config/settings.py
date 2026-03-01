from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    
    # App
    app_name: str = "Agente Juridico Breviliere"
    debug: bool = False
    log_level: str = "INFO"

    # LLM
    llm_provider: str = "openai"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    openai_model_light: str = "gpt-4o-mini"

    # Embeddings / Vector Store
    embedding_model: str = "text-embedding-3-small"
    chroma_persist_dir: str = "./data/chroma"

    # Database
    database_url: str = "postgresql+asyncpg://juridico:juridico_dev@localhost:5432/juridico"
    redis_url: str = "redis://localhost:6379/0"

    # Channels
    whatsapp_verify_token: str = ""
    whatsapp_api_token: str = ""
    whatsapp_phone_number_id: str = ""
    telegram_bot_token: str = ""
    instagram_access_token: str = ""

    # Integrations
    crm_provider: str = "pipedrive"
    crm_api_token: str = ""
    slack_webhook_url: str = ""
    notification_email: str = ""
    meta_api_version: str = "v18.0"

    # Whisper
    whisper_model: str = "whisper-1"

    # LGPD
    privacy_policy_url: str = ""
    terms_of_use_url: str = ""
    data_retention_days: int = 1825

@lru_cache()
def get_settings() -> Settings:
    return Settings()
