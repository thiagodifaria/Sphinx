from __future__ import annotations

from rich.text import Text
from textual.containers import VerticalScroll, Horizontal
from textual.message import Message
from textual.widgets import Button, Markdown, Static

from app.core.domain.models.iac import IaCFile
from app.core.domain.models.optimization import OptimizationOpportunity


class Solution(Static):
    """Um widget para exibir os detalhes de uma solução e permitir a sua aplicação."""

    BORDER_TITLE = "Detalhes da Solução"

    class ApplySolution(Message):
        """Mensagem emitida quando o utilizador decide aplicar a solução."""

        def __init__(self, iac_to_apply: IaCFile) -> None:
            self.iac_to_apply = iac_to_apply
            super().__init__()

    def compose(self) -> None:
        with VerticalScroll(id="solution-scroll-container"):
            yield Static("[bold]Título:[/bold]", classes="label")
            yield Static(id="sv-title", markup=False)

            yield Horizontal(classes="separator")
            yield Static("[bold]Descrição do Problema:[/bold]", classes="label")
            yield Static(id="sv-description", markup=False)

            yield Horizontal(classes="separator")
            yield Static("[bold]Análise de Impacto:[/bold]", classes="label")
            yield Static(id="sv-impact", markup=False)

            yield Horizontal(classes="separator")
            yield Static("[bold]Arquivo de Solução Sugerido:[/bold]", classes="label")
            yield Markdown(id="sv-diff-view")

            yield Button(
                "Aplicar esta Solução",
                variant="success",
                id="apply-solution-button",
                disabled=True,
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Emite a mensagem ApplySolution quando o botão é pressionado."""
        if (
            event.button.id == "apply-solution-button"
            and self.current_opportunity
            and self.current_opportunity.suggested_change
        ):
            if iac_file := self.current_opportunity.suggested_change.suggested_iac_file:
                self.post_message(self.ApplySolution(iac_file))

    def show_opportunity(self, opportunity: OptimizationOpportunity | None) -> None:
        """Atualiza o painel para exibir os detalhes de uma oportunidade."""
        self.current_opportunity = opportunity
        container = self.query_one("#solution-scroll-container")

        is_visible = opportunity is not None
        container.set_class(not is_visible, "hidden")

        apply_button = self.query_one(Button)
        if not opportunity or not opportunity.suggested_change:
            apply_button.disabled = True
            self.query_one("#sv-title").update(
                Text("Selecione uma oportunidade na lista à esquerda.", style="dim")
            )
            self.query_one("#sv-description").update("-")
            self.query_one("#sv-impact").update("-")
            self.query_one(Markdown).update("")
            return

        self.query_one("#sv-title").update(opportunity.title)
        self.query_one("#sv-description").update(opportunity.description)

        change = opportunity.suggested_change
        self.query_one("#sv-impact").update(change.impact_assessment)

        code_markdown = f"```terraform\n{change.suggested_iac_file.content}\n```"
        self.query_one(Markdown).update(code_markdown)

        apply_button.disabled = "error.tf" in change.suggested_iac_file.filename