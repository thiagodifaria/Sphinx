from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime

from app.core.domain.models.history import ActionRecord
from app.core.domain.models.iac import IaCFile
from app.core.domain.models.observability import Metric
from app.core.domain.models.optimization import OptimizationOpportunity, SuggestedChange
from app.core.domain.models.rules import AnalysisRule
from app.core.domain.models.workspace import Workspace


class HistoryRepositoryPort(ABC):
    """
    Define o contrato para a persistência do histórico de ações.
    """

    @abstractmethod
    async def initialize(self) -> None:
        """Garante que o armazenamento de dados está pronto para uso."""
        raise NotImplementedError

    @abstractmethod
    async def add_record(self, record: ActionRecord) -> None:
        """Adiciona um novo registro de ação ao histórico."""
        raise NotImplementedError

    @abstractmethod
    async def get_all_records(self) -> list[ActionRecord]:
        """Recupera todos os registros de ação, do mais recente para o mais antigo."""
        raise NotImplementedError


class LLMServicePort(ABC):
    """
    Define o contrato para um serviço de Large Language Model (LLM).
    """

    @abstractmethod
    async def generate_iac(self, prompt: str) -> IaCFile:
        """Gera um arquivo de Infraestrutura como Código a partir de um prompt."""
        raise NotImplementedError

    @abstractmethod
    async def generate_solution_for_opportunity(
        self, opportunity: OptimizationOpportunity
    ) -> SuggestedChange:
        """Gera uma solução de código para uma oportunidade de otimização."""
        raise NotImplementedError


class ObservabilityGatewayPort(ABC):
    """
    Define o contrato para um gateway de dados de observabilidade.
    """

    @abstractmethod
    async def fetch_metric_range(
        self, query: str, start_time: datetime, end_time: datetime
    ) -> list[Metric]:
        """Busca dados de uma métrica para um intervalo de tempo."""
        raise NotImplementedError


class RuleRepositoryPort(ABC):
    """
    Define o contrato para um repositório que fornece regras de análise.
    """

    @abstractmethod
    def get_all(self) -> list[AnalysisRule]:
        """Carrega e retorna todas as regras de análise disponíveis."""
        raise NotImplementedError


class WorkspaceRepositoryPort(ABC):
    """Define o contrato para o repositório de workspaces."""

    @abstractmethod
    async def add(self, workspace: Workspace) -> None:
        """Adiciona um novo workspace."""
        raise NotImplementedError

    @abstractmethod
    async def get_all(self) -> list[Workspace]:
        """Retorna todos os workspaces salvos."""
        raise NotImplementedError