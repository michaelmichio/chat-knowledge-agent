from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "Chat Knowledge Agent"
    APP_ENV: str = "development"
    PORT: int = 8000

    DATABASE_URL: str
    REDIS_URL: str
    VECTOR_DB_URL: str
    CORS_ORIGINS: str = "http://localhost:3000"
    
    UPLOAD_DIR: str = "/data/uploads"
    MAX_UPLOAD_MB: int = 25
    ALLOWED_MIME: str = "application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/csv"
    
    OPENAI_API_KEY: str | None = None
    LLM_PROVIDER: str = "openai"
    
    # ⬅️ custom model provider
    CUSTOM_LLM_URL: str | None = None
    CUSTOM_LLM_TOKEN: str | None = None
    CUSTOM_LLM_MODEL: str = "Qwen2.5-7B"

    class Config:
        env_file = ".env"


@lru_cache
def get_settings():
    """Cache config agar hanya dibaca sekali."""
    return Settings()
