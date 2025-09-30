# src/sphinx/core/domain/services/anomaly_detection.py

from __future__ import annotations
from datetime import timedelta

from app.core.domain.models.observability import Metric
from app.core.domain.models.optimization import OptimizationOpportunity
from app.core.domain.models.rules import AnalysisRule, OperatorEnum


class AnomalyDetectionService:
    """
    Contém a lógica de negócio genérica para detectar anomalias com base em um
    conjunto de regras configuráveis.

    Este serviço foi refatorado para ser um motor de regras puro. Ele não contém
    mais lógica de negócio específica, mas sim a capacidade de processar qualquer
    regra que siga o modelo AnalysisRule, tornando-o flexível e extensível.
    """

    def find_opportunities(
        self, metrics: list[Metric], rules: list[AnalysisRule]
    ) -> list[OptimizationOpportunity]:
        """
        Analisa uma lista de métricas contra um conjunto de regras e retorna as
        oportunidades de otimização encontradas.
        """
        opportunities: list[OptimizationOpportunity] = []
        for rule in rules:
            # Filtra as métricas que são relevantes para a regra atual.
            relevant_metrics = [m for m in metrics if m.name == rule.metric_name]
            
            for metric in relevant_metrics:
                if self._evaluate_condition(metric, rule):
                    opportunity = self._create_opportunity_from_rule(metric, rule)
                    opportunities.append(opportunity)
        
        return opportunities

    def _evaluate_condition(self, metric: Metric, rule: AnalysisRule) -> bool:
        """Avalia se uma métrica satisfaz a condição de uma regra."""
        if not metric.datapoints:
            return False

        # Garante que temos dados suficientes para a janela de tempo da regra.
        metric.datapoints.sort(key=lambda dp: dp.timestamp)
        duration = metric.datapoints[-1].timestamp - metric.datapoints[0].timestamp
        if duration < timedelta(minutes=rule.condition.duration_minutes):
            return False

        # Verifica se todos os pontos de dados na janela satisfazem o operador.
        op_map = {
            OperatorEnum.LT: lambda val, thr: val < thr,
            OperatorEnum.GT: lambda val, thr: val > thr,
            OperatorEnum.EQ: lambda val, thr: val == thr,
        }
        eval_func = op_map[rule.condition.operator]
        
        return all(eval_func(dp.value, rule.condition.threshold) for dp in metric.datapoints)

    def _create_opportunity_from_rule(
        self, metric: Metric, rule: AnalysisRule
    ) -> OptimizationOpportunity:
        """Cria um objeto OptimizationOpportunity a partir de uma regra e métrica."""
        # Extrai um identificador de recurso dos labels da métrica.
        resource_id = metric.labels.get("job") or metric.labels.get("instance") or "recurso_desconhecido"

        # Formata as strings de template com os valores da regra e da métrica.
        title = rule.opportunity_title_template.format(resource_id=resource_id)
        description = rule.opportunity_description_template.format(
            resource_id=resource_id,
            threshold=rule.condition.threshold * 100,  # Exibe como porcentagem
            duration_minutes=rule.condition.duration_minutes,
        )

        return OptimizationOpportunity(
            title=title,
            description=description,
            resource_address=resource_id,
            evidence=[metric],
        )