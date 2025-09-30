# test_gemini.py

import os
import asyncio
import google.generativeai as genai
from dotenv import load_dotenv
import time

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

async def run_gemini_test():
    """
    Executa um teste simples e isolado de requisição para a API do Gemini.
    """
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        print("ERRO: Chave de API 'GOOGLE_API_KEY' não encontrada no arquivo .env!")
        return

    print("1. Configurando a API do Gemini...")
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        print("   - Configuração bem-sucedida.")
    except Exception as e:
        print(f"   - ERRO na configuração: {e}")
        return

    prompt = "Olá, mundo! Responda apenas com 'OK'."
    print(f"\n2. Enviando um prompt simples para o modelo: '{prompt}'")
    print("   - Aguardando resposta da API...")

    start_time = time.time()
    try:
        # Usamos um timeout de 60 segundos na requisição
        response = await asyncio.wait_for(
            model.generate_content_async(prompt),
            timeout=60.0
        )
        end_time = time.time()
        print("\n--- SUCESSO! ---")
        print(f"Resposta recebida em {end_time - start_time:.2f} segundos.")
        print(f"Texto da resposta: {response.text}")

    except asyncio.TimeoutError:
        end_time = time.time()
        print("\n--- FALHA ---")
        print(f"A API não respondeu em {end_t-ime - start_time:.2f} segundos (Timeout).")
        print("Isso confirma que o problema é de conexão/rede ou lentidão na API, e não no código do Sphinx.")

    except Exception as e:
        end_time = time.time()
        print("\n--- FALHA ---")
        print(f"Ocorreu um erro inesperado após {end_time - start_time:.2f} segundos:")
        print(e)

if __name__ == "__main__":
    asyncio.run(run_gemini_test())