from __future__ import annotations
from typing import Literal

from pydantic import BaseModel, Field


class IaCFile(BaseModel):
    """Representa um único arquivo de Infraestrutura como Código (IaC)."""
    filename: str = Field(..., description="O nome do arquivo, ex: 'main.tf'.")
    content: str = Field(..., description="O conteúdo de código do arquivo.")
    provider: str = Field(default="terraform", description="A ferramenta de IaC, ex: 'terraform'.")


class TerraformBackendConfig(BaseModel):
    """
    Representa a configuração para um backend remoto do Terraform.
    Nesta fase inicial, focamos no backend S3 da AWS.
    """
    bucket: str
    key: str
    region: str


class TerraformConfiguration(BaseModel):
    """
    Representa um conjunto completo de configuração do Terraform para uma operação.
    Este modelo agora é a unidade de trabalho principal para os nossos casos de uso de IaC,
    permitindo que eles operem com configurações mais complexas que incluem estado remoto.
    """
    main_file: IaCFile
    backend_config: TerraformBackendConfig | None = None


ResourceChangeAction = Literal["create", "update", "delete", "no-op", "replace"]

class ResourceChange(BaseModel):
    address: str
    action: ResourceChangeAction

class ExecutionPlan(BaseModel):
    changes: list[ResourceChange]
    raw_output: str

class ApplyResult(BaseModel):
    success: bool
    raw_output: str