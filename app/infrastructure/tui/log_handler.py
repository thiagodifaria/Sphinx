# src/sphinx/infrastructure/tui/log_handler.py

from __future__ import annotations
import logging

from textual.app import App
from textual.message import Message


class TuiLogHandler(logging.Handler):
    """
    Um handler de logging que envia registros como mensagens para a TUI do Textual.

    Isso desacopla a lógica de logging do código da aplicação da UI. Qualquer
    módulo pode simplesmente usar o logger padrão do Python, e este handler
    interceptará as mensagens e as encaminhará para a TUI de forma assíncrona.
    """

    class NewLog(Message):
        """Mensagem customizada do Textual para transportar um registro de log."""
        def __init__(self, record: str) -> None:
            self.record = record
            super().__init__()

    def __init__(self, app: App):
        super().__init__()
        self.app = app

    def emit(self, record: logging.LogRecord) -> None:
        """Chamado pelo sistema de logging para cada novo registro."""
        log_message = self.format(record)
        # post_message é thread-safe e pode ser chamado de qualquer lugar.
        self.app.post_message(self.NewLog(log_message))