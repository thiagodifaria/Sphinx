# src/sphinx/infrastructure/config/settings.py

from __future__ import annotations

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Centraliza as configurações da aplicação, com validação e tipagem do Pydantic.

    Este modelo carrega automaticamente as configurações de variáveis de ambiente
    ou de um arquivo .env, garantindo que a aplicação inicie apenas com os
    parâmetros necessários e válidos. O uso de SecretStr protege valores
    sensíveis de serem expostos em logs.
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