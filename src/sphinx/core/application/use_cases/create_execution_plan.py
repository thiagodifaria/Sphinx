# src/sphinx/core/application/use_cases/create_execution_plan.py

from __future__ import annotations

from src.sphinx.core.application.ports.providers.iac_provider import IaCProviderPort
from src.sphinx.core.domain.models.iac import ExecutionPlan, IaCFile


class CreateExecutionPlanUseCase:
    """
    Orquestra a criação de um plano de execução de IaC.

    Este caso de uso serve como uma camada de orquestração limpa, encapsulando a
    lógica de interagir com um provedor de IaC para obter um plano, sem se
    preocupar com os detalhes de como esse plano é gerado.
    """

    def __init__(self, iac_provider: IaCProviderPort) -> None:
        self._iac_provider = iac_provider

    async def execute(self, iac_file: IaCFile) -> ExecutionPlan:
        """
        Executa o caso de uso de criação de plano de execução.

        Args:
            iac_file: O arquivo IaC a partir do qual o plano será criado.

        Returns:
            O plano de execução gerado pelo provedor de IaC.
        """
        return await self._iac_provider.plan(iac_file)