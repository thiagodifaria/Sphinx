from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import Button, DataTable, Input, Static
from rich.text import Text

from app.core.application.state import AppState
from app.core.application.use_cases.workspaces import (
    CreateWorkspaceUseCase,
    ListWorkspacesUseCase,
    SetActiveWorkspaceUseCase,
)
from app.core.domain.models.workspace import Workspace
from app.infrastructure.di.containers import Container


class WorkspaceScreen(Static):
    """Um ecrã para gerir e selecionar Workspaces de trabalho."""

    @inject
    def __init__(
        self,
        list_ws_uc: ListWorkspacesUseCase = Provide[Container.list_workspaces_uc],
        create_ws_uc: CreateWorkspaceUseCase = Provide[Container.create_workspaces_uc],
        set_active_ws_uc: SetActiveWorkspaceUseCase = Provide[
            Container.set_active_workspace_uc
        ],
        app_state: AppState = Provide[Container.app_state],
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.list_ws_uc = list_ws_uc
        self.create_ws_uc = create_ws_uc
        self.set_active_ws_uc = set_active_ws_uc
        self.app_state = app_state
        self._workspaces: list[Workspace] = []

    def compose(self) -> ComposeResult:
        with Horizontal(id="ws-container"):
            with Vertical(id="ws-list-container"):
                yield DataTable(id="ws-table", cursor_type="row", zebra_stripes=True)
            with Vertical(id="ws-create-container"):
                yield Input(placeholder="Nome do Workspace", id="ws-name")
                yield Input(placeholder="Nome do Bucket S3", id="ws-bucket")
                yield Input(placeholder="Caminho do State (key)", id="ws-key")
                yield Input(placeholder="Região da AWS", id="ws-region")
                yield Button("Salvar Novo Workspace", id="ws-save", variant="primary")

    async def on_mount(self):
        self.query_one("#ws-list-container").border_title = "Workspaces Salvos"
        self.query_one("#ws-create-container").border_title = "Novo Workspace (Backend S3)"

        table = self.query_one(DataTable)
        table.add_columns("Nome", "Bucket", "Ativo")
        await self._refresh_table()

    async def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "ws-save":
            inputs = self.query(Input)
            name, bucket, key, region = (i.value for i in inputs)
            if all((name, bucket, key, region)):
                await self._refresh_table()
                for i in inputs:
                    i.clear()
                self.app.notify(
                    "Workspace (mock) 'salvo' com sucesso!",
                    title="Sucesso",
                    severity="information",
                )

    def on_data_table_row_selected(self, event: DataTable.RowSelected):
        selected_id = event.row_key.value
        if not selected_id:
            return

        workspace = next(
            (ws for ws in self._workspaces if str(ws.id) == selected_id), None
        )

        if workspace and workspace != self.app_state.active_workspace:
            self.set_active_ws_uc.execute(workspace)
            self.app.notify(f"Workspace '{workspace.name}' ativado.", severity="information")
        else:
            self.set_active_ws_uc.execute(None)
        self._update_active_indicator()

    async def _refresh_table(self):
        self._workspaces = await self.list_ws_uc.execute()
        table = self.query_one(DataTable)
        table.clear()

        if not self._workspaces:
            table.add_row(Text("Nenhum workspace salvo.", style="dim"))
        else:
            for ws in self._workspaces:
                table.add_row(
                    Text(ws.name, style="bold"),
                    ws.backend_config.bucket,
                    "",
                    key=str(ws.id),
                )
        self._update_active_indicator()

    def _update_active_indicator(self):
        table = self.query_one(DataTable)
        for row_key_str in table.rows:
            row_key = str(row_key_str)
            row_ws = next((ws for ws in self._workspaces if str(ws.id) == row_key), None)
            is_active = row_ws is not None and row_ws == self.app_state.active_workspace

            if row_key in table.rows:
                table.update_cell(
                    row_key,
                    "Ativo",
                    Text("✔", style="bold green") if is_active else "",
                )