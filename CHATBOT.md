---
name: chat-ia-micromedicao-streamlit
description: >
  Use esta skill para implementar um chat de IA generativa com RAG (Retrieval-Augmented
  Generation) em Streamlit, utilizando LangChain + HuggingFace (embeddings gratuitos) +
  FAISS como vector store local, sobre a base de dados de micromedição de saneamento
  (Dados_-_Estudo_Micromedição.xlsx). Acione quando o usuário pedir: chat inteligente sobre
  os dados, assistente de perguntas e respostas sobre micromedição, FAQ automatizado de
  sistema comercial, chatbot sobre consumo e faturamento de água, ou qualquer variação de
  interface conversacional sobre a base de dados de saneamento. Inclui knowledge base
  pré-definida com FAQs do domínio, pipeline RAG completo, interface de chat Streamlit,
  e fallback para perguntas fora do escopo.
---

# SKILL: Chat de IA Generativa com RAG — Micromedição / Sistema Comercial de Saneamento

## 1. VISÃO GERAL DA ARQUITETURA

```
┌──────────────────────────────────────────────────────────────┐
│                    STREAMLIT FRONTEND                        │
│  ┌─────────────────┐          ┌──────────────────────────┐  │
│  │  Chat UI        │          │  FAQ Pré-definido (sidebar)│ │
│  │  (histórico +   │          │  (perguntas sugeridas)    │ │
│  │   input)        │          └──────────────────────────┘  │
│  └────────┬────────┘                                         │
└───────────┼──────────────────────────────────────────────────┘
            │ pergunta do usuário
            ▼
┌──────────────────────────────────────────────────────────────┐
│                    PIPELINE RAG (LangChain)                  │
│                                                              │
│  1. Embedding da pergunta                                    │
│     └─ HuggingFace: neuralmind/bert-base-portuguese-cased   │
│         ou sentence-transformers/paraphrase-multilingual-    │
│         MiniLM-L12-v2  (gratuito, roda local)               │
│                                                              │
│  2. Busca vetorial (FAISS local — sem servidor externo)      │
│     └─ Retorna top-k chunks relevantes do knowledge base     │
│                                                              │
│  3. Geração da resposta (LLM)                               │
│     └─ Opção A: Anthropic Claude API (claude-sonnet-4-...)  │
│     └─ Opção B: HuggingFace Hub (zephyr-7b-beta, gratuito) │
│     └─ Opção C: Groq API (llama-3, ultra-rápido, gratuito)  │
│                                                              │
│  4. Resposta contextualizada + fonte citada                  │
└──────────────────────────────────────────────────────────────┘
            │
            ▼
┌──────────────────────────────────────────────────────────────┐
│              KNOWLEDGE BASE (3 camadas)                      │
│                                                              │
│  Camada 1: FAQ estático do domínio (texto curado)           │
│  Camada 2: Estatísticas calculadas dos dados reais          │
│  Camada 3: Documentos técnicos de saneamento (opcional)     │
└──────────────────────────────────────────────────────────────┘
```

---

## 2. DEPENDÊNCIAS

```txt
# requirements.txt
streamlit>=1.35.0
langchain>=0.2.0
langchain-community>=0.2.0
langchain-huggingface>=0.0.3
faiss-cpu>=1.8.0
sentence-transformers>=3.0.0
pandas>=2.0.0
openpyxl>=3.1.0
numpy>=1.24.0
python-dotenv>=1.0.0

# Escolher UM dos LLMs abaixo:
anthropic>=0.30.0          # Opção A — melhor qualidade
# huggingface-hub>=0.23.0  # Opção B — gratuito
# groq>=0.9.0              # Opção C — gratuito e rápido
```

---

## 3. KNOWLEDGE BASE — DOCUMENTO DE DOMÍNIO COMPLETO

Criar o arquivo `knowledge_base.py` com toda a base de conhecimento como strings.
Este é o conteúdo que alimenta o RAG — não depende de PDFs externos.

