
from functools import lru_cache

from pydantic import AnyHttpUrl, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        validate_default=True,
    )

    # PostgreSQL
    postgres_db: str
    postgres_user: str
    postgres_password: SecretStr
    postgres_host: str = "localhost"
    postgres_port: int = Field(default=5432, ge=1, le=65535)

    # TEI embedding service
    tei_embed_url: AnyHttpUrl = "http://localhost:8001/embed"

    # Embedding configuration
    embedding_batch_size: int = Field(default=4, ge=1)
    embedding_model_name: str = "embeddinggemma-300m"

    # HTTP configuration
    http_timeout_seconds: float = Field(default=120.0, gt=0)

    # LLM configuration
    llm_provider: str = "openai_compatible"
    llm_base_url: AnyHttpUrl = "http://localhost:8000/v1"
    llm_model_name: str = "movie-llm"
    llm_api_key: SecretStr | None = None

    # LLM generation defaults
    llm_temperature: float = Field(default=0.3, ge=0.0, le=2.0)
    llm_max_tokens: int = Field(default=256, gt=0)

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
