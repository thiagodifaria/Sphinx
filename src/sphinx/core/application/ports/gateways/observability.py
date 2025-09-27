# src/sphinx/core/application/ports/gateways/observability.py

from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime

from src.sphinx.core.domain.models.observability import Metric


class ObservabilityGatewayPort(ABC):
    """
    Define o contrato para um gateway de dados de observabilidade.
    """

    @abstractmethod
    async def fetch_metric_range(
        self, query: str, start_time: datetime, end_time: datetime
    ) -> list[Metric]:
        """

        Busca dados de uma métrica para um intervalo de tempo.

        Args:
            query: A query na linguagem do sistema de monitoramento (ex: PromQL).
            start_time: O início do intervalo de tempo.
            end_time: O fim do intervalo de tempo.

        Returns:
            Uma lista de Métricas, pois uma query pode retornar múltiplas séries temporais.
        """
        raise NotImplementedError