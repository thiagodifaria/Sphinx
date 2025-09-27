# src/sphinx/core/application/use_cases/generate_iac.py

from __future__ import annotations

from src.sphinx.core.application.ports.gateways.llm import LLMServicePort
from src.sphinx.core.domain.models.iac import IaCFile


class GenerateIacUseCase:
    """
    Orquestra a geração de um arquivo IaC a partir de um prompt do usuário.

    Este caso de uso encapsula o fluxo de negócio, dependendo de abstrações (portas)
    para interagir com sistemas externos. Ele não conhece detalhes de implementação
    do LLM, apenas o contrato definido pela LLMServicePort.
    """

    def __init__(self, llm_service: LLMServicePort) -> None:
        self._llm_service = llm_service

    async def execute(self, prompt: str) -> IaCFile:
        """
        Executa o caso de uso de geração de IaC.

        Args:
            prompt: O prompt de entrada fornecido pelo usuário.

        Returns:
            O arquivo IaC gerado pelo serviço de LLM.
        """
        # Futuramente, este método pode incluir lógica adicional, como validação
        # do prompt, enriquecimento com contexto ou tratamento de erros de negócio.
        iac_file = await self._llm_service.generate_iac(prompt)
        return iac_file