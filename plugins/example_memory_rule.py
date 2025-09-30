# plugins/example_memory_rule.py

from __future__ import annotations

from app.core.domain.models.observability import Metric
from app.core.domain.models.optimization import OptimizationOpportunity
from app.core.plugins.interfaces import AnalysisRulePlugin


class HighMemoryUsageRule(AnalysisRulePlugin):
    """
    Um plugin de exemplo que detecta oportunidades de otimização
    para alto uso de memória.
    """
    @property
    def name(self) -> str:
        return "High Memory Usage Rule"

    @property
    def author(self) -> str:
        return "Sphinx Team"

    def analyze(self, metrics: list[Metric]) -> list[OptimizationOpportunity]:
        """
        Lógica de análise do plugin: procura por métricas de memória
        que excedem um limiar fixo.
        """
        opportunities: list[OptimizationOpportunity] = []
        memory_metrics = [m for m in metrics if "process_virtual_memory_bytes" in m.name]

        # Limiar de 100MB para este exemplo.
        HIGH_MEMORY_THRESHOLD_BYTES = 100 * 1024 * 1024

        for metric in memory_metrics:
            if not metric.datapoints:
                continue
            
            # Verifica se o valor mais recente da métrica excede o limiar.
            latest_value = metric.datapoints[-1].value
            if latest_value > HIGH_MEMORY_THRESHOLD_BYTES:
                resource_id = metric.labels.get("job", "recurso_desconhecido")
                opportunities.append(
                    OptimizationOpportunity(
                        title=f"Alto Uso de Memória Detectado para '{resource_id}'",
                        description=(
                            f"O uso de memória para o recurso '{resource_id}' excedeu "
                            f"{HIGH_MEMORY_THRESHOLD_BYTES / (1024*1024):.2f}MB. "
                            "Considere investigar por memory leaks ou aumentar a alocação de memória."
                        ),
                        resource_address=resource_id,
                        evidence=[metric],
                    )
                )
        return opportunities