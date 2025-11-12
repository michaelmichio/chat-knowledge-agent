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

    class Config:
        env_file = ".env"


@lru_cache
def get_settings():
    """Cache config agar hanya dibaca sekali."""
    return Settings()
