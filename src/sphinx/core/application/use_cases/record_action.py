# src/sphinx/core/application/use_cases/record_action.py

from __future__ import annotations

from src.sphinx.core.application.ports.gateways.history import HistoryRepositoryPort
from src.sphinx.core.domain.models.history import ActionRecord


class RecordActionUseCase:
    """Orquestra o registro de uma ação no histórico da aplicação."""

    def __init__(self, history_repository: HistoryRepositoryPort) -> None:
        self._history_repository = history_repository

    async def execute(self, record: ActionRecord) -> None:
        """
        Executa o caso de uso para salvar um registro de ação.

        Args:
            record: O registro da ação a ser salvo.
        """
        await self._history_repository.add_record(record)