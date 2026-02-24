"""Application Settings."""
from functools import lru_cache
from pydantic_settings import SettingsConfigDict, BaseSettings


class Settings(BaseSettings):
    """Application configuration."""

    SERVICE_NAME: str = "video-service"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5433/video_db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/1"

    # AWS
    AWS_ENDPOINT_URL: str = ""
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_DEFAULT_REGION: str = "us-east-1"

    # S3
    S3_BUCKET: str = "video-uploads"

    # SNS
    SNS_TOPIC_ARN: str = ""

    # Auth Service
    AUTH_SERVICE_URL: str = "http://localhost:8001"
    model_config = SettingsConfigDict(env_file=".env")


@lru_cache()
def get_settings() -> Settings:
    return Settings()
