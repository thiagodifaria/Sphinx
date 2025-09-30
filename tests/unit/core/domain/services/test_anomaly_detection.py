# tests/unit/core/domain/services/test_anomaly_detection.py

from __future__ import annotations
from datetime import datetime, timedelta

import pytest

from src.sphinx.core.domain.models.observability import DataPoint, Metric
from src.sphinx.core.domain.services.anomaly_detection import AnomalyDetectionService


@pytest.fixture
def anomaly_service() -> AnomalyDetectionService:
    """Fixture do Pytest que fornece uma instância limpa do nosso serviço."""
    return AnomalyDetectionService()


def test_find_opportunities_returns_opportunity_for_idle_cpu(anomaly_service: AnomalyDetectionService):
    """
    Verifica se uma oportunidade é criada quando os dados da métrica de CPU
    estão consistentemente abaixo do limiar de ociosidade.
    """
    # Arrange: Criação de dados de métrica que simulam uma CPU ociosa.
    now = datetime.now()
    idle_metrics = [
        Metric(
            name="rate(process_cpu_seconds_total[1m])",
            labels={"job": "test-instance"},
            datapoints=[
                DataPoint(timestamp=now - timedelta(minutes=15), value=0.01),
                DataPoint(timestamp=now - timedelta(minutes=10), value=0.02),
                DataPoint(timestamp=now, value=0.015),
            ],
        )
    ]

    # Act: Execução do método que queremos testar.
    opportunities = anomaly_service.find_opportunities(idle_metrics)

    # Assert: Verificação dos resultados.
    assert len(opportunities) == 1
    assert opportunities[0].title == "CPU Ociosa Detectada para 'test-instance'"
    assert "permaneceu abaixo de 10.0%" in opportunities[0].description


def test_find_opportunities_returns_nothing_for_active_cpu(anomaly_service: AnomalyDetectionService):
    """
    Verifica se nenhuma oportunidade é criada quando os dados da métrica de CPU
    indicam atividade normal (acima do limiar).
    """
    # Arrange: Criação de dados de métrica que simulam uma CPU ativa.
    now = datetime.now()
    active_metrics = [
        Metric(
            name="rate(process_cpu_seconds_total[1m])",
            labels={"job": "test-instance"},
            datapoints=[
                DataPoint(timestamp=now - timedelta(minutes=15), value=0.5),
                DataPoint(timestamp=now - timedelta(minutes=10), value=0.8),
                DataPoint(timestamp=now, value=0.6),
            ],
        )
    ]

    # Act
    opportunities = anomaly_service.find_opportunities(active_metrics)

    # Assert
    assert len(opportunities) == 0


def test_find_opportunities_returns_nothing_for_irrelevant_metrics(anomaly_service: AnomalyDetectionService):
    """
    Verifica se o serviço ignora métricas que não são relevantes para as
    regras de detecção de anomalia atualmente implementadas.
    """
    # Arrange: Criação de dados de uma métrica não relacionada à CPU.
    now = datetime.now()
    other_metrics = [
        Metric(
            name="memory_usage_bytes",
            labels={"job": "test-instance"},
            datapoints=[DataPoint(timestamp=now, value=1024)],
        )
    ]

    # Act
    opportunities = anomaly_service.find_opportunities(other_metrics)

    # Assert
    assert len(opportunities) == 0