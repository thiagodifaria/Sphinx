# src/sphinx/infrastructure/di/containers.py

import asyncio
import random
from dependency_injector import containers, providers
from uuid import uuid4
from datetime import datetime, timedelta

from app.adapters.gateways.db_sqlite import (
    SQLiteHistoryRepository, SQLiteWorkspaceRepository
)
from app.adapters.gateways.llm_gemini import GeminiAdapter
from app.adapters.gateways.obs_prometheus import PrometheusGateway
from app.adapters.gateways.rule_yaml import YamlRuleRepository
from app.adapters.providers.iac_terraform import TerraformAdapter
from app.core.application.state import AppState
from app.core.application.use_cases.apply_infrastructure_changes import (
    ApplyInfrastructureChangesUseCase,
)
from app.core.application.use_cases.create_execution_plan import (
    CreateExecutionPlanUseCase,
)
from app.core.application.use_cases.create_optimization_plan import (
    CreateOptimizationPlanUseCase,
)
from app.core.application.use_cases.fetch_metrics import FetchMetricsUseCase
from app.core.application.use_cases.generate_iac import GenerateIacUseCase
from app.core.application.use_cases.manage_workspaces import (
    CreateWorkspaceUseCase, ListWorkspacesUseCase, SetActiveWorkspaceUseCase
)
from app.core.application.use_cases.record_action import RecordActionUseCase
from app.core.application.use_cases.view_history import ViewHistoryUseCase
from app.core.domain.services.anomaly_detection import AnomalyDetectionService
from app.core.plugins.manager import PluginManager
from app.infrastructure.config.settings import Settings

# --- Modelos para Dados Mockados ---
from app.core.domain.models.optimization import OptimizationOpportunity, SuggestedChange
from app.core.domain.models.iac import IaCFile, TerraformBackendConfig
from app.core.domain.models.observability import Metric, DataPoint
from app.core.domain.models.history import ActionRecord
from app.core.domain.models.workspace import Workspace


# --- Funções Geradoras de Dados Mockados ---

def create_mock_opportunities():
    """Cria uma lista de oportunidades realistas para fins de visualização."""
    
    mock_terraform_code = """
resource "aws_instance" "web_server" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro" # Otimizado de t2.medium para t2.micro

  tags = {
    Name = "WebServer"
  }
}
"""
    now = datetime.now()
    cpu_datapoints = [
        DataPoint(timestamp=now - timedelta(minutes=15-i), value=random.uniform(0.02, 0.08))
        for i in range(15)
    ]
    
    opportunities = [
        OptimizationOpportunity(
            id=uuid4(),
            title="CPU Ociosa Detectada para 'prometheus'",
            description="O uso da CPU para o recurso 'prometheus' permaneceu abaixo de 10% por mais de 15 minutos, indicando provisionamento excessivo.",
            resource_address="prometheus",
            evidence=[Metric(name="cpu_usage", labels={"job": "prometheus"}, datapoints=cpu_datapoints)],
            suggested_change=SuggestedChange(
                impact_assessment="Reduzir o tamanho da instância de 't2.medium' para 't2.micro' pode gerar uma economia de custos de aproximadamente 50% com impacto mínimo no desempenho, dado o baixo uso de CPU.",
                suggested_iac_file=IaCFile(
                    filename="instance.tf",
                    content=mock_terraform_code
                )
            )
        ),
        OptimizationOpportunity(
            id=uuid4(),
            title="Sugerir Upgrade de Volume EBS de gp2 para gp3",
            description="O volume EBS 'vol-012345abcdef' é do tipo 'gp2'. O tipo 'gp3' oferece melhor performance e é até 20% mais barato.",
            resource_address="vol-012345abcdef",
            evidence=[Metric(name="aws_ebs_volume_info", labels={"volume_id": "vol-012345abcdef", "volume_type": "gp2"}, datapoints=[])],
            suggested_change=SuggestedChange(
                impact_assessment="O upgrade para gp3 é uma operação online sem tempo de inatividade. Resultará em economia de custos imediata e melhor desempenho de linha de base (3,000 IOPS).",
                suggested_iac_file=IaCFile(
                    filename="ebs_volume.tf",
                    content="# A alteração do tipo de volume deve ser feita no recurso 'aws_ebs_volume' correspondente.\n# Exemplo:\n# resource \"aws_ebs_volume\" \"example\" {\n#   type = \"gp3\"\n# }"
                )
            )
        ),
        OptimizationOpportunity(
            id=uuid4(),
            title="Alto Uso de Memória Detectado para 'api-service'",
            description="O serviço 'api-service' está usando mais de 90% da memória alocada. Considere aumentar a alocação de memória ou investigar por memory leaks.",
            resource_address="api-service",
            evidence=[Metric(name="memory_usage", labels={"job": "api-service"}, datapoints=[DataPoint(timestamp=now, value=0.92)])],
            suggested_change=None
        ),
    ]
    return opportunities

def create_mock_history_records():
    """Cria uma lista de registros de histórico para a UI."""
    return [
        ActionRecord(
            opportunity_id=uuid4(),
            applied_at=datetime.now() - timedelta(hours=1),
            resource_address="prod-aurora-cluster",
            opportunity_title="Redimensionar instância de banco de dados ociosa",
            applied_iac_content="# Terraform code for db resizing..."
        ),
        ActionRecord(
            opportunity_id=uuid4(),
            applied_at=datetime.now() - timedelta(days=2),
            resource_address="staging-load-balancer",
            opportunity_title="Atualizar Load Balancer para nova geração",
            applied_iac_content="# Terraform code for LB upgrade..."
        ),
    ]

