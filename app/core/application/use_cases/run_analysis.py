# src/sphinx/core/application/use_cases/create_optimization_plan.py

from __future__ import annotations
from datetime import datetime, timedelta

from app.core.application.ports.gateways.llm import LLMServicePort
from app.core.application.ports.gateways.rules import RuleRepositoryPort
from app.core.application.use_cases.fetch_metrics import FetchMetricsUseCase
from app.core.domain.models.optimization import OptimizationOpportunity
from app.core.domain.services.anomalies import AnomalyDetectionService
from app.core.plugins.manager import PluginManager


class CreateOptimizationPlanUseCase:
    """
    Orquestra a análise de métricas, utilizando tanto regras de YAML quanto
    plugins de análise dinâmica.
    """

    def __init__(
        self,
        fetch_metrics_uc: FetchMetricsUseCase,
        anomaly_detection_service: AnomalyDetectionService,
        llm_service: LLMServicePort,
        rule_repository: RuleRepositoryPort,
        plugin_manager: PluginManager, # Nova dependência
    ) -> None:
        self._fetch_metrics_uc = fetch_metrics_uc
        self._anomaly_detection_service = anomaly_detection_service
        self._llm_service = llm_service
        self._rule_repository = rule_repository
        self._plugin_manager = plugin_manager

    async def execute(self) -> list[OptimizationOpportunity]:
        """
        Executa o fluxo completo: carrega regras, executa plugins, busca métricas,
        detecta anomalias e gera soluções.
        """
        all_rules = self._rule_repository.get_all()
        analysis_plugins = self._plugin_manager.get_analysis_rule_plugins()
        
        # Coleta as queries de métricas tanto das regras YAML quanto dos plugins (se necessário).
        # Por enquanto, assumimos que os plugins usam as mesmas métricas já coletadas.
        queries_to_fetch = list(set(rule.metric_name for rule in all_rules))
        if not queries_to_fetch and not analysis_plugins:
            return []

        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=15)
        all_metrics = []
        for query in queries_to_fetch:
            metrics = await self._fetch_metrics_uc.execute(query, start_time, end_time)
            all_metrics.extend(metrics)
        
        # Executa a análise baseada em regras YAML
        opportunities = self._anomaly_detection_service.find_opportunities(
            metrics=all_metrics, rules=all_rules
        )
        
        # Executa a análise de cada plugin carregado
        for plugin in analysis_plugins:
            plugin_opportunities = plugin.analyze(metrics=all_metrics)
            opportunities.extend(plugin_opportunities)
        
        # Enriquecimento com LLM para todas as oportunidades encontradas
        for opportunity in opportunities:
            suggested_change = await self._llm_service.generate_solution_for_opportunity(opportunity)
            opportunity.suggested_change = suggested_change
            
        return opportunities