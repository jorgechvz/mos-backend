"""Application settings module."""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    stream_api_key: str = Field(..., alias="STREAM_API_KEY")
    stream_api_secret: str = Field(..., alias="STREAM_API_SECRET")
    stream_token_seconds: int = Field(60 * 60, alias="STREAM_TOKEN_SECONDS")

    class Config:
        """Configuration for Pydantic BaseSettings."""

        env_file = ".env"
        env_prefix = "STREAM_"
        case_sensitive = False


settings = Settings()
