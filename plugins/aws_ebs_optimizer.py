# plugins/aws_ebs_optimizer.py

from __future__ import annotations
import logging

from app.core.domain.models.observability import Metric
from app.core.domain.models.optimization import OptimizationOpportunity
from app.core.plugins.interfaces import AnalysisRulePlugin

logger = logging.getLogger(__name__)


class EbsGp2ToGp3RulePlugin(AnalysisRulePlugin):
    """
    Um plugin que analisa métricas de volumes EBS da AWS e sugere o upgrade
    de volumes do tipo 'gp2' para 'gp3'.
    """

    @property
    def name(self) -> str:
        return "AWS EBS gp2 to gp3 Optimizer"

    @property
    def author(self) -> str:
        return "Sphinx Project"

    def analyze(self, metrics: list[Metric]) -> list[OptimizationOpportunity]:
        """
        Implementa a lógica de análise para encontrar volumes gp2.
        Ele espera uma métrica (ex: 'aws_ebs_volume_info') que contenha
        os labels 'volume_id' e 'volume_type'.
        """
        opportunities: list[OptimizationOpportunity] = []
        
        # Filtra as métricas que contêm as informações do tipo de volume.
        volume_info_metrics = [m for m in metrics if m.name == "aws_ebs_volume_info"]
        logger.info(f"Plugin '{self.name}' encontrou {len(volume_info_metrics)} métrica(s) de volume EBS para analisar.")

        for metric in volume_info_metrics:
            volume_type = metric.labels.get("volume_type")
            volume_id = metric.labels.get("volume_id")

            if not volume_id:
                continue

            # A lógica principal do plugin: se o volume é gp2, cria uma oportunidade.
            if volume_type == "gp2":
                logger.info(f"Plugin '{self.name}' detectou volume gp2: {volume_id}")
                opportunities.append(
                    OptimizationOpportunity(
                        title=f"Sugerir Upgrade de Volume EBS de gp2 para gp3",
                        description=(
                            f"O volume EBS '{volume_id}' é do tipo 'gp2'. "
                            "O tipo 'gp3' oferece performance de linha de base superior "
                            "(3,000 IOPS e 125 MiB/s) e é até 20% mais barato por GB. "
                            "O upgrade de gp2 para gp3 é recomendado para quase todos os casos de uso, "
                            "resultando em melhor performance e redução de custos."
                        ),
                        resource_address=volume_id,
                        evidence=[metric],
                    )
                )
        
        return opportunities