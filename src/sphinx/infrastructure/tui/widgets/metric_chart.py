# src/sphinx/infrastructure/tui/widgets/metric_chart.py

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.reactive import reactive
from textual.widgets import Label, Static

from src.sphinx.core.domain.models.observability import Metric


class MetricChart(Static):
    """Um widget para exibir uma única métrica como um gráfico sparkline."""

    metric: reactive[Metric | None] = reactive(None)
    SPARKLINE_CHARS = " ▂▃▄▅▆▇█"

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label(id="title")
            yield Static(id="sparkline", renderable="Carregando...")

    def watch_metric(self, new_metric: Metric | None) -> None:
        """Chamado quando a propriedade 'metric' é atualizada com novos dados."""
        if not new_metric or not new_metric.datapoints:
            self.query_one("#title", Label).update("Métrica indisponível")
            self.query_one("#sparkline", Static).update("-")
            return

        # Monta o título do gráfico a partir do nome e labels da métrica.
        labels = ", ".join(f"{k}='{v}'" for k, v in new_metric.labels.items())
        title = f"[bold]{new_metric.name}[/bold] {{{labels}}}"
        self.query_one("#title", Label).update(title)

        # Gera o gráfico sparkline a partir dos pontos de dados.
        sparkline = self._generate_sparkline([dp.value for dp in new_metric.datapoints])
        self.query_one("#sparkline", Static).update(f"[green]{sparkline}[/green]")
    
    def _generate_sparkline(self, values: list[float]) -> str:
        """Normaliza os valores e os converte para caracteres sparkline."""
        if not values:
            return ""
        min_val, max_val = min(values), max(values)
        value_range = max_val - min_val
        
        if value_range == 0:
            return self.SPARKLINE_CHARS[len(self.SPARKLINE_CHARS) // 2] * len(values)

        def get_char(val: float) -> str:
            # Normaliza o valor para um índice dentro dos caracteres sparkline.
            index = int(((val - min_val) / value_range) * (len(self.SPARKLINE_CHARS) - 1))
            return self.SPARKLINE_CHARS[index]

        return "".join(get_char(v) for v in values)