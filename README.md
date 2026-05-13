# sanova-micromedicao-dashboard

**Dashboard de Analise Comercial de Micromedicao** — Streamlit dashboard for commercial analysis of sanitation micro-metering data.

> Teste pratico para Analista de Dados | SANOVA — Inovacao em Saneamento

---

## Sobre Este Projeto

Este trabalho demonstra capacidade de engenharia de dados e analise de sistemas comerciais de saneamento, com foco em **micromedicao, deteccao de anomalias e recuperacao de receita**.

A SANOVA (sanova.com.br) atua ha quase 15 anos no mercado nacional de saneamento, com mais de 150 clientes impactados. Este projeto aplica esses conhecimentos em um estudo real de dados comerciais de uma concessionaria de saneamento — **1.912 ligacoes** ao longo de **13 meses**.

---

## O que Este Dashboard Faz

O dashboard responde perguntas estrategicas sobre o sistema de abastecimento:

| Pergunta | Aba |
|---|---|
| Quais ligacoes geram/pagam receita? | Visao Geral |
| Onde ha sinais de fraude? | Anomalias & Fraudes |
| Quanto custa o consumo zero? | Consumo Zero |
| Quais hidrometros precisam troca? | Hidrometros |
| Quanto podemos recuperar de receita? | Recuperacao de Receita |
| Os dados sao confiaveis? | Qualidade de Dados |
| Perguntas em linguagem natural? | Chatbot IA |

---

## Arquitetura do Sistema

```mermaid
flowchart TD
    subgraph RAW["data/raw/"]
        A["micromedicao.xlsx\n132 colunas"]
    end

    subgraph ETL["src/etl/"]
        B["extractor.py"]
        C["transformer.py\n10 passos"]
        D["loader.py\nCSV + validacao"]
    end

    subgraph PROCESSED["data/processed/"]
        E["micromedicao_tratado.csv\n1.912 x 151"]
    end

    subgraph DASHBOARD["src/dashboard/"]
        F["load_data.py\n@st.cache_data"]
        G["main.py\nsidebar + filtros"]
        H["tabs/\n6 abas analiticas"]
        I["chat/\nRAG + Llama-3.1-8B"]
    end

    subgraph CHATBOT["Chatbot IA (sob demanda)"]
        J["knowledge_base.py\nChunks estaticos + dinamicos"]
        K["rag_pipeline.py\nInMemoryVector + Embeddings + Memory"]
        L["llm_config.py\nHuggingFace Inference Providers"]
    end

    A --> B --> C --> D --> E
    E --> F --> G
    G --> H
    G --> I
    I --> J --> K --> L

    style RAW fill:#1a1a2e,color:#eee
    style ETL fill:#16213e,color:#eee
    style PROCESSED fill:#0f3460,color:#eee
    style DASHBOARD fill:#1a3a2e,color:#eee
    style CHATBOT fill:#1a3a2e,color:#eee
```

```mermaid
flowchart LR
    CSV["micromedicao_tratado.csv"]
        --> CACHE["@st.cache_data\nload_data"]
        --> FILTERS["Sidebar\nChatbot | Filtros | Toggles"]
        --> TAB1["Visao Geral"]
        --> PLT1["Plotly KPIs + Area"]
        --> CSV

    FILTERS --> TAB2["Anomalias"] --> PLT2["Scatter + Barras"]
    FILTERS --> TAB3["Consumo Zero"] --> PLT3["Histograma"]
    FILTERS --> TAB4["Hidrometros"] --> PLT4["Pizza + Barras"]
    FILTERS --> TAB5["Recuperacao"] --> PLT5["Waterfall + Gauge"]
    FILTERS --> TAB6["Qualidade"] --> PLT6["Heatmap + Tabela"]
    FILTERS -.-> CHAT["Chatbot IA\nRAG + Llama + Memory"]
    CHAT -.-> FILTERS

    style CSV fill:#1a1a2e,color:#eee
    style CACHE fill:#0f3460,color:#eee
    style FILTERS fill:#16213e,color:#eee
    style TAB1,TAB2,TAB3,TAB4,TAB5,TAB6 fill:#0f3460,color:#eee
    style PLT1,PLT2,PLT3,PLT4,PLT5,PLT6 fill:#2980B9,color:#fff
    style CHAT fill:#27AE60,color:#fff
```

