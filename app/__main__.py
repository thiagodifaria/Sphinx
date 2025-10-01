import asyncio
import logging

from app.infrastructure import cli
from app.infrastructure.di.containers import Container

logger = logging.getLogger(__name__)


async def initialize_dependencies(container: Container) -> None:
    """Inicializa dependências assíncronas, como conexões a bases de dados."""
    logger.info("A inicializar dependências...")

    history_repo = container.history_repository()
    await history_repo.initialize()

    workspace_repo = container.workspace_repository()
    await workspace_repo.initialize()

    plugin_manager = container.plugin_manager()
    plugin_manager.discover_and_load()

    logger.info("Dependências inicializadas com sucesso.")


def bootstrap() -> None:
    """Configura o contentor de DI, inicializa e executa a aplicação."""
    container = Container()
    container.config.from_dict({"mock_data": "true"})

    # Liga o contentor aos módulos que necessitam de injeção de dependência.
    container.wire(
        modules=[
            "app.infrastructure.cli",
            "app.infrastructure.tui.screens.chat",
            "app.infrastructure.tui.screens.dashboard",
            "app.infrastructure.tui.screens.history",
            "app.infrastructure.tui.screens.workspace",
            __name__,
        ]
    )

    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
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