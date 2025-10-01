from __future__ import annotations

from app.core.application.ports.gateways import HistoryRepositoryPort
from app.core.domain.models.history import ActionRecord


class ViewHistoryUseCase:
    """Orquestra a busca e apresentação do histórico de ações."""

    def __init__(self, history_repository: HistoryRepositoryPort) -> None:
        self._history_repository = history_repository

    async def execute(self) -> list[ActionRecord]:
        """
        Executa o caso de uso para buscar todo o histórico de ações.
        """
        return await self._history_repository.get_all_records()