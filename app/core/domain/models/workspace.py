from __future__ import annotations
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.core.domain.models.iac import TerraformBackendConfig


class Workspace(BaseModel):
    """
    Representa um workspace de trabalho, que agrupa uma configuração de
    backend remoto com um nome amigável.
    """
    id: UUID = Field(default_factory=uuid4)
    name: str = Field(..., description="Nome único para o workspace.")
    backend_config: TerraformBackendConfig