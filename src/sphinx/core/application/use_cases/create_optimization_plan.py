# src/sphinx/core/application/use_cases/create_optimization_plan.py

from __future__ import annotations
from datetime import datetime, timedelta

from src.sphinx.core.application.ports.gateways.llm import LLMServicePort
from src.sphinx.core.application.use_cases.fetch_metrics import FetchMetricsUseCase
from src.sphinx.core.domain.models.optimization import OptimizationOpportunity
from src.sphinx.core.domain.services.anomaly_detection import AnomalyDetectionService


class CreateOptimizationPlanUseCase:
    """
    Orquestra a análise de métricas e a criação de um plano de otimização,
    incluindo a geração de soluções em código para as oportunidades encontradas.
    """

    def __init__(
        self,
        fetch_metrics_uc: FetchMetricsUseCase,
        anomaly_detection_service: AnomalyDetectionService,
        llm_service: LLMServicePort,
    ) -> None:
        self._fetch_metrics_uc = fetch_metrics_uc
        self._anomaly_detection_service = anomaly_detection_service
        self._llm_service = llm_service

    async def execute(self, queries: list[str]) -> list[OptimizationOpportunity]:
        """
        Executa o fluxo de busca de métricas, detecção e geração de solução.
        """
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=15)
        
        all_metrics = []
        for query in queries:
            metrics = await self._fetch_metrics_uc.execute(query, start_time, end_time)
            all_metrics.extend(metrics)
            
        opportunities = self._anomaly_detection_service.find_opportunities(all_metrics)
        
        for opportunity in opportunities:
            suggested_change = await self._llm_service.generate_solution_for_opportunity(opportunity)
            opportunity.suggested_change = suggested_change
            
        return opportunities