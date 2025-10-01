from __future__ import annotations

from textual.widgets import RichLog

from app.infrastructure.tui.log_handler import TuiLogHandler


class LogViewer(RichLog):
    """Um widget para exibir logs da aplicação em tempo real na TUI."""

    def __init__(self, **kwargs) -> None:
        super().__init__(wrap=True, highlight=True, **kwargs)

    def on_mount(self) -> None:
        """Define o título do painel de log quando o widget é montado."""
        self.border_title = "Logs da Aplicação"

    def on_tui_log_handler_new_log(self, message: TuiLogHandler.NewLog) -> None:
        """Ouve a mensagem do nosso gestor de log e escreve o registo na TUI."""
        self.write(message.record)