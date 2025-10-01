from __future__ import annotations
import logging

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import TabbedContent, TabPane, Footer, Header

from app.infrastructure.tui.log_handler import TuiLogHandler
from app.infrastructure.tui.screens.chat import ChatScreen
from app.infrastructure.tui.screens.dashboard import DashboardScreen
from app.infrastructure.tui.screens.history import HistoryScreen
from app.infrastructure.tui.screens.workspace import WorkspaceScreen
from app.infrastructure.tui.widgets.log import LogViewer


class SphinxApp(App):
    """A aplicação TUI principal do Sphinx."""

    CSS_PATH = ["assets/style.css"]
    BINDINGS = [
        ("ctrl+t", "toggle_tabs", "Abas"),
        ("ctrl+q", "quit", "Sair"),
    ]

    def compose(self) -> ComposeResult:
        """Compõe a UI com abas e um painel de log persistente."""
        yield Header()
        with Vertical(id="app-container"):
            with TabbedContent(initial="chat_tab") as tabs:
                tabs.id = "main-tabs"
                with TabPane("Chat de Geração", id="chat_tab"):
                    yield ChatScreen()
                with TabPane("Dashboard", id="dashboard_tab"):
                    yield DashboardScreen()
                with TabPane("Histórico", id="history_tab"):
                    yield HistoryScreen()
                with TabPane("Workspaces", id="workspaces_tab"):
                    yield WorkspaceScreen()
            yield LogViewer(classes="box")
        yield Footer()

    def on_mount(self) -> None:
        """Configura o gestor de logging da TUI ao iniciar a aplicação."""
        handler = TuiLogHandler(self)
        logging.basicConfig(
            level=logging.INFO,
            handlers=[handler],
            force=True,
        )
        logging.info("Sphinx TUI iniciada e pronta.")

    def action_toggle_tabs(self) -> None:
        """Ação para focar no conteúdo das abas."""
        self.query_one("#main-tabs").focus()