def create_mock_workspaces():
    """Cria uma lista de workspaces para a UI."""
    return [
        Workspace(
            id=uuid4(),
            name="Produção AWS",
            backend_config=TerraformBackendConfig(bucket="prod-tfstate-bucket", key="terraform.tfstate", region="us-east-1")
        ),
        Workspace(
            id=uuid4(),
            name="Staging GCP",
            backend_config=TerraformBackendConfig(bucket="stg-tfstate-gcs", key="terraform/state", region="us-central1")
        ),
    ]

# --- Classes de Casos de Uso Mockados ---

class MockCreateOptimizationPlanUseCase:
    """Retorna dados de oportunidades pré-definidos."""
    async def execute(self) -> list[OptimizationOpportunity]:
        await asyncio.sleep(2)
        return create_mock_opportunities()

class MockViewHistoryUseCase:
    """Retorna dados de histórico pré-definidos."""
    async def execute(self) -> list[ActionRecord]:
        await asyncio.sleep(0.5)
        return create_mock_history_records()

class MockListWorkspacesUseCase:
    """Retorna dados de workspaces pré-definidos."""
    async def execute(self) -> list[Workspace]:
        await asyncio.sleep(0.5)
        return create_mock_workspaces()


class Container(containers.DeclarativeContainer):
    """Contêiner de Injeção de Dependência (DI) principal da aplicação."""
    
    config = providers.Configuration()
    settings = providers.Singleton(Settings)
    app_state = providers.Singleton(AppState)

    plugin_manager = providers.Singleton(PluginManager, plugins_dir=settings.provided.plugins_dir)
    anomaly_detection_service = providers.Factory(AnomalyDetectionService)

    gemini_adapter = providers.Singleton(
        GeminiAdapter,
        api_key=settings.provided.google_api_key.get_secret_value,
    )
    prometheus_gateway = providers.Singleton(PrometheusGateway, url=settings.provided.prometheus_url)
    history_repository = providers.Singleton(SQLiteHistoryRepository, db_path=settings.provided.sqlite_db_path)
    workspace_repository = providers.Singleton(SQLiteWorkspaceRepository, db_path=settings.provided.sqlite_db_path)
    rule_repository = providers.Singleton(YamlRuleRepository, file_path=settings.provided.rules_file_path)
    
    terraform_adapter = providers.Singleton(TerraformAdapter)

    # --- Casos de Uso Reais ---
    real_fetch_metrics_uc = providers.Factory(FetchMetricsUseCase, observability_gateway=prometheus_gateway)
    real_generate_iac_uc = providers.Factory(GenerateIacUseCase, llm_service=gemini_adapter)
    real_create_execution_plan_uc = providers.Factory(CreateExecutionPlanUseCase, iac_provider=terraform_adapter)
    real_apply_infrastructure_changes_uc = providers.Factory(ApplyInfrastructureChangesUseCase, iac_provider=terraform_adapter)
    real_record_action_uc = providers.Factory(RecordActionUseCase, history_repository=history_repository)
    real_view_history_uc = providers.Factory(ViewHistoryUseCase, history_repository=history_repository)
    real_create_workspaces_uc = providers.Factory(CreateWorkspaceUseCase, workspace_repo=workspace_repository)
    real_list_workspaces_uc = providers.Factory(ListWorkspacesUseCase, workspace_repo=workspace_repository)
    real_set_active_workspace_uc = providers.Factory(SetActiveWorkspaceUseCase, app_state=app_state)
    real_create_optimization_plan_uc = providers.Factory(
        CreateOptimizationPlanUseCase,
        fetch_metrics_uc=real_fetch_metrics_uc,
        anomaly_detection_service=anomaly_detection_service,
        llm_service=gemini_adapter,
        rule_repository=rule_repository,
        plugin_manager=plugin_manager,
    )

    # --- Casos de Uso Mockados ---
    mock_create_optimization_plan_uc = providers.Factory(MockCreateOptimizationPlanUseCase)
    mock_view_history_uc = providers.Factory(MockViewHistoryUseCase)
    mock_list_workspaces_uc = providers.Factory(MockListWorkspacesUseCase)

    # --- Seletores (Decidem entre Real e Mock) ---
    create_optimization_plan_uc = providers.Selector(
        config.mock_data,
        true=mock_create_optimization_plan_uc,
        false=real_create_optimization_plan_uc,
    )
    view_history_uc = providers.Selector(
        config.mock_data,
        true=mock_view_history_uc,
        false=real_view_history_uc,
    )
    list_workspaces_uc = providers.Selector(
        config.mock_data,
        true=mock_list_workspaces_uc,
        false=real_list_workspaces_uc,
    )
    
    # Casos de uso que não precisam de mock (pois alteram o estado ou não são lidos na UI inicial)
    # permanecem apontando para a implementação real.
    generate_iac_uc = real_generate_iac_uc
    create_execution_plan_uc = real_create_execution_plan_uc
    apply_infrastructure_changes_uc = real_apply_infrastructure_changes_uc
    record_action_uc = real_record_action_uc
    create_workspaces_uc = real_create_workspaces_uc
    set_active_workspace_uc = real_set_active_workspace_uc
    fetch_metrics_uc = real_fetch_metrics_uc