```python
# knowledge_base.py
"""
Base de conhecimento do sistema comercial de saneamento.
Dividida em chunks temáticos para indexação vetorial.
Cada item da lista é um chunk independente.
"""

KNOWLEDGE_BASE_DOCS = [

    # ── GLOSSÁRIO ───────────────────────────────────────────────────────────
    """
    GLOSSÁRIO DO SISTEMA COMERCIAL DE SANEAMENTO

    MATRÍCULA: Identificador único de cada ligação de água/esgoto. Cada imóvel
    possui uma matrícula distinta no sistema comercial.

    VOLUME_LIDO: Volume medido fisicamente pelo hidrômetro na leitura de campo,
    expresso em metros cúbicos (m³).

    VOLUME_REAL: Volume aceito e validado pelo sistema após análise. Pode diferir
    do volume lido quando há suspeita de leitura incorreta ou fraude. Nunca deve
    ser maior que o VOLUME_LIDO em condições normais.

    VOLUME_FATURADO: Volume efetivamente cobrado na fatura. Nunca é inferior ao
    consumo mínimo tarifário (10 m³), mesmo que o consumo real seja menor.

    VALOR_AGUA: Valor cobrado pelo fornecimento de água.
    VALOR_ESGOTO: Valor cobrado pelo serviço de coleta e tratamento de esgoto.
    VALOR_SERVICOS: Cobranças adicionais por serviços específicos.
    VALOR_IMPOSTOS: Tributos incidentes sobre o faturamento.
    VALOR_DESCONTOS: Descontos concedidos (tarifa social, isenções).
    VALOR_TOTAL: Soma de todos os componentes menos os descontos. É o valor final
    da fatura do cliente.
    """,

    # ── SITUAÇÕES DE LIGAÇÃO ────────────────────────────────────────────────
    """
    SITUAÇÕES POSSÍVEIS DE UMA LIGAÇÃO DE ÁGUA

    Ativa: Ligação funcionando normalmente, com fornecimento de água e geração
    de fatura mensal. A grande maioria das ligações está nesta situação.

    Cancelada: Ligação desativada a pedido do cliente ou por decisão administrativa.
    Não gera faturamento. O hidrômetro geralmente é retirado.

    Cortada Ramal: Corte realizado diretamente na rede de distribuição (ramal),
    geralmente por inadimplência grave ou por questões técnicas. É uma intervenção
    mais severa que o corte no cavalete.

    Cortada Cavalete: Corte realizado no cavalete do imóvel (ponto de entrada da
    ligação). É o corte mais comum por inadimplência. O hidrômetro permanece instalado.

    Suprimida: Ligação temporariamente sem fornecimento por razões técnicas ou
    operacionais, sem ser considerada cancelada oficialmente.

    Cortada na Fita: Corte realizado com fita de segurança no hidrômetro, impedindo
    a passagem de água. Técnica usada como medida preventiva ou administrativa.

    Eliminada: Ligação definitivamente removida do cadastro e da rede física.
    Não existe mais como entidade operacional.
    """,

    # ── CATEGORIAS DE CONSUMO ───────────────────────────────────────────────
    """
    CATEGORIAS DE CONSUMO E SEUS PERFIS

    Residencial: Categoria mais numerosa, com 1.664 ligações (87% do total).
    Volume médio mensal de 42,3 m³ e faturamento médio de R$ 548,84.
    Responsável por R$ 883.082,50 da receita mensal (75,6% do total).
    Inclui apartamentos, casas e condomínios residenciais.

    Comercial: 143 ligações (7,5% do total), com volume médio de 79,9 m³ e
    faturamento médio de R$ 1.394,59. Gera R$ 177.113,05 mensais (15,2% da receita).
    Exemplos: estabelecimentos comerciais, lojas, restaurantes, hotéis.

    Industrial: 83 ligações (4,3% do total), com volume médio de 76,3 m³ e
    faturamento médio de R$ 1.624,45. Gera R$ 107.213,98 mensais (9,2% da receita).
    Engloba indústrias e grandes consumidores com processos produtivos.

    Pública: 5 ligações (0,3% do total). Órgãos e instalações do poder público.
    Geralmente possuem tratamento tarifário diferenciado.

    RECEITA TOTAL MENSAL (ligações ativas): R$ 1.167.995,44
    """,

    # ── HIDRÔMETROS ─────────────────────────────────────────────────────────
    """
    HIDRÔMETROS: TIPOS, MARCAS E CLASSES METROLÓGICAS

    TIPOS DE HIDRÔMETRO:
    - Unijato: Mais comum, com 1.348 unidades (72,6%). Funciona com um único jato
      d'água impulsionando a turbina. Indicado para ligações residenciais e
      pequenos comércios. Menor custo.
    - Unijato Pré-equipado: 284 unidades (15,3%). Versão do unijato preparada para
      leitura remota ou telemetria.
    - Multijato: 136 unidades (7,3%). Múltiplos jatos de água aumentam a precisão
      de medição em faixas de consumo variadas. Usado em comércios e indústrias.
    - Ultrassônico: 62 unidades (3,3%). Tecnologia mais avançada, sem partes móveis.
      Alta precisão e durabilidade. Indicado para grandes consumidores e
      monitoramento contínuo.

    MARCAS: O parque de hidrômetros possui 6 marcas (A a F). A Marca A é dominante.
    As marcas foram anonimizadas para fins de análise, mas no sistema real cada
    marca corresponde a um fabricante específico com características de desgaste
    e precisão próprias.

    CLASSES METROLÓGICAS (conforme ABNT NBR 15538):
    - Classe A: Padrão mais básico. 276 unidades (14,9%). Menor faixa de medição
      precisa. Adequada para consumos muito baixos.
    - Classe B: Padrão intermediário e mais comum. 1.499 unidades (80,8%).
      Equilíbrio entre custo e precisão. Recomendado para uso geral.
    - Classe C: Maior precisão. 55 unidades (3,0%). Detecta consumos muito baixos
      com maior exatidão. Indicado onde se suspeita de vazamentos internos.

    DIÂMETROS DISPONÍVEIS: 3/4" (mais comum — residencial), 1", 1½" e 2"
    (para maiores vazões — industrial e comercial).

    IDADE MÉDIA DO PARQUE: 2,1 anos.
    HIDRÔMETROS COM MAIS DE 5 ANOS: 177 unidades — candidatos à substituição por
    submedição progressiva (equipamentos velhos tendem a medir menos do que o
    volume real, gerando perda de receita para a concessionária).
    """,

    # ── ANOMALIAS E FRAUDES ─────────────────────────────────────────────────
    """
    ANOMALIAS, FRAUDES E INCONSISTÊNCIAS DETECTADAS

    DIVERGÊNCIA LIDO vs REAL (Fraude/Adulteração):
    Ocorre quando VOLUME_LIDO é maior que VOLUME_REAL. Em condições normais,
    o sistema nunca deve validar um volume real superior ao lido — o que indica
    que houve intervenção manual no sistema para reduzir artificialmente o volume
    faturado. Foram detectados 11 casos nesta situação, representando possível
    fraude ou erro sistêmico grave.

    LIGAÇÕES ATIVAS COM CONSUMO ZERO:
    77 ligações com SIT._LIG_AGUA = 'Ativa' e VOLUME_LIDO = 0 no mês de referência.
    Causas possíveis: hidrômetro parado/travado, fraude (derivação antes do
    hidrômetro), leitura não realizada, ou imóvel desocupado ainda ativo no
    cadastro. Cada caso representa receita potencial não capturada.

    CONSUMO CONSTANTE EXATO POR VÁRIOS MESES:
    Quando o volume lido é exatamente o mesmo por 6 meses ou mais, pode indicar
    que o operador está estimando o consumo em vez de realizar a leitura efetiva
    (prática de "consumo estimado" não autorizado).

    CONSUMO IMPLAUSÍVEL (OUTLIER ESTATÍSTICO):
    Volumes que excedem a média histórica da ligação em mais de 3 desvios-padrão
    podem indicar vazamento não comunicado, fraude reversa (consumo irregular não
    registrado antes) ou erro de leitura.

    LIGAÇÕES SEM HIDRÔMETRO (ativas):
    1 ligação ativa sem NUMERO_HIDROMETRO cadastrado. Representa consumo não
    mesurado e, portanto, receita não capturada.
    """,

    # ── CONSUMO MÍNIMO E TARIFA ─────────────────────────────────────────────
    """
    CONSUMO MÍNIMO E ESTRUTURA TARIFÁRIA

    CONSUMO MÍNIMO TARIFÁRIO: 10 m³ por mês.
    Independentemente do volume lido, o cliente é cobrado por no mínimo 10 m³.
    O VALOR_TOTAL mínimo observado na base é de aproximadamente R$ 89,03
    (referência para ligações residenciais no consumo mínimo, incluindo água
    e esgoto na menor faixa tarifária).

    ESTRUTURA DO FATURAMENTO:
    A fatura é composta por: VALOR_AGUA + VALOR_ESGOTO + VALOR_SERVICOS
    + VALOR_IMPOSTOS - VALOR_DESCONTOS = VALOR_TOTAL

    O valor do esgoto é calculado como percentual do valor da água (geralmente
    80% em sistemas de cobrança proporcional). Ligações sem rede de esgoto
    disponível têm VALOR_ESGOTO zerado.

    FATURAMENTO MÉDIO POR CATEGORIA:
    - Residencial: R$ 548,84/mês
    - Comercial: R$ 1.394,59/mês
    - Industrial: R$ 1.624,45/mês
    FATURAMENTO MÉDIO GERAL (ativas): R$ 646,73/mês
    """,

    # ── RECUPERAÇÃO DE RECEITA ──────────────────────────────────────────────
    """
    OPORTUNIDADES DE RECUPERAÇÃO DE RECEITA

    1. FISCALIZAÇÃO DE ANOMALIAS DE LEITURA (11 casos):
    Os 11 casos com VOLUME_LIDO > VOLUME_REAL representam divergência que pode
    indicar adulteração do sistema. Prioridade ALTA. Ação: auditoria de campo
    e revisão dos lançamentos.

    2. REGULARIZAÇÃO DE CONSUMO ZERO (77 ligações ativas):
    Estimativa conservadora: 77 ligações × R$ 89,03 (tarifa mínima) =
    R$ 6.855,31/mês de receita potencial não capturada. Em 12 meses: ~R$ 82.264.
    Ação: vistoria de campo para identificar causa e regularização.

    3. SUBSTITUIÇÃO DE HIDRÔMETROS VELHOS (177 com > 5 anos):
    Hidrômetros envelhecidos submedem progressivamente. Premissa técnica: 15% de
    submedição em equipamentos com mais de 5 anos (referência literatura técnica
    de saneamento). Impacto estimado: 177 × R$ 646,73 × 15% × 12 meses
    ≈ R$ 205.658/ano de receita não capturada por submedição.
    Ação: substituição preventiva do parque envelhecido.

    4. REDUÇÃO DO ÍNDICE DE PERDAS COMERCIAIS:
    O Índice de Perdas Comerciais (IPC) é calculado pela diferença entre o volume
    disponibilizado e o volume faturado. Toda irregularidade identificada (fraude,
    submedição, consumo não registrado) impacta diretamente o IPC.

    5. PAYBACK DAS AÇÕES:
    O custo médio de uma vistoria de campo é estimado em R$ 80–150 por ligação.
    Para as 77 ligações com consumo zero, o payback da vistoria é de < 2 meses
    considerando regularização com a tarifa mínima de R$ 89,03.
    Para substituição de hidrômetros: custo médio de R$ 200–400/unidade vs
    ganho anual de ~R$ 1.163/unidade = payback de 2–4 meses.
    """,

    # ── METODOLOGIA DE ANÁLISE ──────────────────────────────────────────────
    """
    METODOLOGIA DE ANÁLISE E PREMISSAS ADOTADAS

    BASE DE DADOS: 1.912 ligações com histórico de 13 meses (mês atual +
    12 meses históricos, sufixados de _01 a _12).

    PERÍODO DE REFERÊNCIA: As colunas sem sufixo representam o mês mais recente.
    As colunas _01 representam o mês imediatamente anterior, e assim por diante
    até _12 (mês mais antigo da série).

    PREMISSAS ADOTADAS POR FALTA DE DADOS:
    - Tarifa mínima de R$ 89,03 (extraída dos dados reais — menor valor observado)
    - Custo unitário da água: ~R$ 10/m³ (estimativa para cálculo de perdas)
    - Fator de submedição em hidrômetros > 5 anos: 15% (literatura técnica)
    - Tarifa social não foi segregada por falta de identificação no cadastro

    INDICADORES-CHAVE DE ANÁLISE (KPIs):
    - Índice de Consumo Zero (ICZ): % de ligações ativas com consumo zero
      ICZ da base = 77/1815 = 4,2%
    - Taxa de Anomalia de Leitura: 11/1912 = 0,57%
    - Participação por categoria na receita:
      Residencial 75,6% | Comercial 15,2% | Industrial 9,2%
    - Volume médio geral faturado: 46,2 m³/ligação/mês
    """,

    # ── FAQ DIRETO ───────────────────────────────────────────────────────────
    """
    PERGUNTAS FREQUENTES — FAQ DO SISTEMA COMERCIAL

    P: Quantas ligações existem na base de dados?
    R: A base contém 1.912 ligações no total, sendo 1.815 ativas (94,9%),
    39 canceladas, 20 cortadas no ramal, 9 cortadas no cavalete, 6 suprimidas,
    6 cortadas na fita e 2 eliminadas.

    P: Qual é o faturamento total mensal?
    R: R$ 1.167.995,44 considerando apenas as ligações ativas.

    P: Quantas anomalias foram detectadas?
    R: 11 casos com divergência entre volume lido e volume real (possível fraude),
    77 ligações ativas com consumo zero, e 177 hidrômetros com mais de 5 anos
    (risco de submedição).

    P: Qual categoria consome mais?
    R: Industrial tem o maior consumo médio individual (76,3 m³/mês), seguida de
    Comercial (79,9 m³/mês). Porém, Residencial representa 75,6% da receita total
    pelo volume absoluto de clientes (1.664 ligações).

    P: O que é consumo mínimo?
    R: É o volume de 10 m³ cobrado mensalmente mesmo que o consumo real seja
    inferior. Representa uma garantia de receita mínima por ligação e cobre os
    custos fixos de disponibilização do serviço.

    P: Qual o potencial de recuperação de receita?
    R: Estimativa consolidada: R$ 82.264/ano com regularização do consumo zero,
    mais R$ 205.658/ano com substituição de hidrômetros velhos, totalizando
    aproximadamente R$ 287.922/ano de potencial de recuperação identificado
    (considerando apenas as oportunidades quantificadas com os dados disponíveis).

    P: Qual tipo de hidrômetro é mais comum?
    R: O hidrômetro Unijato é o mais comum, representando 72,6% do parque
    (1.348 unidades). A classe metrológica B é a predominante (80,8%).

    P: Como identificar uma fraude no sistema?
    R: Os principais indicadores são: VOLUME_LIDO superior ao VOLUME_REAL (11 casos
    detectados), consumo zero persistente em ligação ativa, consumo constante
    exato por muitos meses (indica estimativa em vez de leitura), e consumo que
    supera em mais de 3 desvios-padrão a média histórica da própria ligação.
    """,
]
```

