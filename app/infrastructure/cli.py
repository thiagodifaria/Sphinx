import typer
from rich.console import Console

from app.infrastructure.tui.app import SphinxApp

app = typer.Typer(
    name="sphinx",
    help="Sphinx: Plataforma de engenharia de nuvem autónoma no seu terminal.",
    add_completion=False,
)

console = Console()


@app.command()
def run() -> None:
    """Inicia a Interface de Utilizador de Terminal (TUI) do Sphinx."""
    sphinx_app = SphinxApp()
    sphinx_app.run()