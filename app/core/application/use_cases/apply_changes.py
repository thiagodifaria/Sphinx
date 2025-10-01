from __future__ import annotations

from app.core.application.ports.providers import IaCProviderPort
from app.core.domain.models.iac import ApplyResult, TerraformConfiguration


class ApplyInfrastructureChangesUseCase:
    """Orquestra a aplicação de mudanças na infraestrutura."""

    def __init__(self, iac_provider: IaCProviderPort) -> None:
        self._iac_provider = iac_provider

    async def execute(self, config: TerraformConfiguration) -> ApplyResult:
        """Executa o caso de uso para aplicar as mudanças da infraestrutura."""
        return await self._iac_provider.apply(config)