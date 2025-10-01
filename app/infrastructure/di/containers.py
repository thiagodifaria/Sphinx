from dependency_injector import containers, providers

from app.adapters.gateways.gemini import GeminiAdapter
from app.adapters.gateways.prometheus import PrometheusGateway
from app.adapters.gateways.sqlite import (
    SQLiteHistoryRepository,
    SQLiteWorkspaceRepository,
)
from app.adapters.gateways.yaml_rules import YamlRuleRepository
from app.adapters.providers.terraform import TerraformAdapter
from app.core.application.state import AppState
from app.core.application.use_cases.apply_changes import (
    ApplyInfrastructureChangesUseCase,
)
from app.core.application.use_cases.build_config import BuildTerraformConfigUseCase
from app.core.application.use_cases.create_plan import CreateExecutionPlanUseCase
from app.core.application.use_cases.fetch_metrics import FetchMetricsUseCase
from app.core.application.use_cases.generate_iac import GenerateIacUseCase
from app.core.application.use_cases.record_action import RecordActionUseCase
from app.core.application.use_cases.run_analysis import RunAnalysisCycleUseCase
from app.core.application.use_cases.view_history import ViewHistoryUseCase
from app.core.application.use_cases.workspaces import (
    CreateWorkspaceUseCase,
    ListWorkspacesUseCase,
    SetActiveWorkspaceUseCase,
)
from app.core.domain.services.anomalies import AnomalyDetectionService
from app.core.plugins.manager import PluginManager
from app.infrastructure.config.settings import Settings
from app.infrastructure.config.simulation import (
    MockCreateOptimizationPlanUseCase,
    MockListWorkspacesUseCase,
    MockViewHistoryUseCase,
)


class Container(containers.DeclarativeContainer):
    """Contentor de Injeção de Dependência (DI) principal da aplicação."""

    config = providers.Configuration()
    settings = providers.Singleton(Settings)
    app_state = providers.Singleton(AppState)

    # Camada Core
    plugin_manager = providers.Singleton(
        PluginManager, plugins_dir=settings.provided.plugins_dir
    )
    anomaly_detection_service = providers.Factory(AnomalyDetectionService)

    #  Adaptadores (Gateways & Providers)
    gemini_adapter = providers.Singleton(
        GeminiAdapter,
        api_key=settings.provided.google_api_key.get_secret_value,
    )
    prometheus_gateway = providers.Singleton(
        PrometheusGateway, url=settings.provided.prometheus_url
    )
    history_repository = providers.Singleton(
        SQLiteHistoryRepository, db_path=settings.provided.sqlite_db_path
    )
    workspace_repository = providers.Singleton(
        SQLiteWorkspaceRepository, db_path=settings.provided.sqlite_db_path
    )
    rule_repository = providers.Singleton(
        YamlRuleRepository, file_path=settings.provided.rules_file_path
    )
    terraform_adapter = providers.Singleton(TerraformAdapter)

    # Casos de Uso Reais
    real_create_optimization_plan_uc = providers.Factory(
        RunAnalysisCycleUseCase,
        fetch_metrics_uc=providers.Factory(
            FetchMetricsUseCase, observability_gateway=prometheus_gateway
        ),
        anomaly_detection_service=anomaly_detection_service,
        llm_service=gemini_adapter,
        rule_repository=rule_repository,
        plugin_manager=plugin_manager,
    )
    real_view_history_uc = providers.Factory(
        ViewHistoryUseCase, history_repository=history_repository
    )
    real_list_workspaces_uc = providers.Factory(
        ListWorkspacesUseCase, workspace_repo=workspace_repository
    )

    # Casos de Uso de Simulação (Mock)
    mock_create_optimization_plan_uc = providers.Factory(
        MockCreateOptimizationPlanUseCase
    )
    mock_view_history_uc = providers.Factory(MockViewHistoryUseCase)
    mock_list_workspaces_uc = providers.Factory(MockListWorkspacesUseCase)

    # Seletores (Decidem entre Real e Simulação)
    create_optimization_plan_uc = providers.Selector(
        config.mock_data,
        true=mock_create_optimization_plan_uc,
        false=real_create_optimization_plan_uc,
    )
    view_history_uc = providers.Selector(
        config.mock_data, true=mock_view_history_uc, false=real_view_history_uc
    )
    list_workspaces_uc = providers.Selector(
        config.mock_data, true=mock_list_workspaces_uc, false=real_list_workspaces_uc
    )

    # Outros Casos de Uso (sem modo de simulação por agora)
    build_config_uc = providers.Factory(
        BuildTerraformConfigUseCase, app_state=app_state, settings=settings
    )
    generate_iac_uc = providers.Factory(GenerateIacUseCase, llm_service=gemini_adapter)
    create_execution_plan_uc = providers.Factory(
        CreateExecutionPlanUseCase, iac_provider=terraform_adapter
    )
    apply_infrastructure_changes_uc = providers.Factory(
        ApplyInfrastructureChangesUseCase, iac_provider=terraform_adapter
    )
    record_action_uc = providers.Factory(
        RecordActionUseCase, history_repository=history_repository
    )
    create_workspaces_uc = providers.Factory(
        CreateWorkspaceUseCase, workspace_repo=workspace_repository
    )
    set_active_workspace_uc = providers.Factory(
        SetActiveWorkspaceUseCase, app_state=app_state
    )