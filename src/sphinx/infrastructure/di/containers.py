# src/sphinx/infrastructure/di/containers.py

from dependency_injector import containers, providers

from src.sphinx.adapters.gateways.llm_gemini import GeminiAdapter
from src.sphinx.adapters.gateways.obs_prometheus import PrometheusGateway
from src.sphinx.adapters.providers.iac_terraform import TerraformAdapter
from src.sphinx.core.application.use_cases.apply_infrastructure_changes import (
    ApplyInfrastructureChangesUseCase,
)
from src.sphinx.core.application.use_cases.create_execution_plan import (
    CreateExecutionPlanUseCase,
)
from src.sphinx.core.application.use_cases.create_optimization_plan import (
    CreateOptimizationPlanUseCase,
)
from src.sphinx.core.application.use_cases.fetch_metrics import FetchMetricsUseCase
from src.sphinx.core.application.use_cases.generate_iac import GenerateIacUseCase
from src.sphinx.core.domain.services.anomaly_detection import AnomalyDetectionService


class UseCases(containers.DeclarativeContainer):
    """Contêiner para os casos de uso da aplicação."""
    fetch_metrics = providers.Factory(
        FetchMetricsUseCase,
        observability_gateway=...,
    )
    generate_iac = providers.Factory(
        GenerateIacUseCase,
        llm_service=...,
    )
    create_execution_plan = providers.Factory(
        CreateExecutionPlanUseCase,
        iac_provider=...,
    )
    apply_infrastructure_changes = providers.Factory(
        ApplyInfrastructureChangesUseCase,
        iac_provider=...,
    )
    create_optimization_plan = providers.Factory(
        CreateOptimizationPlanUseCase,
        fetch_metrics_uc=fetch_metrics,
        anomaly_detection_service=...,
        llm_service=..., # Nova dependência adicionada
    )


class Container(containers.DeclarativeContainer):
    """
    Contêiner de Injeção de Dependência (DI) principal da aplicação.
    """

    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.sphinx.infrastructure.cli",
            "src.sphinx.infrastructure.tui.screens.chat_screen",
            "src.sphinx.infrastructure.tui.screens.dashboard_screen",
        ]
    )

    config = providers.Configuration(strict=True, dotenv_path=".env")

    # --- Domain Services ---
    anomaly_detection_service = providers.Factory(AnomalyDetectionService)

    # --- Gateways ---
    gemini_adapter = providers.Singleton(
        GeminiAdapter,
        api_key=config.GOOGLE_API_KEY,
    )
    prometheus_gateway = providers.Singleton(
        PrometheusGateway,
        url=config.PROMETHEUS_URL
    )

    # --- Providers ---
    terraform_adapter = providers.Singleton(TerraformAdapter)

    # --- Use Cases Wiring ---
    use_cases = providers.Container(
        UseCases,
        fetch_metrics__observability_gateway=prometheus_gateway,
        generate_iac__llm_service=gemini_adapter,
        create_execution_plan__iac_provider=terraform_adapter,
        apply_infrastructure_changes__iac_provider=terraform_adapter,
        create_optimization_plan__anomaly_detection_service=anomaly_detection_service,
        # Conecta a nova dependência à implementação do GeminiAdapter.
        create_optimization_plan__llm_service=gemini_adapter,
    )