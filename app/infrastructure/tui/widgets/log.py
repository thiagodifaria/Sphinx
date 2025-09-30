# src/sphinx/infrastructure/tui/widgets/log_viewer.py

from __future__ import annotations

from textual.widgets import RichLog

from app.infrastructure.tui.log_handler import TuiLogHandler


class LogViewer(RichLog):
    """Um widget para exibir logs em tempo real na TUI."""

    def __init__(self, **kwargs) -> None:
        # highlight=True ativa o syntax highlighting para formatos como JSON.
        super().__init__(wrap=True, highlight=True, **kwargs)

    def on_mount(self) -> None:
        """Define o título do painel de log."""
        self.border_title = "Logs da Aplicação"

    def on_tui_log_handler_new_log(self, message: TuiLogHandler.NewLog) -> None:
        """Ouve a mensagem customizada do nosso handler e escreve no log."""
        self.write(message.record)