---

## 4. PIPELINE RAG COMPLETO

```python
# rag_pipeline.py
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate
import streamlit as st

EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
# Alternativa em português: "neuralmind/bert-base-portuguese-cased"
# Alternativa mais pesada/precisa: "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"

SYSTEM_PROMPT = """Você é um assistente especializado em análise de sistemas comerciais
de saneamento, com foco em micromedição, detecção de perdas comerciais e gestão de receita.

Responda SOMENTE com base nas informações fornecidas no contexto abaixo.
Se a pergunta não puder ser respondida com o contexto disponível, diga:
"Não tenho informações suficientes na base de dados para responder esta pergunta.
Posso ajudar com análises sobre consumo, faturamento, hidrômetros, anomalias ou
recuperação de receita desta base de dados."

Seja técnico mas didático. Use números concretos quando disponíveis.
Ao citar valores financeiros, use formato brasileiro (R$ 1.234,56).
Ao citar volumes, use m³.

CONTEXTO RELEVANTE:
{context}

HISTÓRICO DA CONVERSA:
{chat_history}

PERGUNTA: {question}
RESPOSTA:"""

@st.cache_resource(show_spinner="Carregando base de conhecimento...")
def build_rag_chain(llm):
    from knowledge_base import KNOWLEDGE_BASE_DOCS

    # Splitter — chunks pequenos para melhor recuperação
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", "?", "!", " "]
    )
    chunks = splitter.create_documents(KNOWLEDGE_BASE_DOCS)

    # Embeddings (roda local, sem API key)
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )

    # Vector store FAISS (índice local em memória)
    vectorstore = FAISS.from_documents(chunks, embeddings)
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 4}   # retorna os 4 chunks mais relevantes
    )

    # Memória de conversa (últimas 5 trocas)
    memory = ConversationBufferWindowMemory(
        k=5,
        memory_key="chat_history",
        return_messages=True,
        output_key="answer"
    )

    # Prompt customizado
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
```

