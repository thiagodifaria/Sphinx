# src/sphinx/adapters/providers/iac_terraform.py

from __future__ import annotations
import asyncio
import logging
import re
import tempfile
from pathlib import Path
from contextlib import asynccontextmanager
import locale  # Adicionado para obter a codificação correta

from app.core.application.ports.providers.iac_provider import IaCProviderPort
from app.core.domain.models.iac import (
    ApplyResult, ExecutionPlan, ResourceChange, TerraformConfiguration
)

logger = logging.getLogger(__name__)


class TerraformAdapter(IaCProviderPort):
    """
    Implementação do IaCProviderPort que interage com o CLI do Terraform.
    """

    @asynccontextmanager
    async def _work_dir(self, config: TerraformConfiguration):
        """
        Gerencia um diretório de trabalho, escrevendo o main.tf e, opcionalmente,
        um arquivo de configuração de backend.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            work_dir = Path(temp_dir)
            (work_dir / config.main_file.filename).write_text(config.main_file.content, encoding="utf-8")

            if config.backend_config:
                backend_content = f"""
terraform {{
  backend "s3" {{}}
}}
"""
                (work_dir / "backend.tf").write_text(backend_content, encoding="utf-8")
            
            yield work_dir

    async def _initialize_terraform(self, config: TerraformConfiguration, work_dir: Path):
        """Inicializa o Terraform, configurando o backend se necessário."""
        init_command = "terraform init -input=false -no-color"
        if backend_config := config.backend_config:
            # Adiciona os parâmetros de configuração do backend para uma inicialização não-interativa.
            init_command += (
                f' -backend-config="bucket={backend_config.bucket}"'
                f' -backend-config="key={backend_config.key}"'
                f' -backend-config="region={backend_config.region}"'
            )
        await self._run_command(init_command, work_dir)

    async def plan(self, config: TerraformConfiguration) -> ExecutionPlan:
        """Executa 'terraform plan' em um diretório de trabalho isolado."""
        async with self._work_dir(config) as work_dir:
            await self._initialize_terraform(config, work_dir)
            stdout, stderr, exit_code = await self._run_command(
                "terraform plan -input=false -no-color -detailed-exitcode", work_dir
            )
            
            if exit_code == 1:
                error_message = f"Erro no Terraform Plan:\n{stderr}"
                logger.error(error_message)
                return ExecutionPlan(changes=[], raw_output=error_message)

            changes = self._parse_plan_output(stdout)
            return ExecutionPlan(changes=changes, raw_output=stdout)

    async def apply(self, config: TerraformConfiguration) -> ApplyResult:
        """Executa 'terraform apply' em um diretório de trabalho isolado."""
        async with self._work_dir(config) as work_dir:
            await self._initialize_terraform(config, work_dir)
            stdout, stderr, exit_code = await self._run_command(
                "terraform apply -input=false -no-color -auto-approve", work_dir
            )

            success = exit_code == 0
            if success:
                logger.info("Terraform apply executado com sucesso.")
                output = stdout
            else:
                error_message = f"Erro no Terraform Apply:\n{stderr}"
                logger.error(error_message)
                output = error_message
                
            return ApplyResult(success=success, raw_output=output)

    async def _run_command(self, command: str, cwd: Path) -> tuple[str, str, int]:
        """Executa um comando de shell e loga sua saída."""
        logger.info(f"Executando comando em '{cwd}': {command}")
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd,
        )
        stdout_bytes, stderr_bytes = await process.communicate()
        
        # Usa a codificação preferida do sistema para decodificar a saída do terminal,
        # o que é mais seguro no Windows.
        encoding = locale.getpreferredencoding(False)
        stdout = stdout_bytes.decode(encoding, errors="replace")
        stderr = stderr_bytes.decode(encoding, errors="replace")
        
        if stdout:
            logger.debug(f"Saída (stdout):\n{stdout}")
        if stderr:
            logger.warning(f"Saída de erro (stderr):\n{stderr}")
        
        return stdout, stderr, process.returncode or 0

    def _parse_plan_output(self, output: str) -> list[ResourceChange]:
        """Extrai informações de mudança da saída de texto do 'terraform plan'."""
        changes: list[ResourceChange] = []
        pattern = re.compile(r"^\s*(?:#|~|-)\s+([\w\.\-\[\]\"]+)\s+(?:will be|must be|{|~)")

        for line in output.splitlines():
            match = pattern.match(line)
            if not match:
                continue

            address = match.group(1).replace('"', "")
            action = "update"
            if "will be created" in line or line.strip().startswith("#"):
                 action = "create"
            if "will be destroyed" in line:
                action = "delete"
            if "must be replaced" in line:
                action = "replace"
            
            if not any(c.address == address for c in changes):
                changes.append(ResourceChange(address=address, action=action))
        
        return changes