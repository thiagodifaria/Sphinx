# src/sphinx/core/domain/models/optimization.py

from __future__ import annotations

from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.core.domain.models.iac import IaCFile
from app.core.domain.models.observability import Metric


class SuggestedChange(BaseModel):
    """Representa uma solução de código proposta para uma oportunidade."""
    impact_assessment: str = Field(..., description="Análise do impacto esperado da mudança.")
    # Mudança: A sugestão agora é um arquivo IaC completo, não apenas um diff.
    # Isso torna a sugestão autocontida e diretamente aplicável.
    suggested_iac_file: IaCFile = Field(..., description="O arquivo IaC completo com a solução proposta.")


class OptimizationOpportunity(BaseModel):
    """
    Representa uma oportunidade de otimização identificada na infraestrutura.
    """
    id: UUID = Field(default_factory=uuid4)
    title: str = Field(..., description="Um título conciso para a oportunidade.")
    description: str = Field(..., description="Uma explicação detalhada do problema e do impacto.")
    resource_address: str = Field(..., description="O endereço do recurso de IaC associado.")
    evidence: list[Metric] = Field(..., description="A lista de métricas que comprovam a oportunidade.")
    suggested_change: SuggestedChange | None = Field(
        default=None, description="A mudança de código sugerida para resolver a oportunidade."
    )