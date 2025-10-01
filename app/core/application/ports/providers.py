from __future__ import annotations
from abc import ABC, abstractmethod

from app.core.domain.models.iac import (
    ApplyResult, ExecutionPlan, TerraformConfiguration
)


class IaCProviderPort(ABC):
    """
    Define o contrato para um provedor de Infraestrutura como Código.
    """

    @abstractmethod
    async def plan(self, config: TerraformConfiguration) -> ExecutionPlan:
        """Executa um 'plan' para uma determinada configuração de IaC."""
        raise NotImplementedError

    @abstractmethod
    async def apply(self, config: TerraformConfiguration) -> ApplyResult:
        """Aplica as mudanças de uma determinada configuração de IaC."""
        raise NotImplementedError