---

## 5. CONFIGURAÇÃO DOS LLMs (ESCOLHER UM)

### Opção A — Anthropic Claude (melhor qualidade)
```python
# llm_config.py — Opção A
from langchain_anthropic import ChatAnthropic

def get_llm():
    return ChatAnthropic(
        model="claude-sonnet-4-20250514",
        api_key=st.secrets["ANTHROPIC_API_KEY"],   # .streamlit/secrets.toml
        temperature=0.1,
        max_tokens=1024
    )
```

### Opção B — HuggingFace Hub (gratuito)
```python
# llm_config.py — Opção B
from langchain_community.llms import HuggingFaceHub

def get_llm():
    return HuggingFaceHub(
        repo_id="HuggingFaceH4/zephyr-7b-beta",
        huggingfacehub_api_token=st.secrets["HF_TOKEN"],
        model_kwargs={"temperature": 0.1, "max_new_tokens": 512}
    )
```

### Opção C — Groq (gratuito, ultra-rápido)
```python
# llm_config.py — Opção C
from langchain_groq import ChatGroq

def get_llm():
    return ChatGroq(
        model="llama3-8b-8192",
        api_key=st.secrets["GROQ_API_KEY"],
        temperature=0.1,
        max_tokens=1024
    )
```

---

## 6. INTERFACE STREAMLIT COMPLETA

