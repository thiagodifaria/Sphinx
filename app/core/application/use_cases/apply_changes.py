# src/sphinx/core/application/use_cases/apply_infrastructure_changes.py

from __future__ import annotations

from app.core.application.ports.providers.iac_provider import IaCProviderPort
from app.core.domain.models.iac import ApplyResult, TerraformConfiguration


class ApplyInfrastructureChangesUseCase:
    """
    Orquestra a aplicação das mudanças na infraestrutura.
    """
    def __init__(self, iac_provider: IaCProviderPort) -> None:
        self._iac_provider = iac_provider

    async def execute(self, config: TerraformConfiguration) -> ApplyResult:
        """
        Executa o caso de uso para aplicar as mudanças da infraestrutura.
        """
        return await self._iac_provider.apply(config)