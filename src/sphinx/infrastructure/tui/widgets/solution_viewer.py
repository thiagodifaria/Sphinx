# src/sphinx/infrastructure/tui/widgets/solution_viewer.py

from __future__ import annotations

from textual.containers import VerticalScroll
from textual.message import Message
from textual.widgets import Button, Label, Markdown, Static

from src.sphinx.core.domain.models.iac import IaCFile
from src.sphinx.core.domain.models.optimization import OptimizationOpportunity


class SolutionViewer(Static):
    """
    Um widget para exibir os detalhes de uma solução e permitir sua aplicação.
    """

    class ApplySolution(Message):
        """Mensagem emitida quando o usuário decide aplicar a solução."""
        def __init__(self, iac_to_apply: IaCFile) -> None:
            self.iac_to_apply = iac_to_apply
            super().__init__()

    def compose(self):
        with VerticalScroll():
            yield Label("[bold]Detalhes da Oportunidade[/bold]", id="sv-title")
            yield Static(id="sv-description", markup=False)
            yield Label("\n[bold]Análise de Impacto[/bold]", id="sv-impact-label")
            yield Static(id="sv-impact", markup=False)
            yield Label("\n[bold]Arquivo Sugerido[/bold]", id="sv-diff-label")
            yield Markdown(id="sv-diff")
            yield Button(
                "Aplicar esta Solução",
                variant="success",
                id="apply-solution-button",
                disabled=True
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Emite a mensagem para aplicar a solução quando o botão é pressionado."""
        if event.button.id == "apply-solution-button" and self.current_opportunity:
            if iac_file := self.current_opportunity.suggested_change.suggested_iac_file:
                self.post_message(self.ApplySolution(iac_file))

    def show_opportunity(self, opportunity: OptimizationOpportunity | None) -> None:
        """Atualiza o painel para exibir os detalhes de uma oportunidade."""
        self.current_opportunity = opportunity
        is_visible = opportunity is not None
        self.set_class(not is_visible, "hidden")

        apply_button = self.query_one(Button)
        if not opportunity or not opportunity.suggested_change:
            apply_button.disabled = True
            return

        self.query_one("#sv-title").update(f"[bold]{opportunity.title}[/bold]")
        self.query_one("#sv-description").update(opportunity.description)

        change = opportunity.suggested_change
        self.query_one("#sv-impact").update(change.impact_assessment)
        
        # Exibe o conteúdo completo do arquivo sugerido em um bloco de código Terraform.
        code_markdown = f"```terraform\n{change.suggested_iac_file.content}\n```"
        self.query_one(Markdown).update(code_markdown)
        
        # Habilita o botão apenas se houver um arquivo válido para aplicar.
        apply_button.disabled = "error.tf" in change.suggested_iac_file.filename