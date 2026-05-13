"""
Configuracao do LLM para o chatbot RAG.
Usa HuggingFace Inference Providers com Llama-3.1-8B-Instruct (gratuito via credits).
Implementacao via huggingface_hub.InferenceClient — sem langchain-huggingface.
"""

import os

LLM_MODEL = "meta-llama/Llama-3.1-8B-Instruct"
MAX_NEW_TOKENS = 1024
TEMPERATURE = 0.1


def get_api_key() -> str | None:
    """Retorna o token — via env var (Streamlit Secrets) ou .env.local (local)."""
    # Primeiro: variável de ambiente (Streamlit Secrets expõe como env var)
    token = os.getenv("HF_TOKEN")
    if token:
        return token

    # Segundo: carregar .env.local apenas se existir (ambiente local)
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env.local')
    if os.path.exists(dotenv_path):
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=dotenv_path)
        token = os.getenv("HF_TOKEN")
        if token:
            return token

    # Terceiro: tentar st.secrets (Streamlit Cloud com TOML Secrets)
    try:
        import streamlit as st
        return st.secrets.get("HF_TOKEN")
    except Exception:
        pass

    return None


def has_api_key() -> bool:
    """Verifica se o token da API HuggingFace esta configurado."""
    key = get_api_key()
    return bool(key and key.strip() and key != "your_hf_token_here")


class HuggingFaceLLM:
    """LLM via HuggingFace Inference API — implementa invoke() com Interface simples."""

    def __init__(self, repo_id: str, token: str, max_new_tokens: int = 1024, temperature: float = 0.1):
        from huggingface_hub import InferenceClient
        self.repo_id = repo_id
        self.token = token
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature
        self._client = InferenceClient(token=token)

    def invoke(self, prompt: str) -> str:
        if hasattr(prompt, "to_string"):
            prompt = prompt.to_string()
        elif hasattr(prompt, "messages"):
            lines = []
            for m in prompt.messages:
                label = "Usuario" if "user" in str(m).lower() else "Assistente"
                content = m.content if hasattr(m, "content") else str(m)
                lines.append(f"{label}: {content}")
            prompt = "\n".join(lines)
        response = self._client.chat_completion(
            model=self.repo_id,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=self.max_new_tokens,
            temperature=self.temperature,
            provider="auto",
        )
        return response.choices[0].message.content


def get_llm():
    """
    Retorna uma instancia configurada do HuggingFaceLLM.
    Requer HF_TOKEN configurado em .env.local.
    Usa Inference Providers com routing automatico (provider="auto").
    """
    api_key = get_api_key()
    if not api_key or api_key == "your_hf_token_here":
        raise ValueError("HF_TOKEN nao configurado. Edite o arquivo .env.local.")

    return HuggingFaceLLM(repo_id=LLM_MODEL, token=api_key, max_new_tokens=MAX_NEW_TOKENS, temperature=TEMPERATURE)
