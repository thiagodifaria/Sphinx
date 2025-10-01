from __future__ import annotations
import json
import logging

import google.generativeai as genai
from google.generativeai.types import GenerationConfig

from app.core.application.ports.gateways import LLMServicePort
from app.core.domain.models.iac import IaCFile
from app.core.domain.models.optimization import (
    OptimizationOpportunity,
    SuggestedChange,
)

logger = logging.getLogger(__name__)


class GeminiAdapter(LLMServicePort):
    """Implementa a LLMServicePort utilizando a API do Google Gemini."""

    def __init__(self, api_key: str) -> None:
        if not api_key:
            raise ValueError("A chave da API do Google Gemini não foi fornecida.")
        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel("gemini-2.5-flash")

    async def generate_iac(self, prompt: str) -> IaCFile:
        """Gera um arquivo de Infraestrutura como Código a partir de um prompt."""
        system_prompt = """
        Você é um especialista sénior em Terraform. A sua tarefa é gerar um arquivo HCL
        Terraform completo e válido com base na solicitação do utilizador. A sua resposta DEVE ser um objeto JSON
        contendo as chaves "filename" e "content". Não inclua nenhum outro texto ou
        explicação fora do JSON.
        """
        generation_config = GenerationConfig(response_mime_type="application/json")
        full_prompt = f"{system_prompt}\n\nSolicitação do Utilizador: {prompt}"
        try:
            response = await self._model.generate_content_async(
                full_prompt, generation_config=generation_config
            )
            data = json.loads(response.text)
            return IaCFile(**data)
        except Exception as e:
            logger.error(f"Erro na API do Gemini ao gerar IaC: {e}")
            return IaCFile(filename="error.tf", content=f"# Erro ao gerar código: {e}")

    async def generate_solution_for_opportunity(
        self, opportunity: OptimizationOpportunity
    ) -> SuggestedChange:
        """Gera uma solução de código para uma oportunidade de otimização."""
        system_prompt = """
        Você é um especialista em otimização de nuvem e Terraform. A sua tarefa é analisar
        um problema de infraestrutura e gerar um arquivo Terraform completo e válido que resolva o problema.
        A sua resposta DEVE ser um objeto JSON contendo as chaves "impact_assessment"
        (uma breve análise do impacto da mudança) e "suggested_iac_file" (um objeto JSON
        com as chaves "filename" e "content" para o arquivo Terraform).
        """
        context = f"""
        Problema Detetado: {opportunity.title}
        Descrição: {opportunity.description}
        Recurso Afetado: {opportunity.resource_address}
        Com base nestas informações, gere a solução em formato JSON.
        """
        generation_config = GenerationConfig(response_mime_type="application/json")
        full_prompt = f"{system_prompt}\n\nContexto do Problema:\n{context}"

        try:
            response = await self._model.generate_content_async(
                full_prompt, generation_config=generation_config
            )
            data = json.loads(response.text)
            return SuggestedChange(**data)
        except Exception as e:
            logger.error(f"Erro na API do Gemini ao gerar solução: {e}")
            return SuggestedChange(
                impact_assessment="Falha ao gerar sugestão.",
                suggested_iac_file=IaCFile(filename="error.tf", content=f"# Erro: {e}"),
            )