import os
import time
import requests

COHERE_MODEL = "command-r7b-12-2024"
MAX_TOKENS = 500
TEMPERATURE = 0.1
REQUEST_TIMEOUT = 90
MAX_RETRIES = 3
RETRY_BACKOFF = 2


FAQ_FALLBACK = {
    "quantas ligações": "A base de dados contém 1.912 ligações no total, sendo 1.664 residenciais (87%), 143 comerciais (7,5%), 83 industriais (4,3%) e 5 públicas (0,3%).",
    "faturamento": "O faturamento mensal é calculado a partir da soma do VALOR_TOTAL das ligações ativas. Os dados detalhados podem ser visualizados na aba Visão Geral.",
    "anomalias": "Foram detectados 144 casos com divergência entre volume lido e volume real (possível fraude), 224 ligações com 6+ meses de consumo zero, e 414 hidrômetros com mais de 5 anos (risco de submedição).",
    "consumo médio": "A categoria Industrial tem o maior consumo médio individual, seguida de Comercial. Residencial representa a maior fatia da receita pelo volume absoluto de clientes.",
    "consumo mínimo": "O consumo mínimo tarifário é de 10 m³ por mês. Independentemente do volume lido, o cliente é cobrado por no mínimo 10 m³.",
    "recuperação": "O potencial de recuperação de receita é estimado em R$ 2,49 milhões em 12 meses, considerando substituição de hidrômetros, regularização de consumo zero e fiscalização de anomalias.",
    "hidrômetro": "O hidrômetro Unijato é o mais comum (72,6% do parque). A classe metrológica B é a predominante (80,8%). A idade média do parque é de 2,1 anos.",
    "fraude": "Os principais indicadores de fraude são: VOLUME_LIDO superior ao VOLUME_REAL, consumo zero persistente em ligação ativa, e consumo constante exato por muitos meses.",
    "submedição": "Hidrômetros com mais de 5 anos tendem a submedir devido ao desgaste mecânico. Estudos indicam submedição média de 15% ao ano.",
}


def get_cohere_key() -> str | None:
    """Retorna a chave da API Cohere — via st.secrets, env var ou .env.local."""
    try:
        import streamlit as st
        key = st.secrets.get("COHERE_API_KEY")
        if key:
            return key
    except Exception:
        pass

    token = os.getenv("COHERE_API_KEY")
    if token:
        return token

    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env.local')
    if os.path.exists(dotenv_path):
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=dotenv_path)
        token = os.getenv("COHERE_API_KEY")
        if token:
            return token

    return None


def has_api_key() -> bool:
    """Verifica se a API do Cohere está configurada."""
    key = get_cohere_key()
    return bool(key and key.strip())


def get_stats_context(df) -> str:
    """Gera string de contexto com KPIs reais do DataFrame."""
    import pandas as pd

    total_ligacoes = len(df)
    ativas = (df['SIT._LIG_AGUA'] == 'ATIVA').sum() if 'SIT._LIG_AGUA' in df.columns else 0

    fat_mensal = 0
    if 'VALOR_TOTAL' in df.columns:
        fat_mensal = df['VALOR_TOTAL'].sum()

    vol_total = 0
    if 'VOLUME_FATURADO' in df.columns:
        vol_total = df['VOLUME_FATURADO'].sum()

    anomalias = 0
    if 'VOLUME_REAL' in df.columns and 'VOLUME_LIDO' in df.columns:
        anomalias = (df['VOLUME_REAL'].fillna(0) < df['VOLUME_LIDO'].fillna(0) - 1).sum()

    consumo_zero = 0
    if 'VOLUME_LIDO' in df.columns and 'SIT._LIG_AGUA' in df.columns:
        consumo_zero = ((df['VOLUME_LIDO'].fillna(0) == 0) & (df['SIT._LIG_AGUA'] == 'ATIVA')).sum()

    hidro_velhos = 0
    if 'IDADE_HIDRO_ANOS' in df.columns:
        hidro_velhos = (df['IDADE_HIDRO_ANOS'].fillna(0) > 5).sum()

    categorias = {}
    if 'CATEGORIA_PRINCIPAL' in df.columns:
        categorias = df['CATEGORIA_PRINCIPAL'].value_counts().to_dict()

    contexto = f"""
📊 ESTATÍSTICAS ATUAIS DO DASHBOARD:

LIGAÇÕES:
- Total de ligações: {total_ligacoes}
- Ligações ativas: {ativas} ({ativas/total_ligacoes*100:.1f}%)

FATURAMENTO:
- Faturamento mensal: R$ {fat_mensal:,.2f}
- Volume total faturado: {vol_total:,.0f} m³

ANOMALIAS DETECTADAS:
- Divergência LIDO > REAL (possível fraude): {anomalias} casos
- Consumo zero em ligações ativas: {consumo_zero} casos
- Hidrômetros > 5 anos (risco submedição): {hidro_velhos} unidades

QUALIDADE DE Dados:
- Por categoria: {categorias}
"""
    return contexto


