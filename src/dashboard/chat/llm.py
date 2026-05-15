import os
import time
import requests

COHERE_MODEL = "command-r7b-12-2024"
MAX_TOKENS = 800
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


def get_validation_context(df) -> str:
    """Gera contexto com validações Q001-Q012 do DataFrame."""
    import pandas as pd

    q001 = df.duplicated(subset=['MATRICULA']).sum()

    q002 = 0
    if 'DATA_INSTALACAO_HIDROMETRO_DT' in df.columns:
        q002 = (df['DATA_INSTALACAO_HIDROMETRO_DT'] > pd.Timestamp.today()).sum()

    q003 = int(df.get('FLAG_INCONSIST_FATURAMENTO', pd.Series([False]*len(df))).sum())
    q004 = int(df.get('FLAG_FATURADO_MENOR_REAL', pd.Series([False]*len(df))).sum())
    q005 = int(df.get('FLAG_OUTLIER_EXTREMO', pd.Series([False]*len(df))).sum())

    vol_neg = int(df.get('FLAG_VOLUME_NEGATIVO', pd.Series([False]*len(df))).sum())
    val_neg = int(df.get('FLAG_VALOR_NEGATIVO', pd.Series([False]*len(df))).sum())
    q006 = vol_neg + val_neg

    q007 = int(df.get('FLAG_ATIVA_SEM_RECEITA', pd.Series([False]*len(df))).sum())
    q008 = int(df.get('FLAG_SEM_CATEGORIA', pd.Series([False]*len(df))).sum())
    q009 = int(df.get('FLAG_DATA_INVALIDA', pd.Series([False]*len(df))).sum())
    q010 = int(df.get('FLAG_ZERO_ECONOMIAS', pd.Series([False]*len(df))).sum())
    q012 = int(df.get('FLAG_REAL_MAIOR_LIDO', pd.Series([False]*len(df))).sum())

    contexto = f"""
🔍 VALIDAÇÕES DE QUALIDADE (Q001-Q012):

| Código | Verificação | Quantidade | Status |
|--------|-------------|------------|--------|
| Q001 | MATRÍCULA duplicada | {q001} | {'⚠️ ERRO' if q001 > 0 else '✅ OK'} |
| Q002 | Data futura | {q002} | {'⚠️ ERRO' if q002 > 0 else '✅ OK'} |
| Q003 | Inconsistência faturamento | {q003} | {'⚠️ ERRO' if q003 > 0 else '✅ OK'} |
| Q004 | VOLUME_FATURADO < VOLUME_REAL | {q004} | {'⚠️ ERRO' if q004 > 0 else '✅ OK'} |
| Q005 | Outliers extremos | {q005} | {'⚠️ ERRO' if q005 > 0 else '✅ OK'} |
| Q006 | Valores negativos | {q006} | {'⚠️ ERRO' if q006 > 0 else '✅ OK'} |
| Q007 | Ativa sem receita | {q007} | {'⚠️ ERRO' if q007 > 0 else '✅ OK'} |
| Q008 | Sem categoria | {q008} | {'⚠️ ERRO' if q008 > 0 else '✅ OK'} |
| Q009 | Data inválida | {q009} | {'⚠️ ERRO' if q009 > 0 else '✅ OK'} |
| Q010 | Zero economias | {q010} | {'⚠️ ERRO' if q010 > 0 else '✅ OK'} |
| Q012 | REAL > LIDO | {q012} | {'⚠️ ERRO' if q012 > 0 else '✅ OK'} |

_total_inconsistencias = {q001 + q002 + q003 + q004 + q005 + q006 + q007 + q008 + q009 + q010 + q012} registros com problemas detectados.
"""
    return contexto


