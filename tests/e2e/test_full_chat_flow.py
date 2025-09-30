# tests/e2e/test_full_chat_flow.py

from __future__ import annotations
from unittest.mock import AsyncMock

import pytest

from src.sphinx.core.domain.models.iac import ApplyResult, ExecutionPlan, IaCFile
from src.sphinx.infrastructure.di.containers import Container
from src.sphinx.infrastructure.tui.app import SphinxApp
from src.sphinx.infrastructure.tui.widgets import LogViewer

# Marca todos os testes neste arquivo para serem executados com asyncio
pytestmark = pytest.mark.asyncio


async def test_generate_plan_and_apply_flow():
    """
    Testa o fluxo completo na aba 'Chat', desde a geração do código até a aplicação.

    Este teste valida a integração de todas as camadas da aplicação (TUI, Casos
    de Uso, Adaptadores) para um fluxo de trabalho crítico. Usamos o sistema de
    injeção de dependência para substituir os adaptadores reais por mocks,
    permitindo-nos testar o fluxo interno sem tocar em sistemas externos.
    """
    # Arrange: Preparação dos Mocks e da Injeção de Dependência
    # 1. Cria mocks assíncronos para simular nossos adaptadores.
    mock_gemini_adapter = AsyncMock()
    mock_terraform_adapter = AsyncMock()

    # 2. Configura os valores de retorno dos mocks.
    mock_gemini_adapter.generate_iac.return_value = IaCFile(
        filename="main.tf", content='resource "local_file" "test" {}'
    )
    mock_terraform_adapter.plan.return_value = ExecutionPlan(
        changes=[], raw_output="Plan: 0 to add, 0 to change, 0 to destroy."
    )
    mock_terraform_adapter.apply.return_value = ApplyResult(
        success=True, raw_output="Apply complete!"
    )

    # 3. Usa o recurso 'override' do contêiner de DI para substituir as implementações
    #    reais pelos nossos mocks. Isso só afetará o escopo deste teste.
    container = Container()
    container.gemini_adapter.override(mock_gemini_adapter)
    container.terraform_adapter.override(mock_terraform_adapter)
    
    # É crucial fazer o 'wire' *após* o override para que as injeções usem os mocks.
    container.wire(
        modules=[
            "src.sphinx.infrastructure.cli",
            "src.sphinx.infrastructure.tui.screens.chat_screen",
            "src.sphinx.infrastructure.tui.screens.dashboard_screen",
            "src.sphinx.infrastructure.tui.screens.history_screen",
        ]
    )
    
    app = SphinxApp()

    # Act: Executa a simulação da interação do usuário com a TUI.
    async with app.run_test() as pilot:
        # 1. Simula o usuário digitando um prompt e pressionando Enter.
        await pilot.press("tab") # Navega para a aba de Chat, se necessário
        prompt_input = app.query_one("Input")
        prompt_input.value = "create a test file"
        await pilot.press("enter")
        await pilot.pause() # Aguarda a UI reagir

        # 2. Simula o clique no botão 'Planejar'.
        await pilot.click("#plan-button")
        await pilot.pause()

        # 3. Simula o clique no botão 'Aplicar'.
        await pilot.click("#apply-button")
        await pilot.pause()

    # Assert: Verifica se as chamadas internas ocorreram como esperado.
    # Garante que cada passo na UI disparou a chamada correta ao adaptador mockado.
    mock_gemini_adapter.generate_iac.assert_called_once()
    mock_terraform_adapter.plan.assert_called_once()
    mock_terraform_adapter.apply.assert_called_once()

    # Desfaz o override para não afetar outros testes.
    container.unwire()
    container.gemini_adapter.reset_override()
    container.terraform_adapter.reset_override()