SYSTEM_PROMPT = """Você é um assistente especializado em análise de sistemas comerciais
de saneamento, com foco em micromedição, detecção de perdas comerciais e gestão de receita.

Use as estatísticas fornecidas abaixo para responder perguntas de forma precisa e factual.
Se a pergunta não puder ser respondida com os dados disponíveis, diga:
"Não tenho informações suficientes para responder esta pergunta.
Posso ajudar com análises sobre consumo, faturamento, hidrômetros, anomalias ou
recuperação de receita desta base de dados."

Seja técnico mas didático. Use números concretos quando disponíveis.
Ao citar valores financeiros, use formato brasileiro (R$ 1.234,56).
Ao citar volumes, use m³.

{context}

Pergunta: {question}
Resposta:"""


def _get_fallback(question: str) -> str | None:
    """Retorna resposta do FAQ se a pergunta for sobre tópicos conhecidos."""
    question_lower = question.lower()
    for key, answer in FAQ_FALLBACK.items():
        if key in question_lower:
            return answer
    return None


def _call_cohere_api(prompt: str) -> str:
    """Faz chamada para API Cohere usando requests (mais estável no Windows)."""
    api_key = get_cohere_key()
    url = "https://api.cohere.com/v1/chat"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": COHERE_MODEL,
        "message": prompt,
        "max_tokens": MAX_TOKENS,
        "temperature": TEMPERATURE
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=REQUEST_TIMEOUT
    )

    if response.status_code == 200:
        data = response.json()
        return data.get("text", "")
    elif response.status_code == 429:
        raise Exception("rate_limit_exceeded")
    elif response.status_code >= 500:
        raise Exception("server_error")
    else:
        raise Exception(f"api_error: {response.status_code}")


def perguntar(pergunta: str, contexto: str) -> dict:
    """Envia pergunta com contexto para a API Cohere com retry robusto."""
    prompt = SYSTEM_PROMPT.format(context=contexto, question=pergunta)

    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            answer = _call_cohere_api(prompt)
            return {"answer": answer.strip()}
        except Exception as e:
            last_error = str(e)

            if attempt < MAX_RETRIES - 1:
                wait_time = RETRY_BACKOFF ** attempt
                time.sleep(wait_time)
                continue

    fallback = _get_fallback(pergunta)
    if fallback:
        return {"answer": fallback}

    error_lower = last_error.lower()
    if "rate_limit" in error_lower or "quota" in error_lower:
        return {"answer": "", "error": "Limite de requisições excedido. Tente novamente mais tarde."}
    if "timeout" in error_lower or "connection" in error_lower or "10054" in error_lower:
        return {"answer": "", "error": "Erro de conexão. Verifique sua internet e tente novamente."}
    return {"answer": "", "error": last_error}