```python
# app.py
import streamlit as st
from rag_pipeline import build_rag_chain
from llm_config import get_llm

# ── Perguntas sugeridas no FAQ ───────────────────────────────────────────────
FAQ_QUESTIONS = [
    "Quantas ligações existem na base de dados?",
    "Qual é o faturamento total mensal?",
    "Quantas anomalias foram detectadas?",
    "Qual categoria tem maior consumo médio?",
    "O que é consumo mínimo tarifário?",
    "Qual o potencial de recuperação de receita?",
    "Como identificar fraude no sistema?",
    "Quantos hidrômetros precisam de substituição?",
    "Qual a diferença entre Unijato e Multijato?",
    "O que significa ligação cortada no ramal?",
    "Qual a classe metrológica mais comum?",
    "Quais são as principais oportunidades de melhoria?",
]

# ── Configuração da página ───────────────────────────────────────────────────
st.set_page_config(
    page_title="Assistente de Micromedição",
    page_icon="💧",
    layout="wide"
)

st.title("💧 Assistente Inteligente — Sistema Comercial de Saneamento")
st.caption("Faça perguntas sobre a base de dados de micromedição, consumo, "
           "faturamento, hidrômetros e oportunidades de recuperação de receita.")

# ── Sidebar: FAQ e configurações ─────────────────────────────────────────────
with st.sidebar:
    st.header("❓ Perguntas Frequentes")
    st.caption("Clique em uma pergunta para enviá-la:")

    for q in FAQ_QUESTIONS:
        if st.button(q, use_container_width=True, key=f"faq_{q[:20]}"):
            st.session_state["faq_input"] = q

    st.divider()
    st.header("⚙️ Configurações")
    show_sources = st.toggle("Mostrar trechos consultados", value=False)

    if st.button("🗑️ Limpar conversa", use_container_width=True):
        st.session_state["messages"] = []
        st.session_state["rag_chain"] = None
        st.rerun()

# ── Inicializar estado ────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "assistant",
            "content": (
                "Olá! Sou o assistente especializado na análise da base de dados de "
                "micromedição do sistema comercial de saneamento.\n\n"
                "Posso responder perguntas sobre:\n"
                "- 📊 Estatísticas gerais (ligações, consumo, faturamento)\n"
                "- 🚨 Anomalias e fraudes detectadas\n"
                "- 🔧 Hidrômetros (tipos, classes, idade do parque)\n"
                "- 💰 Oportunidades de recuperação de receita\n"
                "- 📖 Glossário técnico do setor de saneamento\n\n"
                "Use as sugestões no menu lateral ou faça sua própria pergunta!"
            )
        }
    ]

if "rag_chain" not in st.session_state or st.session_state["rag_chain"] is None:
    llm = get_llm()
    st.session_state["rag_chain"] = build_rag_chain(llm)

# ── Exibir histórico ──────────────────────────────────────────────────────────
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Capturar input (chat ou FAQ) ──────────────────────────────────────────────
user_input = st.chat_input("Digite sua pergunta sobre micromedição...")

if "faq_input" in st.session_state and st.session_state["faq_input"]:
    user_input = st.session_state.pop("faq_input")

# ── Processar resposta ────────────────────────────────────────────────────────
if user_input:
    # Exibir mensagem do usuário
    st.session_state["messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Gerar resposta
    with st.chat_message("assistant"):
        with st.spinner("Consultando a base de conhecimento..."):
            result = st.session_state["rag_chain"].invoke({"question": user_input})
            answer = result["answer"]

        st.markdown(answer)

        # Mostrar fontes consultadas (opcional)
        if show_sources and result.get("source_documents"):
            with st.expander("📚 Trechos consultados na base de conhecimento"):
                for i, doc in enumerate(result["source_documents"], 1):
                    st.markdown(f"**Trecho {i}:**")
                    st.caption(doc.page_content[:400] + "...")
                    st.divider()

    st.session_state["messages"].append({"role": "assistant", "content": answer})
```

