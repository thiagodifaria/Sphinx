# src/sphinx/infrastructure/tui/screens/chat_screen.py

from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, RichLog

from src.sphinx.core.application.use_cases.apply_infrastructure_changes import ApplyInfrastructureChangesUseCase
from src.sphinx.core.application.use_cases.create_execution_plan import CreateExecutionPlanUseCase
from src.sphinx.core.application.use_cases.generate_iac import GenerateIacUseCase
from src.sphinx.core.domain.models.iac import ApplyResult, ExecutionPlan, IaCFile
from src.sphinx.infrastructure.di.containers import Container as DIContainer


class ChatScreen(Screen):
    BINDINGS = [("q", "quit", "Sair")]
    
    _current_iac_file: reactive[IaCFile | None] = reactive(None)
    _plan_successful: reactive[bool] = reactive(False)

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="main-container"):
            yield RichLog(id="log", wrap=True, highlight=True)
            with Horizontal(id="button-container"):
                yield Button("Planejar (Plan)", id="plan-button", disabled=True)
                yield Button("Aplicar (Apply)", id="apply-button", disabled=True, variant="success")
            yield Input(placeholder="Descreva a infraestrutura que você precisa...")
        yield Footer()

    def watch__current_iac_file(self, new_iac_file: IaCFile | None) -> None:
        """Habilita o botão 'Plan' se houver um arquivo IaC, e reseta o estado 'Apply'."""
        self.query_one("#plan-button", Button).disabled = new_iac_file is None
        self._plan_successful = False

    def watch__plan_successful(self, can_apply: bool) -> None:
        """Habilita o botão 'Apply' somente se o plano foi bem-sucedido."""
        self.query_one("#apply-button", Button).disabled = not can_apply

    @inject
    async def on_input_submitted(
        self,
        message: Input.Submitted,
        generate_iac_uc: GenerateIacUseCase = Provide[DIContainer.use_cases.generate_iac],
    ) -> None:
        """Lida com a submissão de um novo prompt para gerar IaC."""
        self._current_iac_file = None
        prompt = message.value
        log, input_widget = self.query_one(RichLog), self.query_one(Input)

        log.write(f"> {prompt}")
        input_widget.clear()
        log.write("[bold cyan]Sphinx está gerando o código...[/bold cyan]")
        self._current_iac_file = await generate_iac_uc.execute(prompt=prompt)
        
        formatted_code = f"[bold yellow]Arquivo: {self._current_iac_file.filename}[/bold yellow]\n\n"
        formatted_code += f"```terraform\n{self._current_iac_file.content}\n```"
        log.write(formatted_code)

    @inject
    async def on_button_pressed(
        self,
        event: Button.Pressed,
        create_plan_uc: CreateExecutionPlanUseCase = Provide[DIContainer.use_cases.create_execution_plan],
        apply_changes_uc: ApplyInfrastructureChangesUseCase = Provide[DIContainer.use_cases.apply_infrastructure_changes],
    ) -> None:
        """Lida com os cliques nos botões 'Plan' e 'Apply'."""
        if not self._current_iac_file:
            return

        log = self.query_one(RichLog)
        
        if event.button.id == "plan-button":
            log.write("[bold cyan]Sphinx está planejando as mudanças...[/bold cyan]")
            plan = await create_plan_uc.execute(self._current_iac_file)
            self._display_plan(plan)
            # Habilita o botão Apply se o plano não contiver erros
            self._plan_successful = "Erro no Terraform" not in plan.raw_output

        elif event.button.id == "apply-button" and self._plan_successful:
            log.write("[bold magenta]Sphinx está aplicando as mudanças...[/bold magenta]")
            result = await apply_changes_uc.execute(self._current_iac_file)
            self._display_apply_result(result)
            self._current_iac_file = None  # Reseta o estado para um novo ciclo

    def _display_plan(self, plan: ExecutionPlan) -> None:
        log = self.query_one(RichLog)
        # ... (código de exibição do plano permanece o mesmo da Fase 2.1)
        summary = [f"[green]+ {c.address}" for c in plan.changes if c.action == "create"]
        if not summary and "No changes" in plan.raw_output:
            log.write("[bold green]Nenhuma mudança necessária.[/bold green]")
        else:
            log.write(f"\n[bold]Saída do Plano:[/bold]\n```\n{plan.raw_output}\n```")

    def _display_apply_result(self, result: ApplyResult) -> None:
        """Formata e exibe o resultado da operação 'apply' na TUI."""
        log = self.query_one(RichLog)
        if result.success:
            log.write("[bold green]Mudanças aplicadas com sucesso![/bold green]")
        else:
            log.write("[bold red]Falha ao aplicar as mudanças.[/bold red]")
        
        log.write(f"\n[bold]Saída do Apply:[/bold]\n```\n{result.raw_output}\n```")