from __future__ import annotations
from datetime import datetime, timedelta

from app.core.application.ports.gateways import LLMServicePort, RuleRepositoryPort
from app.core.application.use_cases.fetch_metrics import FetchMetricsUseCase
from app.core.domain.models.optimization import OptimizationOpportunity
from app.core.domain.services.anomalies import AnomalyDetectionService
from app.core.plugins.manager import PluginManager


class RunAnalysisCycleUseCase:
    """
    Orquestra o ciclo completo de análise de otimização da infraestrutura.
    """

    def __init__(
        self,
        fetch_metrics_uc: FetchMetricsUseCase,
        anomaly_detection_service: AnomalyDetectionService,
        llm_service: LLMServicePort,
        rule_repository: RuleRepositoryPort,
        plugin_manager: PluginManager,
    ) -> None:
        self._fetch_metrics_uc = fetch_metrics_uc
        self._anomaly_detection_service = anomaly_detection_service
        self._llm_service = llm_service
        self._rule_repository = rule_repository
        self._plugin_manager = plugin_manager

    async def execute(self) -> list[OptimizationOpportunity]:
        """
        Executa o fluxo de análise.

        Returns:
            Uma lista de oportunidades de otimização encontradas e enriquecidas
            com sugestões de solução.
        """
        all_rules = self._rule_repository.get_all()
        analysis_plugins = self._plugin_manager.get_analysis_rule_plugins()

        queries_to_fetch = list(set(rule.metric_name for rule in all_rules))
        if not queries_to_fetch and not analysis_plugins:
            return []

        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=15)
        all_metrics = []
        for query in queries_to_fetch:
            metrics = await self._fetch_metrics_uc.execute(query, start_time, end_time)
            all_metrics.extend(metrics)

        opportunities = self._anomaly_detection_service.find_opportunities(
            metrics=all_metrics, rules=all_rules
        )

        for plugin in analysis_plugins:
            plugin_opportunities = plugin.analyze(metrics=all_metrics)
            opportunities.extend(plugin_opportunities)

        for opportunity in opportunities:
            suggested_change = await self._llm_service.generate_solution_for_opportunity(opportunity)
            opportunity.suggested_change = suggested_change

        return opportunities