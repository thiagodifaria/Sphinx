from __future__ import annotations
import logging
from datetime import datetime

from dependency_injector.wiring import Provide, inject
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Static, LoadingIndicator

from app.core.application.use_cases.apply_changes import (
    ApplyInfrastructureChangesUseCase,
)
from app.core.application.use_cases.build_config import BuildTerraformConfigUseCase
from app.core.application.use_cases.record_action import RecordActionUseCase
from app.core.application.use_cases.run_analysis import RunAnalysisCycleUseCase
from app.core.domain.models.history import ActionRecord
from app.core.domain.models.optimization import OptimizationOpportunity
from app.infrastructure.di.containers import Container
from app.infrastructure.tui.widgets.metric_chart import MetricChart
from app.infrastructure.tui.widgets.opportunities import Opportunities
from app.infrastructure.tui.widgets.solution import Solution

logger = logging.getLogger(__name__)


class DashboardScreen(Static):
    """Uma tela que representa o conteúdo da aba de Dashboard."""

    opportunities: list[OptimizationOpportunity] = []
    selected_opportunity: OptimizationOpportunity | None = None

    @inject
    def __init__(
        self,
        apply_changes_uc: ApplyInfrastructureChangesUseCase = Provide[
            Container.apply_infrastructure_changes_uc
        ],
        record_action_uc: RecordActionUseCase = Provide[Container.record_action_uc],
        create_opt_plan_uc: RunAnalysisCycleUseCase = Provide[
            Container.create_optimization_plan_uc
        ],
        build_config_uc: BuildTerraformConfigUseCase = Provide[
            Container.build_config_uc
        ],
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.apply_changes_uc = apply_changes_uc
        self.record_action_uc = record_action_uc
        self.create_opt_plan_uc = create_opt_plan_uc
        self.build_config_uc = build_config_uc

    def compose(self) -> ComposeResult:
        yield LoadingIndicator(id="dashboard-loading-indicator")
        with Horizontal(id="dashboard-content-container"):
            with Vertical(id="left-column"):
                yield Opportunities(id="opportunities-panel")
                yield MetricChart(id="metric-chart-panel")
            yield Solution(id="solution-viewer")

    def on_mount(self) -> None:
        self.query_one(Solution).show_opportunity(None)
        self.query_one(MetricChart).metric = None
        self.run_worker(self.update_data())
        self.set_interval(60.0, self.update_data)

    def on_opportunities_opportunity_selected(
        self, message: Opportunities.OpportunitySelected
    ) -> None:
        """Chamado quando o widget Opportunities emite uma mensagem de seleção."""
        self.selected_opportunity = message.opportunity
        self.query_one(Solution).show_opportunity(message.opportunity)

        metric_chart = self.query_one(MetricChart)
        if message.opportunity and message.opportunity.evidence:
            metric_chart.metric = message.opportunity.evidence[0]
        else:
            metric_chart.metric = None

    async def on_solution_apply_solution(
        self, message: Solution.ApplySolution
    ) -> None:
        """Chamado quando o widget Solution emite uma mensagem para aplicar a solução."""
        if not self.selected_opportunity:
            logger.error("Nenhuma oportunidade selecionada para aplicar a solução.")
            return

        tf_config = self.build_config_uc.execute(main_file=message.iac_to_apply)

        logger.info(f"Iniciando aplicação para '{self.selected_opportunity.title}'...")
        result = await self.apply_changes_uc.execute(tf_config)

        if result.success:
            logger.info("Solução aplicada com sucesso!")
            action_record = ActionRecord(
                opportunity_id=self.selected_opportunity.id,
                applied_at=datetime.utcnow(),
                resource_address=self.selected_opportunity.resource_address,
                opportunity_title=self.selected_opportunity.title,
                applied_iac_content=message.iac_to_apply.content,
            )
            await self.record_action_uc.execute(action_record)
            self.query_one(Solution).show_opportunity(None)
            await self.update_data()
        else:
            logger.error(f"Falha ao aplicar a solução. Saída: {result.raw_output}")

    async def update_data(self) -> None:
        content_container = self.query_one("#dashboard-content-container")
        loading_spinner = self.query_one("#dashboard-loading-indicator")

        content_container.display = False
        loading_spinner.display = True

        logger.info("A atualizar o dashboard em busca de novas oportunidades...")
        self.opportunities = await self.create_opt_plan_uc.execute()
        logger.info(
            f"Análise concluída. {len(self.opportunities)} oportunidade(s) encontrada(s)."
        )

        panel = self.query_one(Opportunities)
        panel.update_opportunities(self.opportunities)

        loading_spinner.display = False
        content_container.display = True