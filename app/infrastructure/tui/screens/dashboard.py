# src/sphinx/infrastructure/tui/screens/dashboard_screen.py

from __future__ import annotations
import logging
from datetime import datetime

from dependency_injector.wiring import Provide, inject
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Static, LoadingIndicator

from app.core.application.state import AppState
from app.core.application.use_cases.apply_infrastructure_changes import ApplyInfrastructureChangesUseCase
from app.core.application.use_cases.create_optimization_plan import CreateOptimizationPlanUseCase
from app.core.application.use_cases.record_action import RecordActionUseCase
from app.core.domain.models.history import ActionRecord
from app.core.domain.models.iac import TerraformBackendConfig, TerraformConfiguration
from app.core.domain.models.optimization import OptimizationOpportunity
from app.infrastructure.config.settings import Settings
from app.infrastructure.di.containers import Container
from app.infrastructure.tui.widgets.opportunities_panel import OpportunitiesPanel
from app.infrastructure.tui.widgets.solution_viewer import SolutionViewer
from app.infrastructure.tui.widgets.metric_chart import MetricChart # Importamos o novo widget

logger = logging.getLogger(__name__)


class DashboardScreen(Static):
    """Um widget que representa o conteúdo da aba de Dashboard."""

    opportunities: list[OptimizationOportunidade] = []
    selected_opportunity: OptimizationOpportunity | None = None

    @inject
    def __init__(
        self,
        apply_changes_uc: ApplyInfrastructureChangesUseCase = Provide[Container.apply_infrastructure_changes_uc],
        record_action_uc: RecordActionUseCase = Provide[Container.record_action_uc],
        create_opt_plan_uc: CreateOptimizationPlanUseCase = Provide[Container.create_optimization_plan_uc],
        settings: Settings = Provide[Container.settings],
        app_state: AppState = Provide[Container.app_state],
        *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.apply_changes_uc = apply_changes_uc
        self.record_action_uc = record_action_uc
        self.create_opt_plan_uc = create_opt_plan_uc
        self.settings = settings
        self.app_state = app_state


    def compose(self) -> ComposeResult:
        """Compõe a UI com um layout de duas colunas e um indicador de carregamento."""
        yield LoadingIndicator(id="dashboard-loading-indicator")
        with Horizontal(id="dashboard-content-container"):
            # A coluna da esquerda agora é um contêiner vertical
            with Vertical(id="left-column"):
                yield OpportunitiesPanel(id="opportunities-panel")
                yield MetricChart(id="metric-chart-panel")
            yield SolutionViewer(id="solution-viewer")

    def on_mount(self) -> None:
        self.query_one(SolutionViewer).show_opportunity(None)
        self.query_one(MetricChart).metric = None # Limpa o gráfico inicial
        self.run_worker(self.update_data())
        self.set_interval(60.0, self.update_data)

    def on_opportunities_panel_opportunity_selected(self, message: OpportunitiesPanel.OpportunitySelected) -> None:
        self.selected_opportunity = message.opportunity
        self.query_one(SolutionViewer).show_opportunity(message.opportunity)
        
        # Atualiza o gráfico com a primeira métrica de evidência, se houver
        metric_chart = self.query_one(MetricChart)
        if message.opportunity and message.opportunity.evidence:
            metric_chart.metric = message.opportunity.evidence[0]
        else:
            metric_chart.metric = None

    async def on_solution_viewer_apply_solution(self, message: SolutionViewer.ApplySolution) -> None:
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
        
        if not self.selected_opportunity:
            logger.error("Nenhuma oportunidade selecionada para aplicar a solução.")
            return

        tf_config = TerraformConfiguration(
            main_file=message.iac_to_apply,
            backend_config=backend_config
        )

        logger.info(f"Iniciando aplicação para '{self.selected_opportunity.title}'...")
        result = await self.apply_changes_uc.execute(tf_config)
        
        if result.success:
            logger.info("Solução aplicada com sucesso!")
            action_record = ActionRecord(
                opportunity_id=self.selected_opportunity.id,
                applied_at=datetime.utcnow(),
                resource_address=self.selected_opportunity.resource_address,
                opportunity_title=self.selected_opportunity.title,
                applied_iac_content=message.iac_to_apply.content
            )
            await self.record_action_uc.execute(action_record)
            self.query_one(SolutionViewer).show_opportunity(None)
            await self.update_data()
        else:
            logger.error(f"Falha ao aplicar a solução. Saída: {result.raw_output}")

    async def update_data(self) -> None:
        """Busca por oportunidades e atualiza a UI, mostrando um spinner durante o processo."""
        content_container = self.query_one("#dashboard-content-container")
        loading_spinner = self.query_one("#dashboard-loading-indicator")
        
        content_container.display = False
        loading_spinner.display = True
        
        logger.info("Atualizando o dashboard em busca de novas oportunidades...")
        self.opportunities = await self.create_opt_plan_uc.execute()
        logger.info(f"Análise concluída. {len(self.opportunities)} oportunidade(s) encontrada(s).")

        panel = self.query_one(OpportunitiesPanel)
        panel.update_opportunities(self.opportunities)
        
        loading_spinner.display = False
        content_container.display = True