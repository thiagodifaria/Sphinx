# src/sphinx/infrastructure/tui/screens/dashboard_screen.py

from __future__ import annotations
from datetime import datetime, timedelta

from dependency_injector.wiring import Provide, inject
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import Header, Footer

from src.sphinx.core.application.use_cases.apply_infrastructure_changes import ApplyInfrastructureChangesUseCase
from src.sphinx.core.application.use_cases.create_optimization_plan import CreateOptimizationPlanUseCase
from src.sphinx.core.application.use_cases.record_action import RecordActionUseCase
from src.sphinx.core.domain.models.history import ActionRecord
from src.sphinx.core.domain.models.optimization import OptimizationOpportunity
from src.sphinx.infrastructure.di.containers import Container
from src.sphinx.infrastructure.tui.widgets.opportunities_panel import OpportunitiesPanel
from src.sphinx.infrastructure.tui.widgets.solution_viewer import SolutionViewer

EXAMPLE_QUERIES = ["rate(process_cpu_seconds_total[1m])"]


class DashboardScreen(Screen):
    """
    Dashboard interativo que permite visualizar e aplicar soluções de otimização.
    """
    opportunities: list[OptimizationOpportunity] = []
    # Armazena a oportunidade atualmente em visualização
    selected_opportunity: OptimizationOpportunity | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="dashboard-container"):
            yield OpportunitiesPanel(id="opportunities-panel")
            yield SolutionViewer(id="solution-viewer")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(SolutionViewer).show_opportunity(None)
        self.update_data()
        self.set_interval(60.0, self.update_data)

    def on_opportunities_panel_opportunity_selected(
        self, message: OpportunitiesPanel.OpportunitySelected
    ) -> None:
        self.selected_opportunity = message.opportunity
        self.query_one(SolutionViewer).show_opportunity(message.opportunity)

    @inject
    async def on_solution_viewer_apply_solution(
        self,
        message: SolutionViewer.ApplySolution,
        apply_changes_uc: ApplyInfrastructureChangesUseCase = Provide[Container.use_cases.apply_infrastructure_changes],
        record_action_uc: RecordActionUseCase = Provide[Container.use_cases.record_action],
    ) -> None:
        """Ouve o evento 'Aplicar' e orquestra a aplicação e o registro da ação."""
        self.notify("Aplicando a solução sugerida...", title="Operação em Andamento", severity="information")
        result = await apply_changes_uc.execute(message.iac_to_apply)
        
        if result.success and self.selected_opportunity:
            self.notify("Solução aplicada com sucesso!", title="Sucesso", severity="success")
            
            # Cria e registra a ação no histórico
            action_record = ActionRecord(
                opportunity_id=self.selected_opportunity.id,
                resource_address=self.selected_opportunity.resource_address,
                opportunity_title=self.selected_opportunity.title,
                applied_iac_content=message.iac_to_apply.content
            )
            await record_action_uc.execute(action_record)
            
            self.query_one(SolutionViewer).show_opportunity(None)
            await self.update_data()
        else:
            self.notify(f"Falha ao aplicar a solução. Verifique os logs.", title="Erro", severity="error")

    @inject
    async def update_data(
        self,
        create_opt_plan_uc: CreateOptimizationPlanUseCase = Provide[Container.use_cases.create_optimization_plan],
    ) -> None:
        """Busca, analisa e exibe os dados de otimização."""
        panel = self.query_one(OpportunitiesPanel)
        panel.update_opportunities([])
        
        self.opportunities = await create_opt_plan_uc.execute(queries=EXAMPLE_QUERIES)

        panel.update_opportunities(self.opportunities)