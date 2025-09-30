# src/sphinx/infrastructure/tui/widgets/opportunities_panel.py

from __future__ import annotations

from rich.text import Text
from textual.containers import Vertical
from textual.message import Message
from textual.widgets import DataTable
import uuid

from app.core.domain.models.optimization import OptimizationOpportunity


class OpportunitiesPanel(Vertical):
    """
    Um widget de painel para exibir e selecionar oportunidades de otimização,
    completo com borda e título.
    """

    BORDER_TITLE = "Oportunidades de Otimização"

    class OpportunitySelected(Message):
        """Mensagem emitida quando uma oportunidade é selecionada na tabela."""
        def __init__(self, opportunity: OptimizationOpportunity | None) -> None:
            self.opportunity = opportunity
            super().__init__()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._opportunities: list[OptimizationOpportunity] = []

    def compose(self):
        # Adicionamos linhas zebradas para melhor legibilidade
        yield DataTable(id="opportunities_table", cursor_type="row", zebra_stripes=True)

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        # A coluna "Recurso" terá um tamanho fixo, a "Oportunidade" será flexível
        table.add_column("Recurso", key="resource", width=20)
        table.add_column("Oportunidade", key="opportunity")
        self.update_opportunities([]) # Mostra a mensagem inicial

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Quando uma linha é selecionada, encontra o objeto de domínio e emite a mensagem."""
        selected_id = event.row_key.value
        if selected_id:
            # Encontra a oportunidade correspondente na nossa lista interna pelo ID
            found_op = next((op for op in self._opportunities if str(op.id) == selected_id), None)
            self.post_message(self.OpportunitySelected(found_op))
        else:
            self.post_message(self.OpportunitySelected(None))

    def on_data_table_cleared(self, event: DataTable.Cleared) -> None:
        """Quando a tabela é limpa, emite uma mensagem para limpar o painel de solução."""
        self.post_message(self.OpportunitySelected(None))

    def update_opportunities(self, opportunities: list[OptimizationOpportunity]) -> None:
        self._opportunities = opportunities  # Armazena a lista de oportunidades
        table = self.query_one(DataTable)
        table.clear()
        
        if not opportunities:
            table.add_row(Text("Nenhuma oportunidade detectada...", style="dim"))
            return

        for op in opportunities:
            table.add_row(
                Text(op.resource_address, style="bold cyan", overflow="ellipsis"),
                Text(op.title, style="yellow", no_wrap=False), # no_wrap=False permite a quebra de linha
                key=str(op.id)
            )