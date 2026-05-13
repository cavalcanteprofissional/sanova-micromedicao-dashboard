"""
Pipeline RAG: Constroi o chain de busca e geracao de respostas
sem dependencias langchain pesadas — usa apenas huggingface_hub + numpy.
"""

import os
import re
import numpy as np
import pandas as pd
from dataclasses import dataclass

HF_TOKEN = os.getenv("HF_TOKEN", "")

EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

SYSTEM_PROMPT = """Voce e um assistente especializado em analise de sistemas comerciais
de saneamento, com foco em micromedicao, deteccao de perdas comerciais e gestao de receita.

Responda SOMENTE com base nas informacoes fornecidas no contexto abaixo.
Se a pergunta nao puder ser respondida com o contexto disponivel, diga:
"Nao tenho informacoes suficientes na base de dados para responder esta pergunta.
Posso ajudar com analises sobre consumo, faturamento, hidrometros, anomalias ou
recuperacao de receita desta base de dados."

Seja tecnico mas didatico. Use numeros concretos quando disponiveis.
Ao citar valores financeiros, use formato brasileiro (R$ 1.234,56).
Ao citar volumes, use m3.

CONTEXTO RELEVANTE:
{context}

HISTORICO DA CONVERSA:
{chat_history}

PERGUNTA: {question}
RESPOSTA:"""


def _simple_split(text: str, chunk_size: int = 800, overlap: int = 100) -> list[str]:
    """Split plain text into chunks without langchain."""
    if not text.strip():
        return []
    separators = ["\n\n", "\n", ". ", "?", "!", " "]
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        for sep in separators:
            pos = text.rfind(sep, start, end)
            if pos > start:
                end = pos + len(sep)
                break
        chunks.append(text[start:end].strip())
        start = end - overlap
    return [c for c in chunks if c]


@dataclass
class TextChunk:
    """Representa um chunk de texto com seu embedding."""
    page_content: str
    embedding: np.ndarray | None = None


class SimpleEmbeddings:
    """Embeddings via HuggingFace Inference API — 100% HTTP, sem torch/sentence-transformers."""

    def __init__(self, model: str, token: str = ""):
        from huggingface_hub import InferenceClient
        self.model = model
        self.client = InferenceClient(token=token) if token else InferenceClient()

    def embed(self, text: str) -> np.ndarray:
        result = self.client.feature_extraction(text, model=self.model)
        arr = np.array(result)
        return arr / np.linalg.norm(arr)

    def embed_batch(self, texts: list[str]) -> list[np.ndarray]:
        return [self.embed(t) for t in texts]


class SimpleVectorStore:
    """Vector store em memoria com busca por similaridade cosseno — sem InMemoryVectorStore langchain."""

    def __init__(self, chunks: list[TextChunk], embeddings: SimpleEmbeddings):
        self._chunks = chunks
        self._embeddings = embeddings
        self._indexed = False

    def _ensure_indexed(self):
        if not self._indexed:
            embedded = self._embeddings.embed_batch([c.page_content for c in self._chunks])
            for chunk, emb in zip(self._chunks, embedded):
                chunk.embedding = emb
            self._indexed = True

    def similarity_search(self, query: str, k: int = 4) -> list[TextChunk]:
        self._ensure_indexed()
        query_emb = self._embeddings.embed(query)
        scores = []
        for chunk in self._chunks:
            if chunk.embedding is None:
                continue
            score = float(np.dot(query_emb, chunk.embedding))
            scores.append((score, chunk))
        scores.sort(key=lambda x: x[0], reverse=True)
        return [chunk for _, chunk in scores[:k]]


@dataclass
class UserMessage:
    content: str


@dataclass
class AssistantMessage:
    content: str


class SimpleConversationalRAG:
    """RAG chain simples com historico de chat — 100% plain Python, sem langchain."""

    def __init__(self, llm, retriever: SimpleVectorStore):
        self._llm = llm
        self._retriever = retriever
        self._chat_history: list = []

    def _format_history(self) -> str:
        if not self._chat_history:
            return "(sem historico)"
        lines = []
        for msg in self._chat_history:
            if isinstance(msg, UserMessage):
                lines.append(f"Usuario: {msg.content}")
            elif isinstance(msg, AssistantMessage):
                lines.append(f"Assistente: {msg.content}")
        return "\n".join(lines)

    def invoke(self, question: str) -> dict:
        docs = self._retriever.similarity_search(question, k=4)
        context = "\n\n".join(doc.page_content for doc in docs)
        history_str = self._format_history()

        prompt = SYSTEM_PROMPT.format(context=context, chat_history=history_str, question=question)
        answer = self._llm.invoke(prompt)
        if hasattr(answer, "strip"):
            answer = answer.strip()

        self._chat_history.append(UserMessage(content=question))
        self._chat_history.append(AssistantMessage(content=answer))
        return {"answer": answer}

    def clear_history(self):
        self._chat_history.clear()


def build_rag_chain(llm, df: pd.DataFrame | None = None):
    """
    Constroi e retorna um SimpleConversationalRAG com RAG.
    Sem nenhuma dependencia langchain*.
    """
    from dashboard.chat.knowledge_base import KNOWLEDGE_BASE_DOCS, generate_dynamic_stats

    docs = list(KNOWLEDGE_BASE_DOCS)

    if df is not None:
        dynamic_stats = generate_dynamic_stats(df)
        if dynamic_stats:
            docs.append(dynamic_stats)

    all_chunks: list[TextChunk] = []
    for doc in docs:
        parts = _simple_split(doc, chunk_size=800, overlap=100)
        for part in parts:
            if part.strip():
                all_chunks.append(TextChunk(page_content=part.strip()))

    embeddings = SimpleEmbeddings(model=EMBEDDING_MODEL, token=HF_TOKEN)
    vectorstore = SimpleVectorStore(all_chunks, embeddings)

    return SimpleConversationalRAG(llm, vectorstore)