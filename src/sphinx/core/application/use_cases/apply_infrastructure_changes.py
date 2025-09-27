# src/sphinx/core/application/use_cases/apply_infrastructure_changes.py

from __future__ import annotations

from src.sphinx.core.application.ports.providers.iac_provider import IaCProviderPort
from src.sphinx.core.domain.models.iac import ApplyResult, IaCFile


class ApplyInfrastructureChangesUseCase:
    """
    Orquestra a aplicação das mudanças na infraestrutura.

    Este caso de uso encapsula a lógica de negócio para confirmar e aplicar um
    conjunto de mudanças de IaC, delegando a execução real para um provedor
    abstrato, mantendo o núcleo da aplicação agnóstico à ferramenta.
    """
    def __init__(self, iac_provider: IaCProviderPort) -> None:
        self._iac_provider = iac_provider

    async def execute(self, iac_file: IaCFile) -> ApplyResult:
        """
        Executa o caso de uso para aplicar as mudanças da infraestrutura.

        Args:
            iac_file: O arquivo IaC que define o estado desejado da infraestrutura.

        Returns:
            O resultado da operação de 'apply'.
        """
        return await self._iac_provider.apply(iac_file)