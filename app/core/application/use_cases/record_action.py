from __future__ import annotations

from app.core.application.ports.gateways import HistoryRepositoryPort
from app.core.domain.models.history import ActionRecord


class RecordActionUseCase:
    """Orquestra o registo de uma ação no histórico da aplicação."""

    def __init__(self, history_repository: HistoryRepositoryPort) -> None:
        self._history_repository = history_repository

    async def execute(self, record: ActionRecord) -> None:
        """
        Executa o caso de uso para salvar um registo de ação.

        Args:
            record: O registo da ação a ser salvo.
        """
        await self._history_repository.add_record(record)