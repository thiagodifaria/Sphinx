# src/sphinx/core/domain/models/iac.py

from __future__ import annotations
from typing import Literal

from pydantic import BaseModel, Field

# Modelos anteriores (IaCFile, ResourceChangeAction, etc.) permanecem os mesmos
class IaCFile(BaseModel):
    filename: str = Field(..., description="O nome do arquivo, ex: 'main.tf'.")
    content: str = Field(..., description="O conteúdo de código do arquivo.")
    provider: str = Field(default="terraform", description="A ferramenta de IaC, ex: 'terraform'.")

ResourceChangeAction = Literal["create", "update", "delete", "no-op", "replace"]

class ResourceChange(BaseModel):
    address: str = Field(..., description="O endereço do recurso no estado do Terraform.")
    action: ResourceChangeAction = Field(..., description="A ação que será executada no recurso.")

class ExecutionPlan(BaseModel):
    changes: list[ResourceChange] = Field(..., description="Uma lista de mudanças nos recursos.")
    raw_output: str = Field(..., description="A saída de texto crua do comando 'plan'.")


# Novo modelo para a Fase 2.2
class ApplyResult(BaseModel):
    """Representa o resultado de um comando 'apply' de uma ferramenta de IaC."""
    success: bool = Field(..., description="Indica se a operação foi bem-sucedida.")
    raw_output: str = Field(..., description="A saída de texto crua do comando 'apply'.")