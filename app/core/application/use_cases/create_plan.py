from __future__ import annotations

from app.core.application.ports.providers import IaCProviderPort
from app.core.domain.models.iac import ExecutionPlan, TerraformConfiguration


class CreateExecutionPlanUseCase:
    """Orquestra a criação de um plano de execução de IaC."""

    def __init__(self, iac_provider: IaCProviderPort) -> None:
        self._iac_provider = iac_provider

    async def execute(self, config: TerraformConfiguration) -> ExecutionPlan:
        """Executa o caso de uso de criação de plano de execução."""
        return await self._iac_provider.plan(config)