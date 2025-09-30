# src/sphinx/core/application/ports/gateways/rules.py

from __future__ import annotations
from abc import ABC, abstractmethod

from app.core.domain.models.rules import AnalysisRule


class RuleRepositoryPort(ABC):
    """
    Define o contrato para um repositório que fornece regras de análise.
    """

    @abstractmethod
    def get_all(self) -> list[AnalysisRule]:
        """
        Carrega e retorna todas as regras de análise disponíveis.
        """
        raise NotImplementedError