---

## Estrutura do Projeto

```
dashboard-sanova/
├── run.py
├── pyproject.toml
├── .env.example / .env.local
├── src/
│   ├── dashboard/
│   │   ├── main.py              # Entry point
│   │   ├── load_data.py         # @st.cache_data
│   │   ├── config.py            # Premissas
│   │   ├── utils.py             # Helpers
│   │   ├── chat/                # Chatbot IA
│   │   │   ├── llm_config.py    # HuggingFace LLM
│   │   │   ├── rag_pipeline.py  # InMemoryVector + embeddings
│   │   │   └── knowledge_base.py # Base de conhecimento
│   │   └── tabs/
│   │       ├── overview.py       # KPIs + IQD
│   │       ├── anomalies.py      # Fraudes + outliers
│   │       ├── zero_consumption.py
│   │       ├── meters.py
│   │       ├── recovery.py
│   │       └── data_quality.py
│   └── etl/
│       ├── extractor.py
│       ├── transformer.py        # 10 passos
│       ├── loader.py
│       └── run_pipeline.py
├── data/
│   ├── raw/micromedicao.xlsx
│   ├── processed/micromedicao_tratado.csv
│   └── stage/validation_log.json
└── tests/                       # 34 testes pytest
```

---

## ETL — Pipeline de Engenharia de Dados

```mermaid
flowchart LR
    XLSX["Excel Fonte\n132 cols"] --> N1["1. Normalizar\nuppercase + acentos"]
    N1 --> N2["2. Decimal BR\nvirgula -> ponto"]
    N2 --> N3["3. Converter\ndatas DD/MM/AAAA"]
    N3 --> N4["4. Missing cadastral\n82 ligacoes"]
    N4 --> N5["5. Missing economias\nfillna(0)"]
    N5 --> N6["6. Missing volumes\nflag preservada"]
    N6 --> N7["7. Missing valores\n0 para nao-ativos"]
    N7 --> N8["8. Outliers\nP99 + flag"]
    N8 --> N9["9. Enriquecimento\n14 cols calculadas"]
    N9 --> N10["10. Validar\nQ001-Q006"]
    N10 --> CSV["CSV Tratado\n1.912 x 151"]

    style XLSX fill:#e74c3c,color:#fff
    style N1,N2,N3,N4,N5,N6,N7,N8,N9 fill:#2980B9,color:#fff
    style N10 fill:#f39c12,color:#fff
    style CSV fill:#27AE60,color:#fff
```

---

## Chatbot IA Generativa com RAG

Assistente de perguntas em linguagem natural sobre os dados de micromedicao. Integrado na sidebar do dashboard.

```mermaid
flowchart TD
    Q["Pergunta do usuario\n(em PT-BR)"]
        --> EMB["Embedding\nsentence-transformers\nparaphrase-multilingual-MiniLM"]
        --> VEC["InMemoryVectorStore\n(top-4 chunks)"]
        --> LLM["meta-llama/Llama-3.1-8B\nHuggingFace Inference\nProviders (gratuito)"]
        --> A["Resposta\n+ Memoria (k=5)"]

    KB1["Camada Estatica\nknowledge_base.py\n10 chunks tematicos"] --> VEC
    KB2["Camada Dinamica\ngenerate_dynamic_stats(df)\nestatisticas reais"] --> VEC

    style Q fill:#2980B9,color:#fff
    style EMB fill:#16213e,color:#eee
    style VEC fill:#16213e,color:#eee
    style LLM fill:#27AE60,color:#fff
    style A fill:#1a1a2e,color:#eee
    style KB1,KB2 fill:#0f3460,color:#eee
```

