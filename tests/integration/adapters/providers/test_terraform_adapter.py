# tests/integration/adapters/providers/test_terraform_adapter.py

from __future__ import annotations
from pathlib import Path

import pytest

from src.sphinx.adapters.providers.iac_terraform import TerraformAdapter
from src.sphinx.core.domain.models.iac import IaCFile

# Pré-requisito: O CLI do Terraform deve estar instalado e no PATH para estes testes.

TERRAFORM_CONFIG_LOCAL_FILE = """
resource "local_file" "example" {
  content  = "Sphinx integration test!"
  filename = "${path.module}/test.txt"
}
"""

@pytest.fixture
def terraform_adapter() -> TerraformAdapter:
    """Fornece uma instância do adaptador do Terraform."""
    return TerraformAdapter()


@pytest.fixture
def local_iac_file() -> IaCFile:
    """Fornece um objeto IaCFile com uma configuração local simples."""
    return IaCFile(filename="main.tf", content=TERRAFORM_CONFIG_LOCAL_FILE)


async def test_terraform_adapter_plan_parses_changes(
    terraform_adapter: TerraformAdapter, local_iac_file: IaCFile
):
    """
    Testa se o método 'plan' invoca o Terraform e parseia a saída corretamente.
    Este teste valida a interação com o processo externo e a lógica de parsing
    de texto do nosso adaptador.
    """
    # Act
    execution_plan = await terraform_adapter.plan(local_iac_file)

    # Assert
    assert "Erro no Terraform" not in execution_plan.raw_output
    assert "Plan: 1 to add, 0 to change, 0 to destroy." in execution_plan.raw_output
    assert len(execution_plan.changes) == 1
    assert execution_plan.changes[0].address == "local_file.example"
    assert execution_plan.changes[0].action == "create"


async def test_terraform_adapter_apply_creates_file(
    terraform_adapter: TerraformAdapter, local_iac_file: IaCFile, tmp_path: Path
):
    """
    Testa se o método 'apply' executa com sucesso e produz o artefato esperado.

    Para este teste, trocamos o diretório temporário padrão do adaptador por um
    diretório de teste fornecido pelo pytest (tmp_path), permitindo-nos
    verificar se o arquivo foi realmente criado no sistema de arquivos.
    """
    # Arrange
    # Sobrescrevemos o método de execução para forçar o uso de um diretório que podemos inspecionar.
    async def run_in_tmp_path(command: str, cwd: Path) -> tuple[str, str, int]:
        return await terraform_adapter._run_command(command, tmp_path)
    
    # Monkeypatching: substitui temporariamente um método de um objeto
    terraform_adapter._run_command_in_dir = run_in_tmp_path
    
    (tmp_path / local_iac_file.filename).write_text(local_iac_file.content)

    # Act
    apply_result = await terraform_adapter.apply(local_iac_file)
    
    # Assert
    assert apply_result.success is True
    assert "Apply complete!" in apply_result.raw_output
    assert (tmp_path / "test.txt").exists()
    assert (tmp_path / "test.txt").read_text() == "Sphinx integration test!"