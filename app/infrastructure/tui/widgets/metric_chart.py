from __future__ import annotations
from datetime import datetime

from rich.table import Table
from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widgets import Static

from app.core.domain.models.observability import Metric


class MetricChart(Static):
    """Um widget para exibir uma unica metrica como uma tabela."""

    BORDER_TITLE = "Evidencia da Metrica"

    metric: reactive[Metric | None] = reactive(None)

    def compose(self) -> ComposeResult:
        yield Static(id="metric_plot_static")

    def watch_metric(self, new_metric: Metric | None) -> None:
        """Chamado quando a propriedade 'metric' e atualizada com novos dados."""
        plot_static = self.query_one("#metric_plot_static", Static)

        if not new_metric or not new_metric.datapoints:
            self.border_title = "Evidencia da Metrica"
            plot_static.update("\n\n   Selecione uma oportunidade para ver a metrica.")
            return

        labels_str = ", ".join(f"{k}='{v}'" for k, v in new_metric.labels.items())
        self.border_title = f"{new_metric.name} {{{labels_str}}}"

        table = Table(show_header=True, header_style="bold cyan", expand=True)
        table.add_column("Timestamp", style="dim", width=20)
        table.add_column("Value", justify="right")
        table.add_column("Graph", width=40)

        if not new_metric.datapoints:
            plot_static.update(table)
            return

        values = [dp.value for dp in new_metric.datapoints]
        max_val = max(values) if values else 1
        min_val = min(values) if values else 0
        value_range = max_val - min_val if max_val != min_val else 1

        for dp in new_metric.datapoints[-10:]:
            timestamp_str = dp.timestamp.strftime("%H:%M:%S")
            value_str = f"{dp.value:.4f}"
            
            normalized = (dp.value - min_val) / value_range
            bar_length = int(normalized * 30)
            bar = "█" * bar_length
            
            table.add_row(timestamp_str, value_str, bar)

        plot_static.update(table)