# src/sphinx/infrastructure/tui/app.py

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.widgets import TabbedContent, TabPane

from src.sphinx.infrastructure.tui.screens.chat_screen import ChatScreen
from src.sphinx.infrastructure.tui.screens.dashboard_screen import DashboardScreen


class SphinxApp(App):
    """A aplicação TUI principal do Sphinx, agora com abas."""

    CSS_PATH = []
    # Removemos a navegação via BINDINGS e adotamos abas.
    # O 'q' para sair é herdado da Screen, então não é mais necessário aqui.

    def compose(self) -> ComposeResult:
        """Compõe a UI com abas para as diferentes telas."""
        # TabbedContent gerencia a exibição e navegação entre as 'telas'.
        with TabbedContent(initial="chat_tab"):
            with TabPane("Chat de Geração", id="chat_tab"):
                yield ChatScreen()
            with TabPane("Dashboard", id="dashboard_tab"):
                yield DashboardScreen()

    # O método on_mount não é mais necessário aqui, pois cada tela
    # gerencia seu próprio ciclo de vida.