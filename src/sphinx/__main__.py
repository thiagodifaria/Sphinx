# src/sphinx/__main__.py

from src.sphinx.infrastructure import cli
from src.sphinx.infrastructure.di.containers import Container


async def initialize_dependencies(container: Container) -> None:
    """Função assíncrona para inicializar dependências que requerem I/O."""
    # Inicializa o repositório de histórico (cria a tabela se necessário)
    history_repo = await container.history_repository()
    await history_repo.initialize()

def bootstrap() -> None:
    """Inicializa e configura a aplicação antes da execução."""
    container = Container()
    # A classe Settings agora gerencia o carregamento de .env e variáveis de ambiente.
    
    container.wire(
        modules=[
            cli,
            "src.sphinx.infrastructure.tui.screens.chat_screen",
            "src.sphinx.infrastructure.tui.screens.dashboard_screen",
        ]
    )
    
    # O asyncio.run foi removido daqui para ser gerenciado pela TUI.
    # A inicialização do banco de dados será chamada no on_mount do app.
    # Por agora, a primeira escrita criará o banco e a tabela.
    
    cli.app()

if __name__ == "__main__":
    bootstrap()