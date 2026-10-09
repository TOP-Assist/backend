"""Application-level configuration as configured by the environment."""

from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration data."""

    model_config = SettingsConfigDict(
        env_prefix="BACKEND_",
        env_file=".env",
        env_file_encoding="utf-8",
        frozen=True,
        hide_input_in_errors=True,
    )
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    mongodb_uri: SecretStr
    mongodb_database: str = Field(min_length=1)
    mongodb_server_selection_timeout_ms: int = Field(
        default=5_000,
        gt=0,
    )

    analysis_num_workers: int = 1
    analysis_model: str = "de_dep_news_trf"

    llm_base_url: str
    llm_api_key: SecretStr
    llm_model: str

    llm_temperature: float = Field(default=0, ge=0, le=2)
    llm_timeout_seconds: float = Field(default=60, gt=0)
    llm_max_retries: int = Field(default=0, ge=0, le=2)

    translation_base_prompt: str
