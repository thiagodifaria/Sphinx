# src/sphinx/adapters/gateways/llm_gemini.py

from __future__ import annotations

import json

import google.generativeai as genai
from google.generativeai.types import GenerationConfig

from app.core.application.ports.gateways.llm import LLMServicePort
from app.core.domain.models.iac import IaCFile
from app.core.domain.models.optimization import OptimizationOpportunity, SuggestedChange


class GeminiAdapter(LLMServicePort):
    """
    Implementação da LLMServicePort utilizando a API do Google Gemini.
    """

    def __init__(self, api_key: str) -> None:
        if not api_key:
            raise ValueError("A chave da API do Google Gemini não foi fornecida.")
        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel("gemini-2.5-flash")

    async def generate_iac(self, prompt: str) -> IaCFile:
        """Gera código Terraform usando o modelo Gemini via API do Google."""
        # ... (Este método permanece inalterado)
        system_prompt = """
        Você é um especialista sênior em Terraform. Sua tarefa é gerar um arquivo HCL
        Terraform completo e válido com base na solicitação do usuário. Sua resposta DEVE ser um objeto JSON
        contendo as chaves "filename" e "content". Não inclua nenhum outro texto ou
        explicação fora do JSON.
        """
        generation_config = GenerationConfig(response_mime_type="application/json")
        full_prompt = f"{system_prompt}\n\nSolicitação do Usuário: {prompt}"
        try:
            response = await self._model.generate_content_async(full_prompt, generation_config=generation_config)
            data = json.loads(response.text)
            return IaCFile(**data)
        except Exception as e:
            return IaCFile(filename="error.tf", content=f"# Erro ao gerar código: {e}")

    async def generate_solution_for_opportunity(
        self, opportunity: OptimizationOpportunity
    ) -> SuggestedChange:
        """Gera um arquivo IaC completo como solução para uma oportunidade."""
        # A engenharia de prompt agora pede um arquivo completo, não um diff.
        # Isso torna a sugestão diretamente aplicável e mais robusta.
        system_prompt = """
        Você é um especialista em otimização de nuvem e Terraform. Sua tarefa é analisar
        um problema de infraestrutura e gerar um arquivo Terraform completo e válido que resolva o problema.
        Sua resposta DEVE ser um objeto JSON contendo as chaves "impact_assessment"
        (uma breve análise do impacto da mudança) e "suggested_iac_file" (um objeto JSON
        com as chaves "filename" e "content" para o arquivo Terraform).
        """
        context = f"""
        Problema Detectado: {opportunity.title}
        Descrição: {opportunity.description}
        Recurso Afetado: {opportunity.resource_address}
        Com base nestas informações, gere a solução em formato JSON.
        """
        generation_config = GenerationConfig(response_mime_type="application/json")
        full_prompt = f"{system_prompt}\n\nContexto do Problema:\n{context}"

        try:
            response = await self._model.generate_content_async(full_prompt, generation_config=generation_config)
            data = json.loads(response.text)
            # O Pydantic validará a estrutura aninhada do JSON para nós.
            return SuggestedChange(**data)
        except Exception as e:
            print(f"Erro na API do Gemini ao gerar solução: {e}")
            return SuggestedChange(
                impact_assessment="Falha ao gerar sugestão.",
                suggested_iac_file=IaCFile(filename="error.tf", content=f"# Erro: {e}")
            )