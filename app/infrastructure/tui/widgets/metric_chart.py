from __future__ import annotations

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.reactive import reactive
from textual.widgets import Label, Static

from app.core.domain.models.observability import Metric


class MetricChart(Static):
    """Um widget para exibir uma única métrica como um gráfico sparkline."""

    BORDER_TITLE = "Evidência da Métrica"
    SPARKLINE_CHARS = " ▂▃▄▅▆▇█"

    metric: reactive[Metric | None] = reactive(None)

    def compose(self) -> ComposeResult:
        with Vertical(id="metric-chart-container"):
            yield Label(id="metric-title")
            yield Static(
                id="sparkline",
                renderable=Text(
                    "Selecione uma oportunidade para ver a métrica.", style="dim"
                ),
            )

    def watch_metric(self, new_metric: Metric | None) -> None:
        """Chamado quando a propriedade 'metric' é atualizada com novos dados."""
        title_label = self.query_one("#metric-title", Label)
        sparkline_widget = self.query_one("#sparkline", Static)

        if not new_metric:
            title_label.update("")
            sparkline_widget.update(
                Text("Selecione uma oportunidade para ver a métrica.", style="dim")
            )
            return

        labels = ", ".join(f"{k}='{v}'" for k, v in new_metric.labels.items())
        title = f"[bold]{new_metric.name}[/bold] {{{labels}}}"
        title_label.update(title)

        if not new_metric.datapoints:
            sparkline_widget.update(
                Text("Métrica sem dados de série temporal.", style="dim")
            )
            return

        values = [dp.value for dp in new_metric.datapoints]
        sparkline = self._generate_sparkline(values)
        sparkline_widget.update(Text(sparkline, style="green"))

    def _generate_sparkline(self, values: list[float]) -> str:
        """Normaliza os valores e converte-os em caracteres sparkline."""
        if not values:
            return ""
        min_val, max_val = min(values), max(values)
        value_range = max_val - min_val

        if value_range == 0:
            char_index = len(self.SPARKLINE_CHARS) // 2
            return self.SPARKLINE_CHARS[char_index] * len(values)

        def get_char(val: float) -> str:
            index = int(
                ((val - min_val) / value_range) * (len(self.SPARKLINE_CHARS) - 1)
            )
            return self.SPARKLINE_CHARS[index]

        return "".join(get_char(v) for v in values)