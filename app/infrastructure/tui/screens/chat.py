# src/sphinx/infrastructure/tui/screens/chat_screen.py

from __future__ import annotations
import logging

from dependency_injector.wiring import Provide, inject
from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.reactive import reactive
from textual.widgets import Button, Input, RichLog, Static, Markdown, LoadingIndicator

from app.core.application.state import AppState
from app.core.application.use_cases.apply_infrastructure_changes import ApplyInfrastructureChangesUseCase
from app.core.application.use_cases.create_execution_plan import CreateExecutionPlanUseCase
from app.core.application.use_cases.generate_iac import GenerateIacUseCase
from app.core.domain.models.iac import (
    IaCFile, TerraformBackendConfig, TerraformConfiguration
)
from app.infrastructure.config.settings import Settings
from app.infrastructure.di.containers import Container as DIContainer

logger = logging.getLogger(__name__)


class ChatScreen(Static):
    """Um widget que representa o conteúdo da aba de Chat."""
    
    _current_iac_file: reactive[IaCFile | None] = reactive(None)
    _plan_successful: reactive[bool] = reactive(False)
    _is_loading: reactive[bool] = reactive(False)

    @inject
    def __init__(
        self,
        generate_iac_uc: GenerateIacUseCase = Provide[DIContainer.generate_iac_uc],
        create_plan_uc: CreateExecutionPlanUseCase = Provide[DIContainer.create_execution_plan_uc],
        apply_changes_uc: ApplyInfrastructureChangesUseCase = Provide[DIContainer.apply_infrastructure_changes_uc],
        settings: Settings = Provide[DIContainer.settings],
        app_state: AppState = Provide[DIContainer.app_state],
        *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.generate_iac_uc = generate_iac_uc
        self.create_plan_uc = create_plan_uc
        self.apply_changes_uc = apply_changes_uc
        self.settings = settings
        self.app_state = app_state

    def compose(self) -> ComposeResult:
        """Compõe a interface com painéis separados para código e terminal."""
        yield LoadingIndicator(id="loading-indicator")
        
        with Static(classes="content-panel") as code_panel:
            code_panel.border_title = "Código Gerado"
            yield Markdown(id="generated-code-view")

        with Static(classes="content-panel") as terminal_panel:
            terminal_panel.border_title = "Terminal de Execução"
            yield RichLog(id="terminal-log", wrap=True, highlight=True)
            
        with Horizontal(id="button-container"):
            yield Button("Planejar (Plan)", id="plan-button", disabled=True)
            yield Button("Aplicar (Apply)", id="apply-button", disabled=True, variant="success")
        
        yield Input(placeholder="Descreva a infraestrutura que você precisa...")

    def watch__is_loading(self, loading: bool) -> None:
        """Controla a visibilidade do indicador de carregamento."""
        self.query_one(LoadingIndicator).display = loading
        self.set_class(loading, "loading")

    def watch__current_iac_file(self, new_iac_file: IaCFile | None) -> None:
        self.query_one("#plan-button", Button).disabled = new_iac_file is None
        self._plan_successful = False

    def watch__plan_successful(self, can_apply: bool) -> None:
        self.query_one("#apply-button", Button).disabled = not can_apply

    async def on_input_submitted(self, message: Input.Submitted) -> None:
        self._current_iac_file = None
        prompt = message.value
        
        code_view = self.query_one(Markdown)
        terminal_log = self.query_one("#terminal-log")
        input_widget = self.query_one(Input)

        terminal_log.clear()
        terminal_log.write(Text(f"> {prompt}"))
        input_widget.clear()

        self._is_loading = True
        terminal_log.write(Text("Sphinx está gerando o código...", style="bold cyan"))
        
        self._current_iac_file = await self.generate_iac_uc.execute(prompt=prompt)
        
        self._is_loading = False

        if self._current_iac_file:
            code_panel = self.query_one(".content-panel")
            code_panel.border_title = f"Código Gerado: {self._current_iac_file.filename}"
            
            # Adiciona a linguagem "terraform" para habilitar o syntax highlighting
            code_content = f"```terraform\n{self._current_iac_file.content}\n```"
            code_view.update(code_content)
        else:
            terminal_log.write(Text("Falha ao gerar o código.", style="bold red"))

    def _build_tf_config(self) -> TerraformConfiguration | None:
        if not self._current_iac_file:
            return None
            
        backend_config = None
        if self.app_state.active_workspace:
            backend_config = self.app_state.active_workspace.backend_config
            logger.info(f"Usando backend do workspace ativo: '{self.app_state.active_workspace.name}'")
        elif self.settings.tf_backend_s3_bucket and self.settings.tf_backend_s3_key and self.settings.tf_backend_s3_region:
            backend_config = TerraformBackendConfig(
                bucket=self.settings.tf_backend_s3_bucket,
                key=self.settings.tf_backend_s3_key,
                region=self.settings.tf_backend_s3_region
            )
            logger.info("Usando backend S3 das configurações globais (.env).")
        
        return TerraformConfiguration(
            main_file=self._current_iac_file,
            backend_config=backend_config
        )

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        tf_config = self._build_tf_config()
        if not tf_config:
            return

        terminal_log = self.query_one("#terminal-log")
        
        self.watch__plan_successful(False)
        self.query_one("#plan-button").disabled = True
        self._is_loading = True
        
        if event.button.id == "plan-button":
            terminal_log.write(Text("\nIniciando planejamento da configuração gerada...", style="bold cyan"))
            plan = await self.create_plan_uc.execute(tf_config)
            
            if "Erro no Terraform" in plan.raw_output:
                terminal_log.write(Text(plan.raw_output, style="bold red"))
            else:
                terminal_log.write(plan.raw_output)
                terminal_log.write(Text("\nPlanejamento concluído com sucesso!", style="bold green"))
            
            self._plan_successful = "Erro no Terraform" not in plan.raw_output

        elif event.button.id == "apply-button":
            terminal_log.write(Text("\nIniciando aplicação da configuração gerada...", style="bold cyan"))
            result = await self.apply_changes_uc.execute(tf_config)
            
            terminal_log.write(result.raw_output)
            if result.success:
                terminal_log.write(Text("\nAplicação concluída com sucesso!", style="bold green"))
            else:
                terminal_log.write(Text("\nFalha na aplicação.", style="bold red"))
            
            self._current_iac_file = None
        
        self._is_loading = False