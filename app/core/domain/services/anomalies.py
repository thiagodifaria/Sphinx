from __future__ import annotations
from datetime import timedelta

from app.core.domain.models.observability import Metric
from app.core.domain.models.optimization import OptimizationOpportunity
from app.core.domain.models.rules import AnalysisRule, OperatorEnum


class AnomalyDetectionService:
    """
    Um motor de regras para detetar anomalias em métricas com base num conjunto
    de regras configuráveis.
    """

    def find_opportunities(
        self, metrics: list[Metric], rules: list[AnalysisRule]
    ) -> list[OptimizationOpportunity]:
        """
        Analisa uma lista de métricas contra um conjunto de regras.

        Args:
            metrics: A lista de métricas recolhidas para análise.
            rules: A lista de regras de análise a serem aplicadas.

        Returns:
            Uma lista de oportunidades de otimização encontradas.
        """
        opportunities: list[OptimizationOpportunity] = []
        for rule in rules:
            relevant_metrics = [m for m in metrics if m.name == rule.metric_name]

            for metric in relevant_metrics:
                if self._evaluate_condition(metric, rule):
                    opportunity = self._create_opportunity_from_rule(metric, rule)
                    opportunities.append(opportunity)

        return opportunities

    def _evaluate_condition(self, metric: Metric, rule: AnalysisRule) -> bool:
        """Avalia se uma única métrica satisfaz a condição de uma regra."""
        if not metric.datapoints:
            return False

        metric.datapoints.sort(key=lambda dp: dp.timestamp)
        duration = metric.datapoints[-1].timestamp - metric.datapoints[0].timestamp
        if duration < timedelta(minutes=rule.condition.duration_minutes):
            return False

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
        resource_id = metric.labels.get("job") or metric.labels.get("instance") or "recurso_desconhecido"

        title = rule.opportunity_title_template.format(resource_id=resource_id)
        description = rule.opportunity_description_template.format(
            resource_id=resource_id,
            threshold=rule.condition.threshold * 100,
            duration_minutes=rule.condition.duration_minutes,
        )

        return OptimizationOpportunity(
            title=title,
            description=description,
            resource_address=resource_id,
            evidence=[metric],
        )