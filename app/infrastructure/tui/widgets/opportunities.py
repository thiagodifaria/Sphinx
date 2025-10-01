from __future__ import annotations

from rich.text import Text
from textual.containers import Vertical
from textual.message import Message
from textual.widgets import DataTable
import uuid

from app.core.domain.models.optimization import OptimizationOpportunity


class Opportunities(Vertical):
    """Um widget para exibir e selecionar oportunidades de otimização."""

    BORDER_TITLE = "Oportunidades de Otimização"

    class OpportunitySelected(Message):
        """Mensagem emitida quando uma oportunidade é selecionada na tabela."""

        def __init__(self, opportunity: OptimizationOpportunity | None) -> None:
            self.opportunity = opportunity
            super().__init__()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._opportunities: list[OptimizationOpportunity] = []

    def compose(self) -> None:
        yield DataTable(id="opportunities_table", cursor_type="row", zebra_stripes=True)

    def on_mount(self) -> None:
        """Adiciona as colunas à tabela e exibe o estado inicial."""
        table = self.query_one(DataTable)
        table.add_column("Recurso", key="resource", width=20)
        table.add_column("Oportunidade", key="opportunity")
        self.update_opportunities([])

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Emite a mensagem OpportunitySelected quando uma linha é selecionada."""
        selected_id = event.row_key.value
        if selected_id:
            found_op = next(
                (op for op in self._opportunities if str(op.id) == selected_id), None
            )
            self.post_message(self.OpportunitySelected(found_op))
        else:
            self.post_message(self.OpportunitySelected(None))

    def on_data_table_cleared(self, event: DataTable.Cleared) -> None:
        """Emite uma mensagem para limpar a seleção quando a tabela é limpa."""
        self.post_message(self.OpportunitySelected(None))

    def update_opportunities(self, opportunities: list[OptimizationOpportunity]) -> None:
        """Atualiza a tabela com uma nova lista de oportunidades."""
        self._opportunities = opportunities
        table = self.query_one(DataTable)
        table.clear()

        if not opportunities:
            table.add_row(Text("Nenhuma oportunidade detetada...", style="dim"))
            return

        for op in opportunities:
            table.add_row(
                Text(op.resource_address, style="bold cyan", overflow="ellipsis"),
                Text(op.title, style="yellow", no_wrap=False),
                key=str(op.id),
            )