"""
Pipeline RAG: Constroi o chain de busca e geracao de respostas
usando LangChain Core + InMemoryVectorStore + HuggingFace Inference API embeddings.
"""

import os
import pandas as pd
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables import RunnableSequence
from langchain_core.embeddings import Embeddings
from langchain_community.vectorstores import InMemoryVectorStore

EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env.local"))
HF_TOKEN = os.getenv("HF_TOKEN", "")


class HuggingFaceInferenceEmbeddings(Embeddings):
    """Embeddings via HuggingFace Inference API — sem torch, sem sentence-transformers."""

    def __init__(self, model: str, token: str = ""):
        from huggingface_hub import InferenceClient
        self.model = model
        self.client = InferenceClient(token=token) if token else InferenceClient()

    def embed_query(self, text: str) -> list:
        result = self.client.feature_extraction(text, model=self.model)
        if hasattr(result, "tolist"):
            return result.tolist()
        return list(result)

    def embed_documents(self, texts: list) -> list:
        return [self.embed_query(t) for t in texts]


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


class SimpleConversationalRAG:
    """RAG chain simples com historico de chat usando LangChain Core primitives."""

    def __init__(self, llm, retriever):
        self._llm = llm
        self._retriever = retriever
        self._chat_history: list = []
        self._chain = self._build_chain()

    def _format_chat_history(self, history: list) -> str:
        if not history:
            return "(sem historico)"
        lines = []
        for msg in history:
            if isinstance(msg, HumanMessage):
                lines.append(f"Usuario: {msg.content}")
            elif isinstance(msg, AIMessage):
                lines.append(f"Assistente: {msg.content}")
        return "\n".join(lines)

    def _build_chain(self):
        def format_inputs(question):
            docs = self._retriever.invoke(question)
            context = "\n\n".join(doc.page_content for doc in docs)
            return {
                "question": question,
                "context": context,
                "chat_history": self._format_chat_history(self._chat_history),
            }

        prompt = PromptTemplate(
            input_variables=["context", "chat_history", "question"],
            template=SYSTEM_PROMPT
        )

        chain = RunnableSequence(
            format_inputs,
            prompt,
            self._llm,
            StrOutputParser()
        )
        return chain

    def invoke(self, question_input: str) -> dict:
        answer = self._chain.invoke(question_input)
        self._chat_history.append(HumanMessage(content=question_input))
        self._chat_history.append(AIMessage(content=answer))
        return {"answer": answer}

    def clear_history(self):
        self._chat_history.clear()


def build_rag_chain(llm, df: pd.DataFrame | None = None):
    """
    Constroi e retorna um SimpleConversationalRAG com RAG.

    Args:
        llm: Instancia configurada do ChatHuggingFace.
        df: DataFrame opcional com os dados para estatisticas dinamicas.

    Returns:
        SimpleConversationalRAG pronto para uso.
    """
    from dashboard.chat.knowledge_base import KNOWLEDGE_BASE_DOCS, generate_dynamic_stats

    docs = list(KNOWLEDGE_BASE_DOCS)

    if df is not None:
        dynamic_stats = generate_dynamic_stats(df)
        if dynamic_stats:
            docs.append(dynamic_stats)

    from langchain_text_splitters import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", "?", "!", " "]
    )
    chunks = splitter.create_documents(docs)

    embeddings = HuggingFaceInferenceEmbeddings(
        model=EMBEDDING_MODEL,
        token=HF_TOKEN
    )

    vectorstore = InMemoryVectorStore.from_documents(chunks, embeddings)
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 4}
    )

    return SimpleConversationalRAG(llm, retriever)
