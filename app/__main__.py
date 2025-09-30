# src/sphinx/__main__.py

import asyncio
import logging

from app.infrastructure import cli
from app.infrastructure.di.containers import Container

logger = logging.getLogger(__name__)


async def initialize_dependencies(container: Container) -> None:
    """Função assíncrona para inicializar dependências que requerem I/O."""
    logger.info("Inicializando dependências...")
    
    # Adicionado "import asyncio" para a função sleep no provedor mockado
    # Isso é necessário para que a injeção de dependência funcione corretamente
    container.wire(modules=[__name__])
    
    history_repo = container.history_repository()
    await history_repo.initialize()
    
    workspace_repo = container.workspace_repository()
    await workspace_repo.initialize()

    plugin_manager = container.plugin_manager()
    plugin_manager.discover_and_load()

    logger.info("Dependências inicializadas.")
    

def bootstrap() -> None:
    """Inicializa e configura a aplicação antes da execução."""
    container = Container()
    
    container.config.from_dict({"mock_data": "true"})
    
    container.wire(
        modules=[
            "sphinx.infrastructure.cli",
            "sphinx.infrastructure.tui.screens.chat_screen",
            "sphinx.infrastructure.tui.screens.dashboard_screen",
            "sphinx.infrastructure.tui.screens.history_screen",
            "sphinx.infrastructure.tui.screens.workspace_screen",
            __name__,
        ]
    )
    
    try:
        # A injeção de dependência agora é tratada de forma síncrona pelo bootstrap
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(initialize_dependencies(container))
    except Exception as e:
        logging.basicConfig(level=logging.ERROR)
        logger.error(f"Falha ao inicializar dependências: {e}", exc_info=True)
        return

    cli.app()


if __name__ == "__main__":
    bootstrap()