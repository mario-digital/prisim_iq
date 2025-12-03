"""Application configuration using Pydantic Settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "PrismIQ"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False

    # CORS
    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins string into list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    # Price Optimization
    price_min: float = 5.0
    price_max: float = 200.0
    price_step: float = 0.50
    optimization_cache_size: int = 1000

    # OpenAI
    openai_api_key: str = ""
    openai_default_model: str = "gpt-4o"
    openai_model_allowlist: str = "gpt-4o,gpt-4o-mini"

    @property
    def allowed_models(self) -> list[str]:
        return [m.strip() for m in self.openai_model_allowlist.split(",") if m.strip()]


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
