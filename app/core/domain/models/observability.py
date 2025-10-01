from __future__ import annotations
from datetime import datetime

from pydantic import BaseModel, Field


class DataPoint(BaseModel):
    """Representa um único ponto de dados em uma série temporal."""
    timestamp: datetime
    value: float


class Metric(BaseModel):
    """
    Representa uma série temporal completa de uma métrica.

    Este modelo de domínio abstrai a estrutura de dados de um sistema de
    monitoramento (como Prometheus), permitindo que o núcleo da aplicação
    opere sobre um conceito de 'métrica' bem definido e validado.
    """
    name: str = Field(..., description="O nome da métrica, ex: 'cpu_usage_percent'.")
    labels: dict[str, str] = Field(..., description="Labels que identificam unicamente a série temporal.")
    datapoints: list[DataPoint] = Field(..., description="A lista de pontos de dados ao longo do tempo.")