---

## 7. ESTRUTURA DE ARQUIVOS DO PROJETO

```
projeto/
├── app.py                          # Aplicação principal Streamlit
├── rag_pipeline.py                 # Pipeline RAG com LangChain + FAISS
├── llm_config.py                   # Configuração do LLM escolhido
├── knowledge_base.py               # Base de conhecimento textual (domínio)
├── requirements.txt                # Dependências
├── .streamlit/
│   └── secrets.toml                # API keys (NÃO versionar)
└── Dados_-_Estudo_Micromedição.xlsx  # Arquivo de dados original
```

### Arquivo `.streamlit/secrets.toml`
```toml
# Preencher conforme o LLM escolhido
ANTHROPIC_API_KEY = "sk-ant-..."   # Opção A
HF_TOKEN = "hf_..."                # Opção B
GROQ_API_KEY = "gsk_..."           # Opção C
```

---

## 8. EXTENSÃO OPCIONAL — RAG COM DADOS DINÂMICOS DO EXCEL

Para responder perguntas que exigem **cálculos em tempo real** sobre os dados
(ex: "qual matrícula tem maior consumo?"), adicionar uma camada de tool calling:

```python
# data_tools.py — ferramentas de consulta direta ao DataFrame
import pandas as pd
import streamlit as st

@st.cache_data
def load_dataframe():
    df = pd.read_excel("Dados_-_Estudo_Micromedição.xlsx")
    df['DATA_INSTALACAO_HIDROMETRO'] = pd.to_datetime(
        df['DATA_INSTALACAO_HIDROMETRO'], dayfirst=True, errors='coerce'
    )
    return df

def query_top_consumers(n=10, categoria=None):
    """Retorna as N ligações com maior consumo no mês atual."""
    df = load_dataframe()
    if categoria:
        df = df[df['CATEGORIA_PRINCIPAL'] == categoria]
    return df.nlargest(n, 'VOLUME_FATURADO')[
        ['MATRICULA', 'CATEGORIA_PRINCIPAL', 'VOLUME_FATURADO', 'VALOR_TOTAL']
    ].to_string(index=False)

def query_anomalies():
    """Retorna resumo das anomalias detectadas."""
    df = load_dataframe()
    anomalias = df[df['VOLUME_REAL'].fillna(0) < df['VOLUME_LIDO'].fillna(0) - 1]
    zero_ativo = df[(df['SIT._LIG_AGUA'] == 'Ativa') & (df['VOLUME_LIDO'].fillna(0) == 0)]
    return {
        "divergencia_lido_real": len(anomalias),
        "consumo_zero_ativo": len(zero_ativo),
        "matriculas_divergencia": anomalias['MATRICULA'].tolist()
    }
```

