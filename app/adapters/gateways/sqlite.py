# src/sphinx/adapters/gateways/db_sqlite.py

from __future__ import annotations
from datetime import datetime
from uuid import UUID
import json

import aiosqlite

from app.core.application.ports.gateways.history import HistoryRepositoryPort
from app.core.application.ports.gateways.workspace import WorkspaceRepositoryPort
from app.core.domain.models.history import ActionRecord
from app.core.domain.models.iac import TerraformBackendConfig
from app.core.domain.models.workspace import Workspace


class SQLiteHistoryRepository(HistoryRepositoryPort):
    """Implementação da HistoryRepositoryPort que utiliza um banco de dados SQLite."""
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

    async def get_all_records(self) -> list[ActionRecord]:
        """Busca e retorna todos os registros do banco de dados."""
        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM action_history ORDER BY applied_at DESC"
            )
            rows = await cursor.fetchall()
            
            return [
                ActionRecord(
                    opportunity_id=UUID(row["opportunity_id"]),
                    applied_at=datetime.fromisoformat(row["applied_at"]),
                    resource_address=row["resource_address"],
                    opportunity_title=row["opportunity_title"],
                    applied_iac_content=row["applied_iac_content"],
                )
                for row in rows
            ]


class SQLiteWorkspaceRepository(WorkspaceRepositoryPort):
    """Implementação da WorkspaceRepositoryPort que utiliza SQLite."""
    def __init__(self, db_path: str):
        self._db_path = db_path

    async def initialize(self) -> None:
        """Cria a tabela de workspaces se ela não existir."""
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS workspaces (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    backend_config_json TEXT NOT NULL
                )
            """)
            await db.commit()

    async def add(self, workspace: Workspace) -> None:
        """Salva um novo workspace, serializando o backend_config para JSON."""
        async with aiosqlite.connect(self._db_path) as db:
            backend_json = workspace.backend_config.model_dump_json()
            await db.execute(
                "INSERT INTO workspaces (id, name, backend_config_json) VALUES (?, ?, ?)",
                (str(workspace.id), workspace.name, backend_json),
            )
            await db.commit()

    async def get_all(self) -> list[Workspace]:
        """Busca todos os workspaces e desserializa o backend_config a partir do JSON."""
        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM workspaces ORDER BY name")
            rows = await cursor.fetchall()
            return [
                Workspace(
                    id=UUID(row["id"]),
                    name=row["name"],
                    backend_config=TerraformBackendConfig(**json.loads(row["backend_config_json"]))
                )
                for row in rows
            ]