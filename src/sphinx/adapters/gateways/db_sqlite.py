# src/sphinx/adapters/gateways/db_sqlite.py

from __future__ import annotations

import aiosqlite

from src.sphinx.core.application.ports.gateways.history import HistoryRepositoryPort
from src.sphinx.core.domain.models.history import ActionRecord


class SQLiteHistoryRepository(HistoryRepositoryPort):
    """
    Implementação da HistoryRepositoryPort que utiliza um banco de dados SQLite.

    Este adaptador encapsula toda a lógica de interação com o SQLite, como
    queries SQL e gerenciamento de conexão, mantendo o resto da aplicação
    agnóstico ao banco de dados específico utilizado.
    """
    def __init__(self, db_path: str):
        self._db_path = db_path

    async def initialize(self) -> None:
        """Cria a tabela de histórico se ela não existir."""
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS action_history (
                    opportunity_id TEXT PRIMARY KEY,
                    applied_at TEXT NOT NULL,
                    resource_address TEXT NOT NULL,
                    opportunity_title TEXT NOT NULL,
                    applied_iac_content TEXT NOT NULL
                )
            """)
            await db.commit()

    async def add_record(self, record: ActionRecord) -> None:
        """Insere um novo ActionRecord no banco de dados."""
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                """
                INSERT INTO action_history (
                    opportunity_id, applied_at, resource_address,
                    opportunity_title, applied_iac_content
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    str(record.opportunity_id),
                    record.applied_at.isoformat(),
                    record.resource_address,
                    record.opportunity_title,
                    record.applied_iac_content,
                ),
            )
            await db.commit()