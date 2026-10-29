# SPDX-FileCopyrightText: 2026 Bergische Universität Wuppertal
# SPDX-FileCopyrightText: 2026 deepsight GmbH
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Application-level configuration as configured by the environment."""

from typing import Literal
from urllib.parse import quote_plus

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration data."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        frozen=True,
        hide_input_in_errors=True,
    )
    otel_service_name: str = "top-assist-backend"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    otel_exporter_otlp_endpoint: str | None = None

    mongodb_host: str = Field(min_length=1)
    mongodb_port: int = Field(default=27017, gt=0, le=65535)
    mongodb_username: str = Field(min_length=1)
    mongodb_password: SecretStr
    mongodb_database: str = Field(min_length=1)
    mongodb_server_selection_timeout_ms: int = Field(default=5_000, gt=0)

    analysis_num_workers: int = 1
    analysis_model: str = "de_dep_news_trf"

    llm_base_url: str
    llm_api_key: SecretStr
    llm_model: str
    llm_prompt_variant: str = Field(default="default", min_length=1)

    llm_temperature: float = Field(default=0, ge=0, le=2)
    llm_timeout_seconds: float = Field(default=60, gt=0)
    llm_max_retries: int = Field(default=0, ge=0, le=2)

    @property
    def mongodb_uri(self) -> SecretStr:
        """Connection URI assembled from the individual MongoDB settings."""
        username = quote_plus(self.mongodb_username)
        password = quote_plus(self.mongodb_password.get_secret_value())
        return SecretStr(
            f"mongodb://{username}:{password}@{self.mongodb_host}:{self.mongodb_port}"
        )

    @property
    def telemetry_enabled(self) -> bool:
        """
        Whether telemetry is configured. Inferred based on whether the
        environment contains an endpoint to report to.
        """
        return bool(self.otel_exporter_otlp_endpoint)