def get_quality_metrics_context(df) -> str:
    """Gera contexto com métricas de qualidade de dados."""
    import pandas as pd

    total = len(df)
    complete = (df.notna().all(axis=1)).sum()
    iqd = round(complete / total * 100, 1) if total > 0 else 0

    missing_hidrometro = int(df['NUMERO_HIDROMETRO'].isnull().sum()) if 'NUMERO_HIDROMETRO' in df.columns else 0
    missing_volume = int(df['VOLUME_LIDO'].isnull().sum()) if 'VOLUME_LIDO' in df.columns else 0
    missing_categoria = int(df['CATEGORIA_PRINCIPAL'].isnull().sum()) if 'CATEGORIA_PRINCIPAL' in df.columns else 0

    meses_dados_ausentes = int(df.get('MESES_DADOS_AUSENTES', pd.Series([0]*len(df))).sum()) if 'MESES_DADOS_AUSENTES' in df.columns else 0

    contexto = f"""
📈 MÉTRICAS DE QUALIDADE DE DADOS:

- IQD (Índice de Qualidade de Dados): {iqd}%
- Registros completos: {complete} / {total}
- Registros com missing: {total - complete}

MISSING POR CAMPO CRÍTICO:
- NUMERO_HIDROMETRO: {missing_hidrometro} registros ({missing_hidrometro/total*100:.1f}%)
- VOLUME_LIDO (mês atual): {missing_volume} registros ({missing_volume/total*100:.1f}%)
- CATEGORIA_PRINCIPAL: {missing_categoria} registros ({missing_categoria/total*100:.1f}%)

MESES COM DADOS AUSENTES (total): {meses_dados_ausentes} ocorrências
"""
    return contexto


def get_documentation_excerpt() -> str:
    """Retorna trecho da documentação técnica para contexto."""
    doc_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'DOCUMENTACAO_DADOS.md')

    if os.path.exists(doc_path):
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                doc = f.read()

            excerpt = """
📚 RESUMO DA DOCUMENTAÇÃO TÉCNICA:

## Glossário do Sistema Comercial de Saneamento

MATRICULA: Identificador único de cada ligação de água/esgoto.
VOLUME_LIDO: Volume medido fisicamente pelo hidrômetro (m³).
VOLUME_REAL: Volume validado pelo sistema após análise.
VOLUME_FATURADO: Volume efetivamente cobrado na fatura (mín 10 m³).
VALOR_TOTAL: Valor final da fatura (água + esgoto + serviços + impostos - descontos).

## Categorias de Consumo

- Residencial: Maior volume absoluto (87% das ligações)
- Comercial: Volume médio 79,9 m³/mês
- Industrial: Volume médio 76,3 m³/mês, maior consumo individual
- Pública: Órgãos públicos (0,3%)

## Tipos de Hidrômetro

- Unijato: 72,6% do parque (mais comum)
- Unijato Pré-equipado: 15,3%
- Multijato: 7,3%
- Ultrassônico: 3,3% (mais preciso)

## Classes Metrológicas (ABNT NBR 15538)

- Classe A: 14,9% (básico)
- Classe B: 80,8% (intermediário)
- Classe C: 3,0% (maior precisão)

## Anomalias e Fraudes

- LIDO > REAL: Possível adulteração do sistema
- Consumo zero persistente: Possível fraude ou hidrômetro parado
- Consumo constante exato: Possible estimativa de consumo não autorizada

## Premissas Técnicas

- Tarifa mínima: R$ 89,03 (10 m³)
- Fator de submedição (>5 anos): 15%
- Consumo crônico zero: ≥6 meses
- Score de prioridade: pesos empíricos (50/40/30/20/10)
"""
            return excerpt
        except Exception:
            return ""
    return ""


def get_full_context(df, include_docs=False) -> str:
    """Combina todas as fontes de contexto para o chatbot."""
    contexto = get_stats_context(df)
    contexto += "\n" + get_validation_context(df)
    contexto += "\n" + get_quality_metrics_context(df)

    if include_docs:
        doc_excerpt = get_documentation_excerpt()
        if doc_excerpt:
            contexto += "\n" + doc_excerpt

    if len(contexto) > 120000:
        contexto = contexto[:120000] + "\n\n[... contexto truncado por limite de tamanho]"

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