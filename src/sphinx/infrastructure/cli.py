# src/sphinx/infrastructure/cli.py

import typer
from rich.console import Console

from src.sphinx.infrastructure.tui.app import SphinxApp

app = typer.Typer(
    name="sphinx",
    help="Sphinx: Plataforma de engenharia de nuvem autônoma no seu terminal.",
    add_completion=False,
)

console = Console()


@app.command()
def run() -> None:
    """
    Inicia a Interface de Usuário de Terminal (TUI) do Sphinx.
    """
    # Instancia e executa a aplicação Textual, que assume o controle do terminal.
    sphinx_app = SphinxApp()
    sphinx_app.run()


# Adicionar outros comandos como `config`, `version`, etc., futuramente aqui.