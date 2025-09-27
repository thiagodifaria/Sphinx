# src/sphinx/core/domain/models/history.py

from __future__ import annotations
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ActionRecord(BaseModel):
    """

    Representa um registro de uma ação executada com sucesso pelo Sphinx.
    
    Este objeto de domínio é a unidade fundamental para a persistência do histórico,
    permitindo auditoria e aprendizado futuro sobre as ações tomadas.
    """
    opportunity_id: UUID
    applied_at: datetime = Field(default_factory=datetime.utcnow)
    resource_address: str
    opportunity_title: str
    applied_iac_content: str