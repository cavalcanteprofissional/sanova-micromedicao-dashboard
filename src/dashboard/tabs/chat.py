import streamlit as st
import pandas as pd


def render(df: pd.DataFrame):
    """
    Renderiza a interface do chatbot dentro do expander da sidebar.
    O df e usado para gerar estatisticas dinamicas no RAG.
    """
    st.markdown("##### 💬 Chatbot IA — Assistente")
    st.caption("Pergunte sobre micromedição, consumo, faturamento, anomalias e oportunidades.")

    api_ready = _check_api_key()
    if not api_ready:
        _render_setup_notice()
        return

    _init_chat_state(df)

    _render_messages()

    user_input = st.chat_input("Digite sua pergunta sobre micromedição...")

    if user_input:
        _handle_message(user_input, df)


def _check_api_key() -> bool:
    try:
        from dashboard.chat.llm_config import has_api_key
        return has_api_key()
    except Exception:
        return False


def _render_setup_notice():
    st.warning(
        "Configure seu token da API HuggingFace para ativar o assistente.\n\n"
        "1. Crie uma conta gratuita em [huggingface.co](https://huggingface.co)\n"
        "2. Gere um Access Token (tipo: **Fine-grained**, permissão: **Inference > Make calls to the serverless Inference API**)\n"
        "3. Cole o token no arquivo `.env.local` na raiz do projeto\n"
        "4. Reinicie o dashboard"
    )
    st.code("HF_TOKEN=hf_seu_token_aqui", language="bash")


def _init_chat_state(df: pd.DataFrame):
    if "chat_messages" not in st.session_state:
        st.session_state["chat_messages"] = [
            {
                "role": "assistant",
                "content": (
                    "Olá! Sou o assistente de IA do dashboard de micromedição.\n\n"
                    "Pode me perguntar sobre:\n"
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

    if "chat_chain" not in st.session_state:
        st.session_state["chat_chain"] = None
        st.session_state["chat_df"] = df


def _render_messages():
    for msg in st.session_state.get("chat_messages", []):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])


def _handle_message(user_input: str, df: pd.DataFrame):
    messages = st.session_state["chat_messages"]
    messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    chain = st.session_state.get("chat_chain")
    df_ref = st.session_state.get("chat_df")

    if chain is None or df_ref is not df:
        try:
            with st.spinner("Iniciando assistente..."):
                from dashboard.chat.llm_config import get_llm
                from dashboard.chat.rag_pipeline import build_rag_chain
                llm = get_llm()
                chain = build_rag_chain(llm, df)
                st.session_state["chat_chain"] = chain
                st.session_state["chat_df"] = df
        except Exception as e:
            error_msg = (
                f"Erro ao inicializar o assistente: {e}\n\n"
                "Verifique se o HF_TOKEN está corretamente configurado em `.env.local`."
            )
            with st.chat_message("assistant"):
                st.error(error_msg)
            messages.append({"role": "assistant", "content": error_msg})
            return

    with st.chat_message("assistant"):
        with st.spinner("Consultando a base de conhecimento..."):
            try:
                result = chain.invoke({"question": user_input})
                answer = result["answer"]
            except Exception as e:
                answer = f"Erro ao processar a pergunta: {e}"

        st.markdown(answer)
        messages.append({"role": "assistant", "content": answer})

    st.rerun()
