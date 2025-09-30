# src/sphinx/adapters/gateways/obs_prometheus.py

from __future__ import annotations
from datetime import datetime

from prometheus_api_client import PrometheusConnect, PrometheusApiClientException
from app.core.application.ports.gateways.observability import ObservabilityGatewayPort
from app.core.domain.models.observability import DataPoint, Metric


class PrometheusGateway(ObservabilityGatewayPort):
    """
    Implementação da ObservabilityGatewayPort que se conecta ao Prometheus.

    Este adaptador é a ponte entre o domínio do Sphinx e o mundo externo do
    Prometheus. Ele lida com os detalhes da API do Prometheus e, crucialmente,
    atua como uma camada anti-corrupção, transformando os dados de resposta
    em modelos de domínio puros e consistentes.
    """
    def __init__(self, url: str):
        self._client = PrometheusConnect(url=url, disable_ssl=True)

    async def fetch_metric_range(
        self, query: str, start_time: datetime, end_time: datetime
    ) -> list[Metric]:
        """Busca dados no Prometheus e os converte para os modelos de domínio."""
        try:
            raw_data = self._client.get_metric_range_data(
                metric_name=query, start_time=start_time, end_time=end_time
            )
            
            # Processo de transformação: converte o formato de dados do Prometheus
            # para a lista de objetos Metric do nosso domínio.
            metrics: list[Metric] = []
            for item in raw_data:
                metrics.append(Metric(
                    name=item['metric'].get('__name__', query),
                    labels=item['metric'],
                    datapoints=[
                        DataPoint(timestamp=ts, value=float(val))
                        for ts, val in item['values']
                    ]
                ))
            return metrics
        except PrometheusApiClientException as e:
            print(f"Erro ao buscar dados no Prometheus: {e}")
            return []