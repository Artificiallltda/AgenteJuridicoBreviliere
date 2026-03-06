import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # OPENAI
    OPENAI_API_KEY: str = ""
    
    # GOOGLE GEMINI
    GEMINI_API_KEY: str = ""
    
    # EVOLUTION API (WhatsApp)
    EVOLUTION_API_URL: str = ""
    EVOLUTION_API_KEY: str = ""
    INSTANCE_NAME: str = "arth_instance"
    
    # TELEGRAM
    TELEGRAM_BOT_TOKEN: str = ""
    
    class Config:
        env_file = ".env"

settings = Settings()
