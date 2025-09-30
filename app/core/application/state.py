# src/sphinx/core/application/state.py

from __future__ import annotations
from dataclasses import dataclass, field

from app.core.domain.models.workspace import Workspace


@dataclass
class AppState:
    """
    Mantém o estado global da aplicação em tempo de execução.

    Este objeto, gerenciado como um singleton pelo contêiner de DI, permite que
    diferentes partes da aplicação compartilhem informações de estado, como
    qual workspace está ativo, sem acoplamento direto.
    """
    active_workspace: Workspace | None = field(default=None)