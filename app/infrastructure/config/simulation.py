from __future__ import annotations
import asyncio
import random
from uuid import uuid4
from datetime import datetime, timedelta

from app.core.domain.models.history import ActionRecord
from app.core.domain.models.iac import IaCFile, TerraformBackendConfig
from app.core.domain.models.observability import DataPoint, Metric
from app.core.domain.models.optimization import (
    OptimizationOpportunity,
    SuggestedChange,
)
from app.core.domain.models.workspace import Workspace


def create_mock_opportunities() -> list[OptimizationOpportunity]:
    """Cria uma lista de oportunidades de otimização para fins de demonstração."""

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
        DataPoint(
            timestamp=now - timedelta(minutes=15 - i), value=random.uniform(0.02, 0.08)
        )
        for i in range(15)
    ]

    opportunities = [
        OptimizationOpportunity(
            id=uuid4(),
            title="CPU Ociosa Detetada para 'prometheus'",
            description="O uso da CPU para o recurso 'prometheus' permaneceu abaixo de 10% por mais de 15 minutos, indicando provisionamento excessivo.",
            resource_address="prometheus",
            evidence=[
                Metric(
                    name="cpu_usage",
                    labels={"job": "prometheus"},
                    datapoints=cpu_datapoints,
                )
            ],
            suggested_change=SuggestedChange(
                impact_assessment="Reduzir o tamanho da instância de 't2.medium' para 't2.micro' pode gerar uma economia de custos de aproximadamente 50% com impacto mínimo no desempenho, dado o baixo uso de CPU.",
                suggested_iac_file=IaCFile(
                    filename="instance.tf", content=mock_terraform_code
                ),
            ),
        ),
        OptimizationOpportunity(
            id=uuid4(),
            title="Sugerir Upgrade de Volume EBS de gp2 para gp3",
            description="O volume EBS 'vol-012345abcdef' é do tipo 'gp2'. O tipo 'gp3' oferece melhor performance e é até 20% mais barato.",
            resource_address="vol-012345abcdef",
            evidence=[
                Metric(
                    name="aws_ebs_volume_info",
                    labels={"volume_id": "vol-012345abcdef", "volume_type": "gp2"},
                    datapoints=[],
                )
            ],
            suggested_change=SuggestedChange(
                impact_assessment="O upgrade para gp3 é uma operação online sem tempo de inatividade. Resultará em economia de custos imediata e melhor desempenho de linha de base (3,000 IOPS).",
                suggested_iac_file=IaCFile(
                    filename="ebs_volume.tf",
                    content='# A alteração do tipo de volume deve ser feita no recurso "aws_ebs_volume" correspondente.\n# Exemplo:\n# resource "aws_ebs_volume" "example" {\n#   type = "gp3"\n# }',
                ),
            ),
        ),
    ]
    return opportunities


def create_mock_history_records() -> list[ActionRecord]:
    """Cria uma lista de registos de histórico para a UI."""
    return [
        ActionRecord(
            opportunity_id=uuid4(),
            applied_at=datetime.now() - timedelta(hours=1),
            resource_address="prod-aurora-cluster",
            opportunity_title="Redimensionar instância de base de dados ociosa",
            applied_iac_content="# Terraform code for db resizing...",
        ),
        ActionRecord(
            opportunity_id=uuid4(),
            applied_at=datetime.now() - timedelta(days=2),
            resource_address="staging-load-balancer",
            opportunity_title="Atualizar Load Balancer para nova geração",
            applied_iac_content="# Terraform code for LB upgrade...",
        ),
    ]


def create_mock_workspaces() -> list[Workspace]:
    """Cria uma lista de workspaces para a UI."""
    return [
        Workspace(
            id=uuid4(),
            name="Produção AWS",
            backend_config=TerraformBackendConfig(
                bucket="prod-tfstate-bucket",
                key="terraform.tfstate",
                region="us-east-1",
            ),
        ),
        Workspace(
            id=uuid4(),
            name="Staging GCP",
            backend_config=TerraformBackendConfig(
                bucket="stg-tfstate-gcs", key="terraform/state", region="us-central1"
            ),
        ),
    ]


#  Classes de Casos de Uso para Simulação

class MockCreateOptimizationPlanUseCase:
    """Retorna dados de oportunidades pré-definidos com um atraso simulado."""

    async def execute(self) -> list[OptimizationOpportunity]:
        await asyncio.sleep(2)
        return create_mock_opportunities()


class MockViewHistoryUseCase:
    """Retorna dados de histórico pré-definidos com um atraso simulado."""

    async def execute(self) -> list[ActionRecord]:
        await asyncio.sleep(0.5)
        return create_mock_history_records()


class MockListWorkspacesUseCase:
    """Retorna dados de workspaces pré-definidos com um atraso simulado."""

    async def execute(self) -> list[Workspace]:
        await asyncio.sleep(0.5)
        return create_mock_workspaces()