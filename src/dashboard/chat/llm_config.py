"""
Configuracao do LLM para o chatbot RAG.
Usa HuggingFace Inference Providers com Llama-3.1-8B-Instruct (gratuito via credits).
"""

import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env.local'))

LLM_MODEL = "meta-llama/Llama-3.1-8B-Instruct"


def get_api_key() -> str | None:
    """Retorna o token da API HuggingFace, ou None se nao estiver configurado."""
    return os.getenv("HF_TOKEN")


def has_api_key() -> bool:
    """Verifica se o token da API HuggingFace esta configurado."""
    key = get_api_key()
    return bool(key and key != "your_hf_token_here")


def get_llm():
    """
    Retorna uma instancia configurada do ChatHuggingFace.
    Requer HF_TOKEN configurado em .env.local.
    Usa Inference Providers com routing automatico (provider="auto").
    """
    from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

    api_key = get_api_key()
    if not api_key or api_key == "your_hf_token_here":
        raise ValueError("HF_TOKEN nao configurado. Edite o arquivo .env.local.")

    endpoint = HuggingFaceEndpoint(
        repo_id=LLM_MODEL,
        max_new_tokens=1024,
        temperature=0.1,
        huggingfacehub_api_token=api_key,
        provider="auto",
    )

    return ChatHuggingFace(llm=endpoint)
