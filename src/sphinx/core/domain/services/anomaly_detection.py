# src/sphinx/core/domain/services/anomaly_detection.py

from __future__ import annotations
from datetime import datetime, timedelta

from src.sphinx.core.domain.models.observability import Metric
from src.sphinx.core.domain.models.optimization import OptimizationOpportunity

# Em um sistema maduro, estes parâmetros seriam configuráveis.
IDLE_CPU_THRESHOLD = 0.1  # 10% de uso da CPU
IDLE_DURATION_MINUTES = 10


class AnomalyDetectionService:
    """
    Contém a lógica de negócio pura para detectar anomalias nos dados de métricas.

    Este serviço opera exclusivamente sobre os modelos de domínio, tornando-o
    altamente coeso, testável e independente de qualquer framework ou
    fonte de dados externa. Ele é o coração da capacidade analítica do Sphinx.
    """

    def find_opportunities(self, metrics: list[Metric]) -> list[OptimizationOpportunity]:
        """
        Analisa uma lista de métricas e retorna as oportunidades de otimização encontradas.

        Args:
            metrics: A lista de métricas a serem analisadas.

        Returns:
            Uma lista de objetos OptimizationOpportunity.
        """
        opportunities: list[OptimizationOpportunity] = []
        opportunities.extend(self._find_idle_cpu_opportunities(metrics))
        # Futuramente, outras checagens (memória ociosa, discos não utilizados) seriam chamadas aqui.
        return opportunities

    def _find_idle_cpu_opportunities(
        self, metrics: list[Metric]
    ) -> list[OptimizationOpportunity]:
        """Implementa a regra de negócio para detectar CPUs ociosas."""
        idle_opportunities: list[OptimizationOpportunity] = []
        
        # Filtra apenas as métricas de CPU que nos interessam
        cpu_metrics = [
            m for m in metrics if m.name == "rate(process_cpu_seconds_total[1m])"
        ]
        
        for metric in cpu_metrics:
            # Garante que temos dados suficientes para tomar uma decisão
            if not metric.datapoints:
                continue
            
            # Ordena por tempo e verifica se a duração é suficiente
            metric.datapoints.sort(key=lambda dp: dp.timestamp)
            duration = metric.datapoints[-1].timestamp - metric.datapoints[0].timestamp
            if duration < timedelta(minutes=IDLE_DURATION_MINUTES):
                continue
                
            # Verifica se todos os valores estão abaixo do nosso limiar de ociosidade
            is_idle = all(dp.value < IDLE_CPU_THRESHOLD for dp in metric.datapoints)
            
            if is_idle:
                # O endereço do recurso seria extraído dos labels em um cenário real.
                # Para o Prometheus local, usamos o 'job' como identificador.
                resource_id = metric.labels.get("job", "recurso_desconhecido")
                
                opportunity = OptimizationOpportunity(
                    title=f"CPU Ociosa Detectada para '{resource_id}'",
                    description=(
                        f"O uso da CPU para o recurso '{resource_id}' permaneceu abaixo de "
                        f"{IDLE_CPU_THRESHOLD*100}% nos últimos {IDLE_DURATION_MINUTES} minutos. "
                        "Considere reduzir o tamanho da instância ou usar políticas de auto-scaling."
                    ),
                    resource_address=resource_id,
                    evidence=[metric],
                )
                idle_opportunities.append(opportunity)

        return idle_opportunities