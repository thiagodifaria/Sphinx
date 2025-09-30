# src/sphinx/core/application/ports/gateways/llm.py

from __future__ import annotations

from abc import ABC, abstractmethod

from app.core.domain.models.iac import IaCFile
from app.core.domain.models.optimization import OptimizationOpportunity, SuggestedChange


class LLMServicePort(ABC):
    """
    Define o contrato para um serviço de Large Language Model (LLM).
    """

    @abstractmethod
    async def generate_iac(self, prompt: str) -> IaCFile:
        """Gera um arquivo de Infraestrutura como Código a partir de um prompt de texto."""
        raise NotImplementedError

    @abstractmethod
    async def generate_solution_for_opportunity(
        self, opportunity: OptimizationOpportunity
    ) -> SuggestedChange:
        """
        Gera uma solução em código para uma oportunidade de otimização específica.
        """
        raise NotImplementedError