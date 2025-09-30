# src/sphinx/core/application/ports/gateways/workspace.py

from __future__ import annotations
from abc import ABC, abstractmethod

from app.core.domain.models.workspace import Workspace


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