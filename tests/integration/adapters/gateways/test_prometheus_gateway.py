# tests/integration/adapters/gateways/test_prometheus_gateway.py

from __future__ import annotations
from datetime import datetime
import json

import pytest
from httpx import Response

from src.sphinx.adapters.gateways.obs_prometheus import PrometheusGateway

# Um exemplo de resposta JSON da API do Prometheus para uma query de range.
SAMPLE_PROMETHEUS_RESPONSE = {
    "status": "success",
    "data": {
        "resultType": "matrix",
        "result": [
            {
                "metric": {
                    "__name__": "process_cpu_seconds_total",
                    "instance": "localhost:9090",
                    "job": "prometheus"
                },
                "values": [
                    [1727653860, "0.1"],
                    [1727653875, "0.2"]
                ]
            }
        ]
    }
}

@pytest.fixture
def prometheus_gateway() -> PrometheusGateway:
    """Fornece uma instância do gateway do Prometheus para os testes."""
    return PrometheusGateway(url="http://test-prometheus.com")


async def test_fetch_metric_range_parses_correctly(
    prometheus_gateway: PrometheusGateway, httpx_mock
):
    """
    Testa se o gateway consegue parsear uma resposta JSON válida do Prometheus
    e transformá-la em nossos modelos de domínio.
    """
    # Arrange: Configura o mock de HTTP para interceptar a chamada de API.
    # Quando nosso código tentar acessar esta URL, o httpx_mock retornará o JSON acima.
    prometheus_url_pattern = "http://test-prometheus.com/api/v1/query_range**"
    httpx_mock.add_response(
        url__regex=prometheus_url_pattern,
        json=SAMPLE_PROMETHEUS_RESPONSE
    )

    # Act: Executa o método que queremos testar.
    metrics = await prometheus_gateway.fetch_metric_range(
        query="process_cpu_seconds_total",
        start_time=datetime(2025, 9, 29),
        end_time=datetime(2025, 9, 30)
    )

    # Assert: Verifica se a transformação para os modelos de domínio foi bem-sucedida.
    assert len(metrics) == 1
    metric = metrics[0]
    assert metric.name == "process_cpu_seconds_total"
    assert metric.labels["job"] == "prometheus"
    assert len(metric.datapoints) == 2
    assert metric.datapoints[0].timestamp == datetime.fromtimestamp(1727653860)
    assert metric.datapoints[0].value == 0.1
    assert metric.datapoints[1].value == 0.2