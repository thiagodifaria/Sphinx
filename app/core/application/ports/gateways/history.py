# src/sphinx/core/application/ports/gateways/history.py

from __future__ import annotations
from abc import ABC, abstractmethod

from app.core.domain.models.history import ActionRecord


class HistoryRepositoryPort(ABC):
    """
    Define o contrato para um repositório de persistência de histórico.
    """

    @abstractmethod
    async def initialize(self) -> None:
        """Garante que o armazenamento de dados (tabelas, etc.) está pronto."""
        raise NotImplementedError

    @abstractmethod
    async def add_record(self, record: ActionRecord) -> None:
        """
        Adiciona um novo registro de ação ao histórico.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_all_records(self) -> list[ActionRecord]:
        """
        Recupera todos os registros de ação do histórico, ordenados do mais recente para o mais antigo.
        """
        raise NotImplementedError