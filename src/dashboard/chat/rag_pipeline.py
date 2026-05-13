"""
Pipeline RAG: Constroi o chain de busca e geracao de respostas
usando LangChain + FAISS + HuggingFace embeddings.
"""

import pandas as pd
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_classic.chains import ConversationalRetrievalChain
from langchain_classic.memory import ConversationBufferWindowMemory
from langchain_classic.prompts import PromptTemplate

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


def build_rag_chain(llm, df: pd.DataFrame | None = None):
    """
    Constroi e retorna um ConversationalRetrievalChain com RAG.

    Args:
        llm: Instancia configurada do ChatHuggingFace (ou outro LLM compativel).
        df: DataFrame opcional com os dados para estatisticas dinamicas.

    Returns:
        ConversationalRetrievalChain pronto para uso.
    """
    from dashboard.chat.knowledge_base import KNOWLEDGE_BASE_DOCS, generate_dynamic_stats

    docs = list(KNOWLEDGE_BASE_DOCS)

    if df is not None:
        dynamic_stats = generate_dynamic_stats(df)
        if dynamic_stats:
            docs.append(dynamic_stats)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", "?", "!", " "]
    )
    chunks = splitter.create_documents(docs)

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )

    vectorstore = FAISS.from_documents(chunks, embeddings)
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 4}
    )

    memory = ConversationBufferWindowMemory(
        k=5,
        memory_key="chat_history",
        return_messages=True,
        output_key="answer"
    )

    prompt = PromptTemplate(
        input_variables=["context", "chat_history", "question"],
        template=SYSTEM_PROMPT
    )

    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        combine_docs_chain_kwargs={"prompt": prompt},
        return_source_documents=True,
        verbose=False
    )
    return chain
