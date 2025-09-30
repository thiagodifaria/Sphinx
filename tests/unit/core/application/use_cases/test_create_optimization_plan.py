# tests/unit/core/application/use_cases/test_create_optimization_plan.py

from __future__ import annotations
from unittest.mock import AsyncMock, Mock

import pytest

from src.sphinx.core.application.use_cases.create_optimization_plan import CreateOptimizationPlanUseCase
from src.sphinx.core.domain.models.iac import IaCFile
from src.sphinx.core.domain.models.optimization import OptimizationOpportunity, SuggestedChange
from src.sphinx.core.domain.models.observability import Metric


@pytest.fixture
def mock_fetch_metrics_uc() -> AsyncMock:
    """Mock para o caso de uso que busca métricas."""
    return AsyncMock()


@pytest.fixture
def mock_anomaly_service() -> Mock:
    """Mock para o serviço de detecção de anomalias."""
    return Mock()


@pytest.fixture
def mock_llm_service() -> AsyncMock:
    """Mock para o serviço de LLM que gera soluções."""
    return AsyncMock()


@pytest.fixture
def use_case(
    mock_fetch_metrics_uc: AsyncMock,
    mock_anomaly_service: Mock,
    mock_llm_service: AsyncMock,
) -> CreateOptimizationPlanUseCase:
    """Fixture que monta o caso de uso com todas as suas dependências mockadas."""
    return CreateOptimizationPlanUseCase(
        fetch_metrics_uc=mock_fetch_metrics_uc,
        anomaly_detection_service=mock_anomaly_service,
        llm_service=mock_llm_service,
    )


async def test_create_optimization_plan_full_flow(
    use_case: CreateOptimizationPlanUseCase,
    mock_fetch_metrics_uc: AsyncMock,
    mock_anomaly_service: Mock,
    mock_llm_service: AsyncMock,
):
    """
    Testa o fluxo de orquestração completo do caso de uso.

    O objetivo é garantir que o caso de uso chame cada uma de suas dependências
    na ordem correta e passe os dados corretamente entre elas, validando seu
    papel de "maestro" da lógica de negócio.
    """
    # Arrange: Prepara os valores de retorno para cada mock.
    sample_queries = ["cpu_query"]
    sample_metrics = [Mock(spec=Metric)]
    sample_opportunity = Mock(spec=OptimizationOpportunity)
    sample_solution = Mock(spec=SuggestedChange)

    mock_fetch_metrics_uc.execute.return_value = sample_metrics
    mock_anomaly_service.find_opportunities.return_value = [sample_opportunity]
    mock_llm_service.generate_solution_for_opportunity.return_value = sample_solution

    # Act: Executa o caso de uso.
    result_opportunities = await use_case.execute(queries=sample_queries)

    # Assert: Verifica se os mocks foram chamados como esperado.
    # 1. Garante que a busca de métricas foi chamada com a query correta.
    mock_fetch_metrics_uc.execute.assert_called_once()
    assert sample_queries[0] in mock_fetch_metrics_uc.execute.call_args[0]

    # 2. Garante que a detecção de anomalia foi chamada com as métricas retornadas.
    mock_anomaly_service.find_opportunities.assert_called_once_with(sample_metrics)

    # 3. Garante que a geração de solução foi chamada com a oportunidade encontrada.
    mock_llm_service.generate_solution_for_opportunity.assert_called_once_with(sample_opportunity)

    # 4. Garante que a solução gerada foi corretamente anexada ao resultado final.
    assert len(result_opportunities) == 1
    assert result_opportunities[0].suggested_change == sample_solution