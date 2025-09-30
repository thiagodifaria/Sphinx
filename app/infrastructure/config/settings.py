# src/sphinx/infrastructure/config/settings.py

from __future__ import annotations

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Centraliza as configurações da aplicação, com validação e tipagem do Pydantic.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Configurações de API e Serviços
    google_api_key: SecretStr = Field(..., alias="GOOGLE_API_KEY")
    prometheus_url: str = Field(..., alias="PROMETHEUS_URL")
    
    # Configurações de Banco de Dados
    sqlite_db_path: str = Field("sphinx.db", alias="SQLITE_DB_PATH")

    # Configurações do Terraform Backend
    tf_backend_s3_bucket: str | None = Field(default=None, alias="TF_BACKEND_S3_BUCKET")
    tf_backend_s3_key: str | None = Field(default=None, alias="TF_BACKEND_S3_KEY")
    tf_backend_s3_region: str | None = Field(default=None, alias="TF_BACKEND_S3_REGION")

    # Configuração do arquivo de regras e do diretório de plugins
    rules_file_path: str = Field("rules.yml", alias="RULES_FILE_PATH")
    plugins_dir: str = Field("plugins", alias="PLUGINS_DIR")