# src/sphinx/adapters/providers/iac_terraform.py

from __future__ import annotations
import asyncio
import re
import tempfile
from pathlib import Path

from src.sphinx.core.application.ports.providers.iac_provider import IaCProviderPort
from src.sphinx.core.domain.models.iac import ApplyResult, ExecutionPlan, ResourceChange, IaCFile


class TerraformAdapter(IaCProviderPort):
    """
    Implementação do IaCProviderPort que interage com o CLI do Terraform.
    """

    async def plan(self, iac_file: IaCFile) -> ExecutionPlan:
        with tempfile.TemporaryDirectory() as temp_dir:
            work_dir = Path(temp_dir)
            (work_dir / iac_file.filename).write_text(iac_file.content)

            await self._run_command("terraform init -input=false -no-color", work_dir)

            stdout, stderr, exit_code = await self._run_command(
                "terraform plan -input=false -no-color -detailed-exitcode", work_dir
            )
            
            if exit_code == 1:
                return ExecutionPlan(changes=[], raw_output=f"Erro no Terraform:\n{stderr}")

            changes = self._parse_plan_output(stdout)
            return ExecutionPlan(changes=changes, raw_output=stdout)

    async def apply(self, iac_file: IaCFile) -> ApplyResult:
        """
        Executa 'terraform apply' de forma não-interativa em um diretório isolado.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            work_dir = Path(temp_dir)
            (work_dir / iac_file.filename).write_text(iac_file.content)

            await self._run_command("terraform init -input=false -no-color", work_dir)

            # A flag '-auto-approve' é essencial para a automação, mas deve ser usada
            # com cuidado, pois aplica mudanças sem confirmação manual.
            # O fluxo "plan -> review -> apply" na TUI serve como essa confirmação.
            stdout, stderr, exit_code = await self._run_command(
                "terraform apply -input=false -no-color -auto-approve", work_dir
            )

            success = exit_code == 0
            output = stdout if success else f"Erro no Terraform:\n{stderr}"
            return ApplyResult(success=success, raw_output=output)

    async def _run_command(self, command: str, cwd: Path) -> tuple[str, str, int]:
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd,
        )
        stdout, stderr = await process.communicate()
        return stdout.decode(), stderr.decode(), process.returncode or 0

    def _parse_plan_output(self, output: str) -> list[ResourceChange]:
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