---

## 9. EXECUÇÃO E DEPLOY

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar localmente
streamlit run app.py

# Deploy gratuito no Streamlit Community Cloud:
# 1. Publicar código no GitHub (sem o secrets.toml)
# 2. Acessar share.streamlit.io
# 3. Conectar repositório
# 4. Adicionar secrets na interface web do Streamlit Cloud
```

---

## 10. ANTIPADRÕES A EVITAR

- ❌ **Não** usar `@st.cache_data` no `build_rag_chain` — usar `@st.cache_resource`
  (o chain contém objetos não serializáveis como conexões de modelo)
- ❌ **Não** recriar o índice FAISS a cada interação — o `@st.cache_resource` garante
  que seja construído apenas uma vez por sessão do servidor
- ❌ **Não** armazenar API keys no código-fonte — sempre usar `st.secrets` ou variáveis
  de ambiente
- ❌ **Não** usar `ConversationBufferMemory` sem limite de janela (`k`) — em conversas
  longas, o contexto excede o limite de tokens do LLM. Usar `ConversationBufferWindowMemory`
- ❌ **Não** enviar o DataFrame inteiro como contexto — o RAG deve recuperar apenas os
  chunks relevantes. Dados tabulares em massa excedem o contexto do LLM
- ❌ **Não** misturar `st.session_state["messages"]` (histórico de exibição) com o
  `memory` interno do LangChain — são dois registros independentes que devem ser
  mantidos separados
