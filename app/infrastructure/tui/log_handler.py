from __future__ import annotations
import logging

from textual.app import App
from textual.message import Message


class TuiLogHandler(logging.Handler):
    """
    Um gestor de logging que envia registos como mensagens para a TUI.

    Isto permite que qualquer módulo use o logger padrão do Python para enviar
    mensagens para a interface do utilizador de forma assíncrona.
    """

    class NewLog(Message):
        """Mensagem para transportar um registo de log para a UI."""

        def __init__(self, record: str) -> None:
            self.record = record
            super().__init__()

    def __init__(self, app: App):
        super().__init__()
        self.app = app

    def emit(self, record: logging.LogRecord) -> None:
        """
        Chamado pelo sistema de logging para cada novo registo.

        Formata o registo e posta-o como uma mensagem thread-safe para a app Textual.
        """
        log_message = self.format(record)
        self.app.post_message(self.NewLog(log_message))