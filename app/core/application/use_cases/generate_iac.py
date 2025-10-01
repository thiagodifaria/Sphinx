from __future__ import annotations

from app.core.application.ports.gateways import LLMServicePort
from app.core.domain.models.iac import IaCFile


class GenerateIacUseCase:
    """
    Orquestra a geração de um arquivo IaC a partir de um prompt do utilizador.
    """

    def __init__(self, llm_service: LLMServicePort) -> None:
        self._llm_service = llm_service

    async def execute(self, prompt: str) -> IaCFile:
        """
        Executa o caso de uso de geração de IaC.

        Args:
            prompt: O prompt de entrada fornecido pelo utilizador.

        Returns:
            O arquivo IaC gerado pelo serviço de LLM.
        """
        iac_file = await self._llm_service.generate_iac(prompt)
        return iac_file