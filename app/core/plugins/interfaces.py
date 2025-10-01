from __future__ import annotations
from abc import ABC, abstractmethod

from app.core.domain.models.observability import Metric
from app.core.domain.models.optimization import OptimizationOpportunity


class SphinxPlugin(ABC):
    """
    A classe base abstrata para todos os plugins do Sphinx.

    Todo plugin deve herdar desta classe. Ela define os metadados básicos
    que o Sphinx usará para identificar e gerenciar os plugins carregados.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Retorna o nome único e legível do plugin."""
        raise NotImplementedError

    @property
    @abstractmethod
    def author(self) -> str:
        """Retorna o nome do autor ou da equipe que desenvolveu o plugin."""
        raise NotImplementedError


class AnalysisRulePlugin(SphinxPlugin, ABC):
    """
    A interface formal para plugins de Regra de Análise.

    Plugins deste tipo permitem a implementação de lógicas de detecção de
    anomalias complexas em Python, indo além do que é possível com as regras
    simples definidas em YAML. Um plugin pode, por exemplo, usar modelos de
    machine learning ou fazer chamadas a APIs externas para enriquecer a análise.
    """

    @abstractmethod
    def analyze(self, metrics: list[Metric]) -> list[OptimizationOpportunity]:
        """
        Executa a lógica de análise do plugin sobre um conjunto de métricas.

        O Sphinx chamará este método, passando todas as métricas relevantes que
        foram coletadas. O plugin é responsável por processar essas métricas
        e retornar uma lista de quaisquer oportunidades de otimização que encontrar.

        Args:
            metrics: Uma lista de objetos de domínio Metric coletados dos
                     gateways de observabilidade.

        Returns:
            Uma lista de objetos OptimizationOpportunity. Se nenhuma oportunidade
            for encontrada, deve retornar uma lista vazia.
        """
        raise NotImplementedError