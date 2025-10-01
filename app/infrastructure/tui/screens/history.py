from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from textual.app import ComposeResult
from textual.widgets import DataTable, Static
from rich.text import Text

from app.core.application.use_cases.view_history import ViewHistoryUseCase
from app.infrastructure.di.containers import Container


class HistoryScreen(Static):
    """Um ecrã que exibe o histórico de ações de otimização aplicadas."""

    @inject
    def __init__(
        self,
        view_history_uc: ViewHistoryUseCase = Provide[Container.view_history_uc],
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.view_history_uc = view_history_uc

    def compose(self) -> ComposeResult:
        yield DataTable(id="history-table", cursor_type="row", zebra_stripes=True)

    async def on_mount(self) -> None:
        """Busca os dados do histórico e popula a tabela quando o ecrã é montado."""
        table = self.query_one(DataTable)
        table.border_title = "Histórico de Ações Aplicadas"
        table.add_columns("Data/Hora (UTC)", "Recurso", "Ação Realizada")
        await self.update_history()

    async def update_history(self) -> None:
        """Busca e exibe os registos de histórico mais recentes na tabela."""
        table = self.query_one(DataTable)
        table.clear()

        history_records = await self.view_history_uc.execute()

        if not history_records:
            table.add_row(Text("Nenhuma ação registada ainda.", style="dim"))
            return

        for record in history_records:
            table.add_row(
                record.applied_at.strftime("%Y-%m-%d %H:%M:%S"),
                Text(record.resource_address, style="cyan"),
                Text(record.opportunity_title, style="yellow"),
            )