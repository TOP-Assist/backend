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
