# src/sphinx/core/application/use_cases/fetch_metrics.py

from __future__ import annotations
from datetime import datetime

from app.core.application.ports.gateways.observability import ObservabilityGatewayPort
from app.core.domain.models.observability import Metric


class FetchMetricsUseCase:
    """Orquestra a busca de dados de métricas."""

    def __init__(self, observability_gateway: ObservabilityGatewayPort) -> None:
        self._observability_gateway = observability_gateway

    async def execute(self, query: str, start_time: datetime, end_time: datetime) -> list[Metric]:
        """
        Executa o caso de uso para buscar dados de métricas.
        """
        return await self._observability_gateway.fetch_metric_range(
            query=query, start_time=start_time, end_time=end_time
        )