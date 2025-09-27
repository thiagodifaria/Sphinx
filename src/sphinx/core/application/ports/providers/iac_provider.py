# src/sphinx/core/application/ports/providers/iac_provider.py

from __future__ import annotations
from abc import ABC, abstractmethod

from src.sphinx.core.domain.models.iac import ApplyResult, ExecutionPlan, IaCFile


class IaCProviderPort(ABC):
    """
    Define o contrato para um provedor de Infraestrutura como Código.
    """

    @abstractmethod
    async def plan(self, iac_file: IaCFile) -> ExecutionPlan:
        """
        Executa um 'plan' para um determinado arquivo de configuração de IaC.
        """
        raise NotImplementedError

    @abstractmethod
    async def apply(self, iac_file: IaCFile) -> ApplyResult:
        """
        Aplica as mudanças de um determinado arquivo de configuração de IaC.

        Args:
            iac_file: O arquivo de IaC a ser aplicado.

        Returns:
            Um ApplyResult detalhando o sucesso e a saída da operação.
        """
        raise NotImplementedError