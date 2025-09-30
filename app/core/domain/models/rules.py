# src/sphinx/core/domain/models/rules.py

from __future__ import annotations
from enum import Enum

from pydantic import BaseModel, Field


class OperatorEnum(str, Enum):
    """Define os operadores de comparação para uma condição de regra."""
    LT = "less_than"
    GT = "greater_than"
    EQ = "equal_to"


class RuleCondition(BaseModel):
    """
    Define a condição que deve ser satisfeita para que uma regra seja acionada.
    Por exemplo: 'se o valor for MENOR QUE 0.1 por 10 minutos'.
    """
    operator: OperatorEnum = Field(..., description="O operador de comparação (ex: 'less_than').")
    threshold: float = Field(..., description="O valor numérico do limiar a ser comparado.")
    duration_minutes: int = Field(..., description="O período em minutos que a condição deve ser mantida.")


class AnalysisRule(BaseModel):
    """
    Representa uma única regra de análise de métrica de forma declarativa.

    Este modelo de domínio desacopla a lógica de detecção de anomalias do código,
    permitindo que as regras sejam carregadas de fontes externas (como arquivos YAML),
    tornando o Sphinx extensível e customizável pelo usuário.
    """
    name: str = Field(..., description="Um nome único e legível para a regra.")
    metric_name: str = Field(..., description="O nome da métrica a ser consultada (ex: PromQL query).")
    condition: RuleCondition = Field(..., description="O objeto de condição que aciona a regra.")
    opportunity_title_template: str = Field(
        ...,
        description="Template para o título da oportunidade gerada. Use {resource_id}."
    )
    opportunity_description_template: str = Field(
        ...,
        description="Template para a descrição. Use {resource_id}, {threshold}, {duration_minutes}."
    )