import streamlit as st
import pandas as pd
import hashlib


def render(df: pd.DataFrame):
    """Renderiza a interface do chatbot na sidebar."""
    st.markdown("""
    <style>
        div[data-testid="stChatInput"] textarea {
            min-height: 50px !important;
            max-height: 80px !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <style>
        .chat-title {
            font-size: 1.1rem !important;
            font-weight: 600 !important;
            color: #2980B9 !important;
            margin-bottom: 4px !important;
        }
    </style>
    <p class="chat-title">💬 Assistente IA</p>
    """, unsafe_allow_html=True)
    st.caption("Pergunte sobre micromedição, consumo, faturamento e oportunidades.")

    from dashboard.chat.llm import has_api_key, get_stats_context

    api_ready = has_api_key()
    if not api_ready:
        _render_setup_notice()
        return

    _init_chat_state()

    pending_question = st.session_state.get("pending_question")
    if pending_question:
        st.session_state.pop("pending_question")
        _process_message(pending_question, df)
        return

    st.divider()

    _render_messages()

    user_input = st.chat_input("Digite sua pergunta...")

    if user_input:
        _process_message(user_input, df)


def _render_setup_notice():
    st.warning(
        "Configure seu token da API HuggingFace para ativar o assistente.\n\n"
        "1. Crie uma conta gratuita em [huggingface.co](https://huggingface.co)\n"
        "2. Gere um Access Token (tipo: **Fine-grained**, permissão: **Inference > Make calls to the serverless Inference API**)\n"
        "3. Cole o token no arquivo `.env.local` na raiz do projeto\n"
        "4. Reinicie o dashboard"
    )
    st.code("HF_TOKEN=hf_seu_token_aqui", language="bash")


def _init_chat_state():
    if "chat_messages" not in st.session_state:
        st.session_state["chat_messages"] = [
            {
                "role": "assistant",
                "content": (
                    "Olá! Sou o assistente de IA do dashboard de micromedição.\n\n"
                    "Posso responder perguntas sobre:\n"
                    "- Quantidade de ligações e distribuição por categoria\n"
                    "- Volumes de consumo e faturamento mensal\n"
                    "- Anomalias e possíveis fraudes detectadas\n"
                    "- Hidrômetros (tipos, marcas, idade do parque)\n"
                    "- Oportunidades de recuperação de receita\n"
                    "- Glossário técnico do setor de saneamento\n\n"
                    "Digite sua pergunta no campo abaixo!"
                )
            }
        ]

    if "chat_response" not in st.session_state:
        st.session_state["chat_response"] = None


def _render_messages():
    for msg in st.session_state.get("chat_messages", []):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    response = st.session_state.get("chat_response")
    if response:
        with st.chat_message("assistant"):
            with st.spinner("Consultando..."):
                st.markdown(response["answer"])
                if response.get("error"):
                    st.error(response["error"])


def _process_message(user_input: str, df: pd.DataFrame):
    from dashboard.chat.llm import get_stats_context, perguntar

    messages = st.session_state["chat_messages"]
    messages.append({"role": "user", "content": user_input})
    st.session_state["chat_response"] = None

    try:
        contexto = get_stats_context(df)

        with st.spinner("Consultando..."):
            result = perguntar(user_input, contexto)
            answer = result.get("answer", "Resposta não disponível.")

        st.session_state["chat_response"] = result
    except Exception as e:
        error_msg = str(e)
        if "timeout" in error_msg.lower() or "failed" in error_msg.lower():
            error_msg = "Tempo limite excedido. Tente novamente ou reformule a pergunta."
        st.session_state["chat_response"] = {"answer": "", "error": error_msg}

    st.rerun()


def clear_conversation():
    """Limpa o histórico de chat."""
    if "chat_messages" in st.session_state:
        st.session_state["chat_messages"] = [
            {
                "role": "assistant",
                "content": (
                    "Conversa limpa! Sou o assistente de IA do dashboard de micromedição.\n\n"
                    "Posso responder perguntas sobre:\n"
                    "- Quantidade de ligações e distribuição por categoria\n"
                    "- Volumes de consumo e faturamento mensal\n"
                    "- Anomalias e possíveis fraudes detectadas\n"
                    "- Hidrômetros (tipos, marcas, idade do parque)\n"
                    "- Oportunidades de recuperação de receita\n"
                    "- Glossário técnico do setor de saneamento\n\n"
                    "Digite sua pergunta no campo abaixo!"
                )
            }
        ]
    if "chat_response" in st.session_state:
        st.session_state["chat_response"] = None
    if "chat_llm" in st.session_state:
        del st.session_state["chat_llm"]
    st.rerun()