### Configuracao do Chatbot

1. Crie conta em [huggingface.co](https://huggingface.co)
2. Gere um Access Token (tipo **Fine-grained**, permissoes **Inference > Make calls to serverless Inference API**)
3. Edite `.env.local`:

```bash
HF_TOKEN=hf_your_token_here
```

> Custo: gratuito — $0.10/mes em credits HF (centenas de perguntas).

---

## Oportunidades de Recuperacao de Receita

```mermaid
flowchart LR
    A["Hidrometros > 5 anos\n414 ligacoes\nR$ 1.87M"]
    B["Vistoriar sem consumo 6m+\n224 ligacoes\nR$ 120k"]
    C["Fraude (LIDO > REAL)\n144 ligacoes\nR$ 144k"]
    D["Sem hidrometro\n1 ligacao\nR$ 1k"]
    E["Receita perdida (missing)\n—\nR$ 362k"]

    A --> TOTAL["Total\n~R$ 2.5M"]
    B --> TOTAL
    C --> TOTAL
    D --> TOTAL
    E --> TOTAL

    style A fill:#27AE60,color:#fff
    style B fill:#f39c12,color:#fff
    style C fill:#E74C3C,color:#fff
    style D fill:#95A5A6,color:#fff
    style E fill:#95A5A6,color:#fff
    style TOTAL fill:#2980B9,color:#fff
```

---

## Abas do Dashboard

| Aba | Conteudo | Principais Graficos |
|---|---|---|
| **Visao Geral** | KPIs + IQD + distribuicao | Area temporal, pizza, barras |
| **Anomalias & Fraudes** | Deteccao LIDO > REAL, outliers | Scatter, barras, tabela priorizada |
| **Consumo Zero** | Perda por tarifa minima | Histograma, barras |
| **Hidrometros** | Tipo, marca, idade, substituicao | Pizza, barras, tabela por idade |
| **Recuperacao de Receita** | Potencial por acao, waterfall | Waterfall, gauge, tabela priorizada |
| **Qualidade de Dados** | IQD, missing, inconsistencias | Heatmap, tabela |

---

## Stack Tecnologica

| Camada | Tecnologia |
|---|---|
| **Framework** | Python 3.10+ · Streamlit |
| **Dados** | Pandas · NumPy · Plotly |
| **IA / LLM** | LangChain · HuggingFace Inference Providers · Llama-3.1-8B-Instruct |
| **Embeddings** | sentence-transformers · `paraphrase-multilingual-MiniLM-L12-v2` |
| **Vector Store** | InMemoryVectorStore (langchain-community) |
| **Gestão** | Poetry · Pytest (34 testes) |

---

## Como Executar

```bash
# 1. Instalar dependencias
poetry install

# 2. Pipeline ETL (so se precisar reprocessar)
python src/etl/run_pipeline.py

# 3. Chatbot (opcional): configurar HF_TOKEN em .env.local
#   Veja secao "Chatbot IA Generativa com RAG" acima.

# 4. Abrir dashboard
python run.py
```

Dashboard disponible em `http://localhost:8501`.

---

## Premissas Tecnicas

| Premissa | Valor | Fonte |
|---|---|---|
| Tarifa minima | R$ 89,03 | Menor VALOR_TOTAL observado |
| Custo unitario da agua | R$ 10/m³ | Estimativa |
| Fator de submedição (> 5 anos) | 15% | ABNT NBR 15538 |
| Anomalia de leitura | LIDO > REAL + 1 m³ | Critério de fraude |
| Outlier extremo | P99 | Metodo estatistico |

---

*Desenvolvido como teste pratico para Analista de Dados — SANOVA (sanova.com.br) | Palhoca/SC | 2026*
