# src/sphinx/infrastructure/tui/widgets/opportunities_panel.py

from __future__ import annotations

from textual.message import Message
from textual.widgets import DataTable, Static

from src.sphinx.core.domain.models.optimization import OptimizationOpportunity


class OpportunitiesPanel(Static):
    """Um widget para exibir e selecionar oportunidades de otimização."""

    class OpportunitySelected(Message):
        """Mensagem emitida quando uma oportunidade é selecionada na tabela."""
        def __init__(self, opportunity: OptimizationOpportunity) -> None:
            self.opportunity = opportunity
            super().__init__()

    def compose(self):
        yield DataTable(id="opportunities_table", cursor_type="row")

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("Recurso", "Oportunidade")

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Quando uma linha é selecionada, emite a mensagem com o objeto de domínio."""
        if event.data_row:
            opportunity_obj = event.data_row.get("opportunity_obj")
            if opportunity_obj:
                self.post_message(self.OpportunitySelected(opportunity_obj))

    def update_opportunities(self, opportunities: list[OptimizationOpportunity]) -> None:
        table = self.query_one(DataTable)
        table.clear()
        
        if not opportunities:
            table.add_row("[dim]Nenhuma oportunidade detectada...[/dim]", "")
            return

        for op in opportunities:
            # Armazena o objeto de domínio completo na linha da tabela para uso posterior.
            table.add_row(
                f"[bold cyan]{op.resource_address}[/bold cyan]",
                f"[yellow]{op.title}[/yellow]",
                key=str(op.id),
                data={"opportunity_obj": op}
            )