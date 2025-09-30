# src/sphinx/core/application/use_cases/manage_workspaces.py

from __future__ import annotations

from app.core.application.ports.gateways.workspace import WorkspaceRepositoryPort
from app.core.application.state import AppState
from app.core.domain.models.iac import TerraformBackendConfig
from app.core.domain.models.workspace import Workspace


class CreateWorkspaceUseCase:
    """Caso de uso para criar um novo workspace."""
    def __init__(self, workspace_repo: WorkspaceRepositoryPort):
        self._workspace_repo = workspace_repo

    async def execute(self, name: str, bucket: str, key: str, region: str) -> Workspace:
        backend_config = TerraformBackendConfig(bucket=bucket, key=key, region=region)
        workspace = Workspace(name=name, backend_config=backend_config)
        await self._workspace_repo.add(workspace)
        return workspace


class ListWorkspacesUseCase:
    """Caso de uso para listar todos os workspaces existentes."""
    def __init__(self, workspace_repo: WorkspaceRepositoryPort):
        self._workspace_repo = workspace_repo

    async def execute(self) -> list[Workspace]:
        return await self._workspace_repo.get_all()


class SetActiveWorkspaceUseCase:
    """Caso de uso para definir o workspace ativo no estado da aplicação."""
    def __init__(self, app_state: AppState):
        self._app_state = app_state

    def execute(self, workspace: Workspace | None):
        self._app_state.active_workspace = workspace