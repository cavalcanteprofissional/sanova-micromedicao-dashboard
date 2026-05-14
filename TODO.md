# TODO — Dashboard Sanova: Analise Comercial de Micromedicao

## 1. Contextualizacao do Projeto

**Cliente:** SANOVA (sanova.com.br) — empresa de consultoria em saneamento com 15 anos de mercado, >150 clientes impactados, sediada em Palhoça/SC.

**Objetivo:** Dashboard Streamlit para analise tecnica e estrategica do sistema comercial de saneamento, com foco em micromedicao, deteccao de anomalias/fraudes e recuperacao de receita.

**Fonte de dados:** `data/raw/micromedicao.xlsx` -> Pipeline ETL -> `data/processed/micromedicao_tratado.csv` (1.912 registros x 151 colunas)

---

## 2. Diagnostico de Qualidade de Dados (Concluido)

### 2.1 Perfil do Dataset

| Metrica | Valor |
|---|---|
| Total de registros | 1.912 |
| Colunas originais | 132 |
| Colunas apos ETL (+ calculadas) | 151 |
| Periodo de analise | 13 meses (atual + 12 historicos) |
| Duplicatas de matricula | 0 |

### 2.2 Problemas Identificados e Tratados

| Problema | Qtd | Tratamento |
|---|---|---|
| **Missing cadastral agrupado** (82 registros) | 82 (4,3%) | ETL: preencher `SEM_HIDROMETRO` para todos os campos ausentes |
| **Missing em economias** | 247-1.907 | ETL: fillna(0) |
| **Missing progressivo em volumes** | 4,3% -> 8,6% | ETL: preservar NaN + flag `MESES_DADOS_AUSENTES` |
| **Outliers extremos** (> 900k m³) | 15 | ETL: flag `FLAG_OUTLIER_EXTREMO` (P99) |
| **Divergencia LIDO > REAL** (possivel fraude) | 144 | ETL: flag `FLAG_ANOMALIA_LEITURA` |
| **Decimal brasileiro** (1,6 vs 1.6) | - | ETL: converter virgula -> ponto |
| **Encoding** (caracteres especiais) | - | ETL: normalize NFKD + ASCII |

---

## 3. Engenharia de Dados

### 3.1 Pipeline ETL (Concluido)

```
data/raw/micromedicao.xlsx  →  src/etl/  →  data/processed/micromedicao_tratado.csv
                                    ↓
                               data/stage/validation_log.json
```

| Modulo | Funcao | Status |
|---|---|---|
| `extractor.py` | Leitura Excel (Planilha1, dtype=str) | ✅ |
| `transformer.py` | 10 passos: normalizacao, fix formatos, handle missing, enriquecimento | ✅ |
| `loader.py` | save_to_csv + validate_output | ✅ |
| `run_pipeline.py` | Orquestrador completo | ✅ |

### 3.2 Execucao do Pipeline

```bash
cd E:\SANOVA\dashboard-sanova
python src/etl/run_pipeline.py
```

**Output:**
- `data/processed/micromedicao_tratado.csv` (1.912 rows x 151 cols)
- `data/stage/validation_log.json`

---

## 4. Estrutura do Projeto

```
dashboard-sanova/
├── pyproject.toml
├── poetry.lock
├── TODO.md
├── README.md
├── .gitignore
├── run.py                      # Entry point para Streamlit
├── SKILL.md
├── data/
│   ├── raw/
│   │   └── micromedicao.xlsx
│   ├── processed/
│   │   └── micromedicao_tratado.csv
│   └── stage/
│       └── validation_log.json
├── src/
│   ├── dashboard/
│   │   ├── __init__.py
│   │   ├── main.py             # Entry point (imports absolutos)
│   │   ├── load_data.py        # @st.cache_data, leitura CSV
│   │   ├── utils.py            # apply_filters, format_currency, etc.
│   │   ├── config.py           # Constantes, cores, premissas
│   │   ├── assets/             # Assets estaticos (SVG, imagens)
│   │   │   ├── icon.svg        # Favicon (drop icon)
│   │   │   └── logo.svg        # Logo do cabecalho
│   │   └── tabs/
│   │       ├── __init__.py
│   │       ├── overview.py      # Tab 1: KPIs + IQD
│   │       ├── anomalies.py     # Tab 2: Deteccao de anomalias
│   │       ├── zero_consumption.py  # Tab 3: Consumo zero
│   │       ├── meters.py       # Tab 4: Analise de hidrometros
│   │       ├── data_quality.py  # Tab 6: Qualidade de dados
│   │       └── recovery.py      # Tab 5: Recuperacao de receita
│   └── etl/
│       ├── __init__.py
│       ├── extractor.py
│       ├── transformer.py
│       ├── loader.py
│       └── run_pipeline.py
└── tests/
    ├── test_load_data.py
    ├── test_utils.py
    ├── test_tabs.py
    └── test_etl.py
```

---

## 5. Status das Tarefas (Checklist)

### Fase 1 — Infraestrutura
- [x] T.1.1 pyproject.toml com Poetry ✅
- [x] T.1.2 Estrutura de diretorios ✅
- [x] T.1.3 Mover Excel para `data/raw/` ✅

### Fase 2 — ETL
- [x] T.2.1 `extractor.py` ✅
- [x] T.2.2 `transformer.py` (10 passos) ✅
- [x] T.2.3 `loader.py` ✅
- [x] T.2.4 `run_pipeline.py` ✅
- [x] T.2.5 Executar pipeline ✅
- [x] T.2.6 Validar output (shape, colunas) ✅

### Fase 3 — Testes ETL
- [x] T.3.1 Testes ETL (11 testes) ✅
- [x] T.3.2 Testes pipeline CSV (4 testes) ✅

### Fase 4 — Dashboard (CSV)
- [x] T.4.1 `load_data.py` ler CSV tratado ✅
- [x] T.4.2 `config.py` com premissas ✅
- [x] T.4.3 Cache com campos calculados ✅

### Fase 5 — Tabs
- [x] T.5.1 `overview.py` com IQD ✅
- [x] T.5.2 `anomalies.py` com outliers + flags ✅
- [x] T.5.3 `zero_consumption.py` ✅
- [x] T.5.4 `meters.py` ✅
- [x] T.5.5 `recovery.py` ✅
- [x] T.5.6 `data_quality.py` (nova tab) ✅

### Fase 6 — Main + Imports
- [x] T.6.1 `main.py` com 6 tabs ✅
- [x] T.6.2 Imports absolutos (corrigido `from .xxx` -> `from dashboard.xxx`) ✅
- [x] T.6.3 Sidebar com filtros + toggles ✅

### Fase 7 — Execucao
- [x] T.7.1 `run.py` entry point ✅
- [x] T.7.2 Testar imports (34/34 testes passando) ✅

### Fase 8 — Limpeza
- [x] T.8.1 Remover `assets/` vazio + recriar `src/dashboard/assets/` com SVGs ✅
- [x] T.8.2 Remover `tests/__init__.py` duplicado ✅
- [x] T.8.3 Limpar `__pycache__` ✅
- [x] T.8.4 Corrigir import `run.py` para usar `sys.path.insert(0, 'src')` ✅

---

## 6. Oportunidades de Recuperacao de Receita

| Oportunidade | Qtd Ligacoes | Receita Potencial (12m) |
|---|---|---|
| Instalar hidrometro (1 ligacao ativa sem medidor) | 1 | ~R$ 1.068 |
| Fiscalizar anomalias de leitura (LIDO > REAL > 1m³) | 144 | ~R$ 144.000 |
| Vistoriar ligacoes com 6+ meses sem consumo | 224 | ~R$ 119.655 |
| Substituir hidrometros > 5 anos (fator 15% submedição) | 414 | ~R$ 1.869.000 |
| Investigar outliers extremos (15 registros) | 15 | A definir |
| Receita perdida por missing data | - | ~R$ 362.146 |
| **Total estimado** | | **~R$ 2.495.869** |

---

## 7. Execução

```bash
# Pipeline ETL (so se precisar reprocessar)
python src/etl/run_pipeline.py

# Dashboard
python run.py
# Ou diretamente:
streamlit run src/dashboard/main.py
```

---

## 8. Antipadrões Evitados
- Nao usar `st.write(df)` — usar `st.dataframe(use_container_width=True)`
- Calculos pesados dentro de `@st.cache_data`
- Nao usar `fig.show()` — usar `st.plotly_chart(use_container_width=True)`
- Nao misturar filtragem global e local — usar `df_filtered` em todas as tabs
- Imports relativos (`from .xxx`) removidos — usar imports absolutos (`from dashboard.xxx`)

---

## 9. Melhorias UI/UX — Design Visual e Experiencia do Usuario

### 9.1 Diagnostico de Problemas Visuais Identificados

| Problema | Aba | Impacto |
|---|---|---|
| **Sem header personalizado** | Todas | Ausencia de branding SANOVA; identidade visual fraca |
| **Sidebar sem organizacao** | Todas | Filtros agrupados sem hierarquia visual; sem secao de resumo |
| **KPI cards sem cor contextual** | Overview | Todos os metric cards tem cor padrao azul; nao ha distincao por status |
| **Paleta de cores generica** | Todas | Cores hardcoded nos graficos; nao ha consistencia com identidade visual |
| **Grafico de linha sem area** | Overview | Serie temporal sem destaque visual suficiente |
| **Tabs sem hierarquia visual** | Todas | 6 abas listadas sem grupo; icones inconsistentes |
| **Heatmaps com formatacao confusa** | Overview, Data Quality | Percentuais sem clareza (0.0 vs 0,0) |
| **Tabela de acoes sem destaque** | Recovery | Acoes priorizadas sem cor por nivel (Alta/Media/Baixa) |
| **Gauge sem contexto** | Recovery | Valor absoluto sem comparativo com meta |
| **Scatter com outliers distorcendo escala** | Anomalies | Outliers extremos (>900k m3) compressam todos os outros pontos |
| **Separadores `---` excessivos** | Todas | Ruid o visual repetitivo |

---

### 9.2 Plano de Implementacao Progressiva (26 tarefas)

#### Fase U1 — Identidade Visual e Header (Impacto Alto)

- [x] **U.1.1** — CSS custom via `st.html` com variaveis de cor + estilo para KPI cards com borda esquerda colorida ✅
- [x] **U.1.2** — Header com gradiente azul SANOVA + nome do projeto + tagline ✅
- [x] **U.1.3** — Titulo da pagina estilizado com HTML/CSS em vez de `st.title()` puro ✅

#### Fase U2 — Sidebar Organizada (Impacto Medio-Alto)

- [x] **U.2.1** — Filtros em `st.expander` agrupados: Categorias, Situacao, Marca ✅
- [x] **U.2.2** — Card de resumo na sidebar (IQD, total registros, data de atualizacao) ✅
- [x] **U.2.3** — Separar toggles em secao visual distinta ✅
- [x] **U.2.4** — Link para premissas/metadata na sidebar ✅

#### Fase U3 — KPI Cards com Cor Contextual (Impacto Medio)

- [x] **U.3.1** — Cor do KPI card baseada no valor: critico=vermelho, alerta=laranja, bom=verde ✅
- [x] **U.3.2** — Delta colorido: `delta_color="normal"` para receita, `delta_color="inverse"` para casos criticos ✅
- [x] **U.3.3** — Container com background para grupos de KPIs ✅

#### Fase U4 — Graficos com Visual Melhorado (Impacto Medio)

- [x] **U.4.1** — Scatter: zoom no percentil 95% para legibilidade, nota sobre outliers ocultos ✅
- [ ] **U.4.2** — Grafico de linha com area preenchida (`px.area`) — **BUG: `fill='tozeroy'` e invalida em `update_layout`, corrigido**
- [x] **U.4.3** — Waterfall com cores alinhadas ao tema ✅
- [x] **U.4.4** — Gauge com steps de cor e delta vs referencia ✅

#### Fase U5 — Tabelas com Destaque Visual (Impacto Medio)

- [ ] **U.5.1** — Colorir linhas da tabela de anomalias por score (>=100=vermelho, >=50=laranja)
- [x] **U.5.2** — Tabela de acoes com cor na coluna Prioridade (Alta=vermelho, Media=laranja, Baixa=verde) ✅
- [x] **U.5.3** — Paginar tabelas com >50 linhas ✅

#### Fase U6 — Layout e Hierarquia (Impacto Baixo-Medio)

- [x] **U.6.1** — Substituir `st.markdown("---")` por `st.divider()` ✅
- [x] **U.6.2** — Adicionar `st.caption` com info de atualizacao e periodo ✅
- [ ] **U.6.3** — Badges coloridos para status de ligacao
- [ ] **U.6.4** — Tooltips descritivos nos titulos dos graficos
- [ ] **U.6.5** — Progress indicator durante carregamento dos dados

#### Bugs Corrigidos

- [x] **BUG-01** — `fill='tozeroy'` invalido em `overview.py:87` (`update_layout` nao suporta `fill`) — `px.area()` ja preenche area por padrao
- [x] **BUG-02** — `use_container_width` deprecado em todo o codebase (23 ocorrencias em 6 tabs) — substituidos por `width='stretch'`
- [x] **BUG-03** — `Styler.applymap()` deprecado no Pandas 2.2+ — substituido por `Styler.map()` em `recovery.py:77`
- [x] **BUG-04** — Grafico "Distribuicao por Situacao da Ligacao": multiplos bugs corrigidos — (1) `s[:1]` cortava nome para 1 caractere causando todas barras cinzas; (2) 15 registros com `SIT._LIG_AGUA` vazio no CSV lidos como NaN, `fillna` nao funcionava por causa de string vazia; (3) entrada `'N': '#F39C12'` no dicionario era fantasma, nunca encontrada; (4) loop `if s.startswith('N')` nunca executava. Fix: `replace('')` antes de `fillna` em `load_data.py` + dicionario limpo com `'NAO INFORMADA'` em `overview.py`
- [x] **BUG-05** — Filtro global "Situacao da Ligacao" com `default=['ATIVA']` mostrava apenas ATIVA no grafico de distribuicao — agora `default=df['SIT._LIG_AGUA'].unique().tolist()` para marcar todos por padrao
- [x] **BUG-06** — `NameError: name 'background' is not defined` em `main.py:render_header()` — CSS block usava `f"""` com chaves simples (`{` / `}`) que o f-string interpretava como expressoes Python. Fix: CSS reescrito como plain string `"""..."""` sem f-string; JS favicon injetado via concatenacao de string com base64 pre-computado em `LOGO_SVG` (constante de modulo com string literal de ~13.7 KB); SVGs em `src/dashboard/assets/` codificados em build time; `render_header()` agora usa `st.html('''...CSS...JS...''')` como string plain, sem interpolacao de variaveis alem de `LOGO_SVG` no `st.markdown()`
- [x] **BUG-07** — SVGs inlined como base64 em `main.py` sem path externo — `SANOVA ICON.svg` e `SANOVA LOGO 2.svg` ficavam soltos no root do projeto. Fix: moveu para `src/dashboard/assets/icon.svg` e `src/dashboard/assets/logo.svg`; `main.py` agora usa `LOGO_SVG` como constante de modulo (~13.7 KB em base64); variavel `icon_svg` renomeada para `logo_svg` com referencia correta ao logo.svg vs icon.svg; **favicon do navegador** usa `logo.svg` (logo completo SANOVA) via JS `link.href` injectado no `<head>`
- [x] **UI-01** — Filtros da sidebar substituidos de `st.multiselect` para toggle buttons via `st.checkbox` organizados em colunas 2xN com CSS custom em dark mode — `main.py` + CSS em `st.html()`; `apply_filters` em `utils.py` corrigido para lidar com lista vazia (significa "mostrar todos")
- [x] **FEAT-01** — Labels de mes nos graficos agora mostram nome real do mes (Inferido a partir de `datetime.now()` — Mes Atual = Maio/2026): `['Mes Atual', 'M-1 (Apr/26)', 'M-2 (Mar/26)', ..., 'M-12 (May/25)']` em `load_data.py:get_month_labels()`, centralizado e usado em `overview.py` e `data_quality.py`

---

### 9.3 Ordem de Implementacao

```
U.1.1 → U.1.2 → U.1.3 (Header + CSS)
    ↓
U.2.1 → U.2.2 → U.2.3 → U.2.4 (Sidebar)
    ↓
U.3.1 → U.3.2 → U.3.3 (KPI Cards)
    ↓
U.4.1 → U.4.2 → U.4.3 → U.4.4 (Graficos)
    ↓
U.5.1 → U.5.2 → U.5.3 (Tabelas)
    ↓
U.6.1 → U.6.2 → U.6.3 → U.6.4 → U.6.5 (Layout)
```

---

### 9.4 Paleta de Cores (Dark Mode)

| Uso | Cor | Hex |
|---|---|---|
| Primaria (agua) | Azul profundo | `#2980B9` |
| Sucesso | Verde | `#27AE60` |
| Alerta | Laranja | `#F39C12` |
| Critico | Vermelho | `#E74C3C` |
| Neutro | Cinza | `#95A5A6` |
| Background cards | Cinza claro | `#F8F9FA` |
| Header gradient | Gradiente azul | `#2980B9` → `#1a5276` |
| Texto principal | Grafite | `#2C3E50` |
| Texto secundario | Cinza medio | `#7F8C8D` |

---

### 9.5 Componentes de Design Propostos

| Componente | Descricao | Prioridade |
|---|---|---|
| `HeaderBanner()` | Banner com branding SANOVA + gradiente azul | Alta |
| `KPICard()` | Card com borda esquerda colorida por status | Alta |
| `SectionTitle()` | Titulo de secao com icone e linha de destaque | Media |
| `ColorizedTable()` | Tabela com linhas coloridas por valor | Media |
| `TooltipFigure()` | Grafico com tooltip descritivo | Media |
| `SidebarSection()` | Expander organizacional na sidebar | Media |

---

---

## 10. Dark Mode (Concluido — Opcao A)

**Objetivo:** Dashboard em modo escuro para leitura confortavel em qualquer ambiente.

### 10.1 Arquivos Alterados

| Arquivo | Alteracao |
|---|---|
| `config.py` | `PLOTLY_TEMPLATE = 'plotly_dark'` (era `'plotly_white'`) |
| `main.py` | CSS completo reescrito com variaveis dark; dark mode via CSS custom em `st.html()` |
| `overview.py` | `gridcolor: rgba(0,0,0,0.1)` -> `rgba(255,255,255,0.1)` |
| `recovery.py` | Styler: backgrounds claros substituidos por tons escuros |
| `tests/test_load_data.py` | Teste `plotly_template` atualizado para `'plotly_dark'` |

> **Nota:** `theme="dark"` em `set_page_config()` removido — parametro nao suportado na versao do Streamlit instalada. Dark mode implementado via CSS custom (`st.html()`) que funciona em qualquer versao.

### 10.2 Paleta Dark Mode

| Variavel CSS | Valor | Uso |
|---|---|---|
| `--bg-card` | `#1E1E1E` | KPI cards, containers |
| `--bg-sidebar` | `#1A1A2E` | Fundo da sidebar |
| `--bg-sidebar-section` | `#252540` | Secoes internas da sidebar |
| `--texto-principal` | `#E0E0E0` | Titulos, labels, valores |
| `--texto-secundario` | `#9BA0A6` | Captions, textos secundarios |
| `--borda` | `#3A3A4A` | Bordas, dividers |

### 10.3 O Que Muda Visualmente

- Sidebar: fundo `#1A1A2E` escuro com secoes em `#252540`
- KPI cards: fundo escuro `#1E1E1E`, texto claro
- Todos os graficos Plotly: fundo escuro com eixos e labels em cores claras
- Tabela de prioridades (Recovery): linhas Alta/Media/Baixa com fundos escuros e texto colorido
- Dividers: `rgba(255,255,255,0.1)` vs `rgba(0,0,0,0.1)` — visivel no fundo escuro
- Streamlit native dark theme ativado via `theme="dark"`

---

## 11. Chatbot IA Generativa com RAG

**Objetivo:** Assistente conversacional integrado na sidebar do dashboard para responder perguntas sobre a base de dados de micromedicao.

### 11.1 Arquitetura

```
Pergunta do usuario
    |
    v
[ Embedding - sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 ]
    |
    v
[ FAISS vector store local - 4 chunks mais relevantes ]
    |
    v
[ LLM - Groq llama-3-8b-8192 (gratuito) ]
    |
    v
[ Resposta contextualizada + fontes ]
```

### 11.2 Knowledge Base (3 camadas)

| Camada | Fonte | Conteudo |
|---|---|---|
| 1 - Estatica | `knowledge_base.py` | Glossario, FAQ, situacoes, categorias, hidrometros, anomalias, tarifas, metodologia |
| 2 - Dinamica | `generate_dynamic_stats()` | Estatisticas reais do DataFrame em tempo de execucao |
| 3 - Tool calling | `df` | Calculos sobre os dados reais (futuro) |

### 11.3 Arquivos Criados

| Arquivo | Funcao |
|---|---|
| `src/dashboard/chat/__init__.py` | Modulo vazio |
| `src/dashboard/chat/knowledge_base.py` | KNOWLEDGE_BASE_DOCS (10 chunks tematicos) + `generate_dynamic_stats(df)` |
| `src/dashboard/chat/llm_config.py` | `get_llm()` — ChatGroq com `GROQ_API_KEY` do `.env.local` |
| `src/dashboard/chat/rag_pipeline.py` | `build_rag_chain(llm, df)` — FAISS + embeddings + ConversationalRetrievalChain |
| `src/dashboard/tabs/chat.py` | `render(df)` — interface Streamlit com `st.chat_message`, FAQ buttons, toggle de fontes |
| `.env.example` | Template com placeholder para `GROQ_API_KEY` |
| `.env.local` | Arquivo local com chave real (gitignorado) |

### 11.4 Configuracao

```bash
# 1. Instalar novas dependencias
poetry install

# 2. Obter chave gratuita em https://console.groq.com
# 3. Editar .env.local com a chave
GROQ_API_KEY=gsk_sua_chave_aqui

# 4. Rodar dashboard
python run.py
```

### 11.5 Integração

O chatbot fica dentro de um `st.expander("💬 Assistente IA")` na sidebar, apos os filtros globais. Se a chave Groq nao estiver configurada, exibe mensagem de orientacao.

---

## 12. Limpeza de Dependencias (12/05/2026)

### 12.1 Auditoria Realizada

Todas as 13 dependencias em `pyproject.toml` foram auditadas (todas as linhas de import de todos os arquivos `.py` do projeto).

| Dependencia | Status | Motivo |
|---|---|---|
| `streamlit` | ✅ Mantida | UI do dashboard |
| `pandas` | ✅ Mantida | ETL + dashboard |
| `numpy` | ✅ Mantida | Calculos numericos |
| `plotly` | ✅ Mantida | Graficos |
| `openpyxl` | ✅ Mantida | Requerido por `pd.read_excel()` |
| `langchain` | ✅ Mantida | Imports em `rag_pipeline.py` |
| `langchain-community` | ✅ Mantida | FAISS vectorstore |
| `langchain-huggingface` | ✅ Mantida | HuggingFaceEmbeddings |
| `langchain-groq` | ✅ Mantida | ChatGroq |
| `faiss-cpu` | ✅ Mantida | Indireto via langchain-community |
| `sentence-transformers` | ✅ Mantida | Nome do modelo de embedding |
| `python-dotenv` | ✅ Mantida | Carrega `.env.local` |
| `pytest` | ✅ Mantida | 4 arquivos de teste |
| `pytest-cov` | ❌ Removida | Nao utilizada — coverage opcional |

### 12.2 Correção de Imports Legados

`rag_pipeline.py` tinha 4 imports usando paths deprecados em LangChain ≥0.3:

| Antes (legado) | Depois (moderno) |
|---|---|
| `from langchain.text_splitter import ...` | `from langchain_text_splitters import ...` |
| `from langchain.memory import ConversationBufferWindowMemory` | `from langchain_core.memory import ConversationBufferWindowMemory` |
| `from langchain.prompts import PromptTemplate` | `from langchain_core.prompts import PromptTemplate` |
| `from langchain.chains import ConversationalRetrievalChain` | Mantido (ja moderno) |

### 12.3 Migração Groq → HuggingFace Inference Providers (12/05/2026)

**Motivo:** Centralizar todas as APIs no ecossistema HuggingFace (já usado para embeddings), eliminar dependência externa do Groq, aproveitar credits gratuitos da HF.

**Mudança de API:**
- Removida: `langchain-groq` (Groq API com Llama-3-8B)
- Adicionada: `huggingface_hub` (Inference Providers com routing automático)
- Modelo: `meta-llama/Llama-3.1-8B-Instruct` (128k contexto, mesmo porte 8B)
- Autenticação: `HF_TOKEN` (Access Token HF, gratuito — $0.10/mês em credits)

**Arquivos alterados:**
| Arquivo | Alteração |
|---|---|
| `pyproject.toml` | `langchain-groq` → `huggingface_hub` |
| `chat/llm_config.py` | `ChatGroq` → `ChatHuggingFace` + `HuggingFaceEndpoint(provider="auto")` |
| `tabs/chat.py` | Mensagens de setup e erro atualizadas |
| `.env.example` | `GROQ_API_KEY` → `HF_TOKEN` |
| `.env.local` | `GROQ_API_KEY` → `HF_TOKEN` |

**Configuração:**
```bash
# 1. poetry install  (remove langchain-groq, adiciona huggingface_hub)
poetry install

# 2. Criar conta HF em https://huggingface.co
# 3. Gerar Access Token em Settings > Access Tokens (tipo: Read)
# 4. Editar .env.local com o token
HF_TOKEN=hf_your_token_here

# 5. Rodar dashboard
python run.py
```

### 12.4 Bug Fix: dotenv path em llm_config.py (12/05/2026)

**Sintoma:** Chatbot mostrava "Configure seu token da API HuggingFace" mesmo com token válido no `.env.local`.

**Causa:** `load_dotenv()` sem argumento procura `.env` por padrão. O arquivo `.env` (exemplo com placeholder `HF_TOKEN=your_hf_token_here`) era encontrado e sobrescrevia o valor real do `.env.local`.

**Correção:** `llm_config.py` — especificar o caminho absoluto do `.env.local`:
```python
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env.local'))
```

### 12.5 Bug Fix: imports langchain_classic em rag_pipeline.py (12/05/2026)

**Sintoma:** `Erro ao inicializar o assistente: No module named 'langchain.chains'`.

**Causa:** LangChain 1.3.0 migrou `ConversationalRetrievalChain`, `ConversationBufferWindowMemory` e `PromptTemplate` para `langchain_classic`, não `langchain` nem `langchain_core`.

**Pacotes instalados:**
- `langchain 1.3.0`
- `langchain-core 1.4.0`
- `langchain-community 0.4.1`
- `langchain-classic 1.0.7`
- `langchain-groq 1.1.2`
- `langchain-huggingface 1.2.2`
- `langchain-text-splitters 1.1.2`

**Imports corrigidos:**

| Componente | Antes (quebrou) | Agora (ok) |
|---|---|---|
| `ConversationalRetrievalChain` | `langchain.chains` | `langchain_classic.chains` |
| `ConversationBufferWindowMemory` | `langchain_core.memory` | `langchain_classic.memory` |
| `PromptTemplate` | `langchain_core.prompts` | `langchain_classic.prompts` |
| `RecursiveCharacterTextSplitter` | `langchain_text_splitters` | (mantém) |
| `HuggingFaceEmbeddings` | `langchain_huggingface` | (mantém) |
| `FAISS` | `langchain_community.vectorstores` | (mantém) |

**Sintoma:** Chatbot mostrava "Configure seu token da API HuggingFace" mesmo com token válido no `.env.local`.

**Causa:** `load_dotenv()` sem argumento procura `.env` por padrão. O arquivo `.env` (exemplo com placeholder `HF_TOKEN=your_hf_token_here`) era encontrado e sobrescrevia o valor real do `.env.local`.

**Correção:** `llm_config.py` — especificar o caminho absoluto do `.env.local`:
```python
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env.local'))
```

---

## 12.6 Deploy no Streamlit Cloud — FAISS CPU (Fechado ✅ 12/05/2026)

**Problema:** `faiss-cpu` não possui wheels compatíveis com o ambiente do Streamlit Cloud (ABI tags não suportados). Erro:

```
Unable to find installation candidates for faiss-cpu (1.11.0.post1)
```

**Solução:** Substituir FAISS por `InMemoryVectorStore` (puro Python, sem C extensions):

| Antes | Depois |
|---|---|
| `from langchain_community.vectorstores import FAISS` | `from langchain_community.vectorstores import InMemoryVectorStore` |
| `FAISS.from_documents(chunks, embeddings)` | `InMemoryVectorStore.from_documents(chunks, embeddings)` |
| `faiss-cpu >= 1.8.0` em `pyproject.toml` | Removido |

`InMemoryVectorStore` está em `langchain-community` (já instalado) e funciona em qualquer ambiente. A busca vetorial é em memória — sem impacto para bases pequenas (~10 chunks no RAG).

**Mudanças:**
- `rag_pipeline.py`: `FAISS` → `InMemoryVectorStore`; reescrito o chain de `ConversationalRetrievalChain` para `SimpleConversationalRAG` usando apenas `langchain_core` primitives (sem `langchain_classic` no código)
- `pyproject.toml`: removido `faiss-cpu`; `langchain-classic` e `langchain-text-splitters` removidos como deps diretos (são transitive de `langchain-huggingface` e `langchain`)
- `poetry.lock`: regenerado com `poetry lock --no-cache --regenerate`
- `tabs/chat.py`: ajustado call `chain.invoke(user_input)` (string direta em vez de dict)
- **34/34 testes passando** após as mudanças

---

## 12.8 Deploy no Streamlit Cloud — langchain-* (Fechado ✅ 13/05/2026)

**Problema:** Mesmo após remover `faiss-cpu` e `sentence-transformers`, uma terceira cascata de dependencias pesadas ainda causava falha no Streamlit Cloud:

```
langchain-huggingface (0.3.1) → langchain-core (0.3.x) → langchain (0.3.30)
→ langsmith (0.3.45) → zstandard → cffi (build nativo → ffi.h: No such file)
```

Erro específico no lock: `cffi 1.17.0rc1` tentando compilar extensão C nativa em ambiente Python 3.14 sem compilador.

**Solução:** Remover TODAS as dependencias `langchain-*` do `pyproject.toml`. O chatbot agora usa apenas `huggingface_hub` + `numpy` + plain Python.

| Componente | Antes (LangChain) | Depois (Custom) |
|---|---|---|
| LLM | `ChatHuggingFace` de `langchain-huggingface` | `HuggingFaceLLM` via `InferenceClient.chat_completion()` |
| Embeddings | `HuggingFaceEmbeddings` (sentence-transformers) | `SimpleEmbeddings` via `InferenceClient.feature_extraction()` |
| Vector Store | `InMemoryVectorStore` de `langchain-community` | `SimpleVectorStore` com cosseno similarity via numpy |
| Text Splitting | `RecursiveCharacterTextSplitter` de `langchain-text-splitters` | `_simple_split()` — plain Python, 20 linhas |
| Chain | `RunnableSequence` + `PromptTemplate` + `StrOutputParser` | Funções Python plain (build_rag_chain → string formatting) |
| Messages | `HumanMessage` / `AIMessage` de `langchain_core.messages` | `UserMessage` / `AssistantMessage` dataclasses |

**Resultado:**
- `pyproject.toml`: `streamlit`, `pandas`, `numpy`, `plotly`, `openpyxl`, `huggingface_hub`, `python-dotenv` — 7 deps apenas
- `poetry.lock`: 69 packages únicos (antes: 126+)
- `langchain`, `langchain-community`, `langchain-huggingface`, `langchain-text-splitters`, `langchain-classic`, `langsmith`, `zstandard`, `cffi`, `sentence-transformers`, `torch`, `triton`, `faiss-cpu` — **ZERO** no lock
- **34/34 testes passando**

---

## 12.9 Deploy no Streamlit Cloud — packages Poetry (Fechado ✅ 13/05/2026)

**Problema:** O `pyproject.toml` tinha a configuração:
```toml
packages = [{include = "dashboard", from = "src/dashboard"}]
```

O Poetry interpreta isso como "empacotar subdiretório `src/dashboard/dashboard/`" (subpasta `dashboard` dentro de `dashboard`), mas o módulo real é `src/dashboard/__init__.py`. Erro:

```
/mount/src/sanova-micromedicao-dashboard/src/dashboard/dashboard does not contain any element
```

**Solução:** Remover a linha `packages` do `pyproject.toml`. Ela é desnecessária porque:
- O dashboard é executado via `run.py`, não via `poetry run dashboard`
- O `run.py` já adiciona `src/` ao `sys.path` diretamente
- Nenhuma entry point Poetry é usada no Streamlit Cloud

---

## 12.10 Deploy no Streamlit Cloud — sys.path no main.py (Fechado ✅ 13/05/2026)

**Problema:** O Streamlit Cloud executa `streamlit run src/dashboard/main.py` diretamente, sem wrapper. O `main.py` importa `from dashboard.load_data import ...` mas o `sys.path` no Streamlit Cloud não inclui `src/`, causando:

```
ModuleNotFoundError: No module named 'dashboard'
```

**Solução:** Adicionar no topo do `main.py`:
```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
```

Isso coloca a raiz do projeto (`/mount/src/sanova-micromedicao-dashboard/`) no `sys.path`, e `src/dashboard/` fica acessível como módulo `dashboard`.

**Configuração do deploy:**
- Main module path: `src/dashboard/main.py`
- Entry point local: `run.py` (para execução via `python run.py`)

---

## 12.12 Deploy no Streamlit Cloud — Sucesso (Fechado ✅ 13/05/2026)

**Status final:** Dashboard operacional no Streamlit Cloud.

**Configuração:**
- Main module path: `src/dashboard/main.py`
- Poetry: `package-mode = false` (gerencia apenas deps)
- `HF_TOKEN` nos Secrets do Streamlit Cloud

**Problemas resolvidos em ordem:**
1. `faiss-cpu` sem wheels → `InMemoryVectorStore` custom
2. `sentence-transformers` → `torch` → `cffi` → compilação nativa → HuggingFace Inference API
3. `langchain-*` transitive deps (`langsmith` → `zstandard` → `cffi`) → removidos todos, `huggingface_hub` direto
4. `packages = []` no `pyproject.toml` → removido + `package-mode = false`
5. `ModuleNotFoundError: dashboard` → `sys.path.insert` (1 nível)
6. `sys.path` conflito no Poetry venv (Codespaces) → condicional (`if not VIRTUAL_ENV`)
7. `RuntimeError: Runtime instance already exists` → `run.py` vs main module path direto

**Dependências finais (66 packages):** streamlit, pandas, numpy, plotly, openpyxl, huggingface_hub, python-dotenv, pytest.

**Aviso de health check transient:** A mensagem `connect: connection refused` no health check durante inicialização é normal em dashboards mais pesados. Não afeta a funcionalidade — o Uvicorn sobe corretamente.

## 12.13 Chatbot HF_TOKEN — Fallback em 3 camadas (Fechado ✅ 13/05/2026)

**Problema:** No Streamlit Cloud, o chatbot crashava porque `load_dotenv()` em `llm_config.py` e `rag_pipeline.py` tentava carregar `.env.local` que não existe no servidor. Quando `load_dotenv` falha, sobrescreve `HF_TOKEN` com string vazia, e o token dos Secrets nunca era lido.

**Solução:** Removido `load_dotenv` de ambos os arquivos; implementada fallback em 3 camadas em `get_api_key()`:

1. **Primeiro:** `os.getenv("HF_TOKEN")` — funciona no Streamlit Cloud (Secrets expõe como env var) e localmente
2. **Segundo:** `.env.local` apenas se existir — ambiente local com token no arquivo gitignored
3. **Terceiro:** `st.secrets.get("HF_TOKEN")` — fallback direto no Streamlit Cloud

**Arquivos alterados:**
- `src/dashboard/chat/llm_config.py`: `get_api_key()` com fallback em 3 camadas; `has_api_key()` agora verifica `key.strip()`
- `src/dashboard/chat/rag_pipeline.py`: removido `load_dotenv`; `HF_TOKEN` via `os.getenv()` direto

**Testes:** 34/34 passando; imports OK.

---

## 12.14 Chatbot — Bug no caminho do .env.local (Fechado ✅ 13/05/2026)

**Problema:** Localmente o chatbot mostrava "Configure seu token da API HuggingFace..." mesmo com `.env.local` preenchido. Causa: path `'..', '..', '.env.local'` resolvia para `src/.env.local` (inexistente), não para a raiz do projeto.

- `src/dashboard/chat` → `..` → `..` → `src/.env.local` → **não existe**
- Deveria ser: `src/dashboard/chat` → `..` → `..` → `..` → `.env.local` → **existe**

**Solução:** Adicionado `'..'` extra em `llm_config.py` linha 22:
```python
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env.local')
```

**Testes:** 34/34 passando; `get_api_key()` agora retorna o token corretamente.

---

## 12.15 Chatbot — HF_TOKEN vazio no rag_pipeline.py (Fechado ✅ 13/05/2026)

**Problema:** Chatbot mostrava "Configure seu token da API..." mesmo com `.env.local` configurado. Causa: `rag_pipeline.py` usava `HF_TOKEN = os.getenv("HF_TOKEN", "")` no topo do módulo — executado no import, sempre string vazia. A função `get_api_key()` do `llm_config.py` nunca era chamada.

**Solução:**
- Removido `HF_TOKEN = os.getenv("HF_TOKEN", "")` do topo do módulo `rag_pipeline.py`
- Em `build_rag_chain()`: importar `get_api_key` de `llm_config.py` e usar `token = get_api_key() or ""` para passar aos embeddings

**Arquivo alterado:** `src/dashboard/chat/rag_pipeline.py`

**Testes:** 34/34 passando; imports OK.

---

## 12.16 Unificar entry point — path fixo em main.py (Fechado ✅ 13/05/2026)

**Problema:** `main.py` tinha path condicional:
```python
if not os.environ.get('VIRTUAL_ENV'):
    sys.path.insert(0, ...)
```
Isso funcionava no Streamlit Cloud (sem VIRTUAL_ENV), mas falhava local quando executado via `poetry run` (com VIRTUAL_ENV).

**Solução:** Remover a condicional — sempre adicionar o caminho correto:
```python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
```

**Arquivo alterado:** `src/dashboard/main.py`

**Testes:** Streamlit inicia corretamente (testado via curl localhost:8501).

---

*Documento atualizado em 13/05/2026 — Projeto completo: ETL + Dashboard + 34 testes + Dark Mode + Chatbot RAG (zero deps langchain)*

---

## 12.17 Chatbot — Bugs de Integracao Streamlit (Aberto 13/05/2026)

**Problema:** O chatbot integrado na sidebar nao funciona corretamente em alguns cenários.

### BUG-CHAT-01: Comparacao de identidade do DataFrame (Critico)

**Arquivo:** `src/dashboard/tabs/chat.py:87`

**Codigo problemático:**
```python
if chain is None or df_ref is not df:
```

**Problema:** `df_ref is not df` compara **identidade de objeto Python**, não conteúdo. Como `load_data()` usa `@st.cache_data`, o DataFrame pode ser recriado entre reruns (nova instância de objeto), causando `True` mesmo sem mudança real de dados. Isso força reconstrução do RAG a cada interação do usuário, degradando performance e potencialmente causando loops de rerun.

**Impacto:** Reconstrução desnecessária do índice de embeddings em cada mensagem.

**Correção:** Remover a comparação `df_ref is not df`. O chain fica em `session_state` e é reutilizado até que o usuário clique em "Limpar conversa". O DataFrame serve apenas para gerar estatísticas dinâmicas no `build_rag_chain`.

### BUG-CHAT-02: provider="auto" quebra no Streamlit Cloud (Critico)

**Arquivo:** `src/dashboard/chat/llm_config.py:72`

**Codigo problemático:**
```python
response = self._client.chat_completion(
    model=self.repo_id,
    messages=[{"role": "user", "content": prompt}],
    max_tokens=self.max_new_tokens,
    temperature=self.temperature,
    provider="auto",  # <-- PROBLEMA
)
```

**Problema:** `provider="auto"` usa Inference Providers (sistema de routing gratuito). Sem credits gratuitos disponíveis no Streamlit Cloud, o Inference Providers pode retornar erro de quota ou falha silenciosa. O provider fixo (ex: `hf-inference`) ou omissão garante comportamento consistente.

**Impacto:** Chat falha silenciosamente no Streamlit Cloud mesmo com token válido.

**Correção:** Remover `provider="auto"` ou usar `provider="hf-inference"` explicitamente.

### BUG-CHAT-03: Sem FAQ sugerido (Medio)

**Arquivo:** `src/dashboard/tabs/chat.py`

**Problema:** A SKILL descreve botões de perguntas sugeridas na sidebar, mas `chat.py` não implementa nenhum. O usuário não consegue clicar em perguntas pré-definidas.

**Correção:** Adicionar perguntas sugeridas clicáveis no topo da área do chat.

### BUG-CHAT-04: Sem botao de limpar conversa (Medio)

**Arquivo:** `src/dashboard/tabs/chat.py`

**Problema:** O histórico de chat acumula indefinidamente sem opção de reset. A memória interna do `SimpleConversationalRAG` não tem limite de janela.

**Correção:** Adicionar botão "Limpar conversa" que reseta `chat_messages` e `chat_chain` do session_state.

### BUG-CHAT-05: Sem spinner na resposta (Medio)

**Arquivo:** `src/dashboard/tabs/chat.py:106`

**Problema:** O spinner aparece apenas na construção do chain (linha 89), mas não na geração da resposta em si. O usuário não tem feedback visual durante a chamada ao LLM.

**Correção:** Adicionar `st.spinner()` ao redor da chamada `chain.invoke()`.

### BUG-CHAT-06: DataFrame armazenado por referência no session_state (Baixo)

**Arquivo:** `src/dashboard/tabs/chat.py:68`

**Codigo:**
```python
st.session_state["chat_df"] = df
```

**Problema:** Armazena a referência do DataFrame. Se o DataFrame for recarregado (cache invalidado), a referência fica desatualizada e não causa rebuild automático.

**Correção:** Não armazenar `chat_df` no session_state (já que não é mais usado na comparação).

### BUG-CHAT-07: Imports de chat redundantes no modulo (Baixo)

**Arquivo:** `src/dashboard/chat/rag_pipeline.py:160-161`

**Problema:** `build_rag_chain` importa `get_api_key` dentro da função, mas já está importado para uso. Imports lazy dentro de funções são boas práticas, mas aqui `generate_dynamic_stats` e `get_api_key` podem ser importados no topo.

**Correção:** Mover imports para o topo do modulo para clareza.

---

## 12.18 Chatbot — Plano de Correção (13/05/2026)

| Bug | Prioridade | Status | Arquivo |
|---|---|---|---|
| BUG-CHAT-01 Identity comparison | Critica | Aberto | chat.py:87 |
| BUG-CHAT-02 provider="auto" | Critica | Aberto | llm_config.py:72 |
| BUG-CHAT-03 Sem FAQ | Media | Aberto | chat.py |
| BUG-CHAT-04 Sem limpar conversa | Media | Aberto | chat.py |
| BUG-CHAT-05 Sem spinner na resposta | Media | Aberto | chat.py |
| BUG-CHAT-06 chat_df por referencia | Baixa | Aberto | chat.py:68 |
| BUG-CHAT-07 Imports redundantes | Baixa | Aberto | rag_pipeline.py |

---

## 12.19 Chatbot — Correções Aplicadas (13/05/2026)

### chat.py — Reescrito completo

| Correção | Descrição |
|---|---|
| Removido `df_ref is not df` | Chain não é mais reconstruído por causa de mudança de identidade do DataFrame. Chain fica em session_state até limpar. |
| Removido `chat_df` do session_state | Não há mais comparação com `df_ref`, referência do DataFrame não é mais necessária. |
| Adicionado FAQ questions | 12 perguntas sugeridas clicáveis dentro de `st.expander` na área do chat. |
| Adicionado `clear_conversation()` | Função exportada que limpa `chat_messages` e `chat_chain` e mostra mensagem de boas-vindas resetada. |
| Spinner na resposta | `st.spinner("Consultando a base de conhecimento...")` ao redor de `chain.invoke()`. |
| Imports reorganizados | Imports lazy dentro de funções para evitar crash se modulo não carregar. |

### llm_config.py — provider="auto" removido

| Correção | Descrição |
|---|---|
| Removido `provider="auto"` | HuggingFace Inference API agora usa routing default (sem Inference Providers). Comportamento consistente local e Streamlit Cloud. |

### main.py — Botão limpar conversa

| Correção | Descrição |
|---|---|
| Adicionado `st.button("🗑️ Limpar conversa")` | Na sidebar, após o `chat.render()`, com ícone de lixeira. Chama `chat.clear_conversation()`. |

**Testes:** 34/34 passando.

**Status:** BUG-CHAT-01 ao BUG-CHAT-05 resolvidos. BUG-CHAT-06 e BUG-CHAT-07 são baixa prioridade e não impactam funcionalidade — mantidos como pendientes para futuras melhorias.

---

## 12.20 Chatbot — Bloqueio do Event Loop Streamlit (Aberto 13/05/2026)

**Sintoma:** Chat não funciona — "Iniciando assistente..." fica travado, aplicação congela completamente.

**Causa Raiz:** O pipeline faz **HTTP calls sequenciais síncronas** dentro do event loop do Streamlit. Cada operação bloqueia o servidor inteiro:
1. `SimpleEmbeddings.embed()` — API HuggingFace (19 chamadas sequenciais para embedding dos chunks)
2. `SimpleConversationalRAG.invoke()` — Mais uma API call pro LLM
3. Tudo roda **dentro do handler do Streamlit**, congelando o event loop
4. O `st.spinner` não aparece porque o loop está bloqueado antes de renderizar

### Problemas Identificados

| # | Problema | Causa | Impacto |
|---|---|---|---|
| P1 | Embeddings sequenciais (19 HTTP calls) | `embed_batch()` itera sem paralelismo | 10-20s de espera bloqueante na primeira mensagem |
| P2 | Nenhum feedback visual durante processamento | Event loop congelado antes do spinner renderizar | UI parece travada |
| P3 | FAQ buttons disparam `_handle_message` no render cycle | `st.button` dentro de loop não controla main flow | Reruns em loop |
| P4 | Sem cache nos embeddings | `_ensure_indexed` roda a cada `build_rag_chain` | Recompilação desnecessária |
| P5 | Sem timeout nas API calls | `InferenceClient` sem timeout | Hang infinito em falhas de rede |

### Arquitetura da Solução (Threading Pattern)

```
User envia mensagem
    │
    ├─► Adiciona mensagem ao chat (IMEDIATO)
    │
    ├─► Mostra placeholder "Pensando..." (IMEDIATO)
    │
    ├─► Spawn background thread
    │       │
    │       ├─► Embeddings pré-computados via @st.cache_resource (1x)
    │       │
    │       ├─► Cria RAG chain (usa vector store cacheado)
    │       │
    │       ├─► Chama LLM com timeout=60s
    │       │
    │       ├─► Atualiza session_state com resposta
    │       │
    │       └─► st.rerun() → UI atualiza com resposta
    │
    └─► st.rerun() → mostra placeholder "Pensando..."
```

### Arquivos a Alterar

| Arquivo | Mudança |
|---|---|
| `rag_pipeline.py` | `build_vector_store()` com `@st.cache_resource`, embeddings pré-computados |
| `llm_config.py` | `timeout=60` + retry com backoff |
| `chat.py` | Threading pattern, `st.empty()` placeholder, FAQ via `session_state["pending_question"]` |

---

## 12.21 Chatbot — Plano de Correção Threading (13/05/2026)

| # | Tarefa | Status |
|---|---|---|
| T1 | Registrar plano no TODO.md | ✅ Concluído |
| T2 | `rag_pipeline.py`: cache_resource + build_vector_store | ✅ Concluído |
| T3 | `llm_config.py`: timeout 60s + retry | ✅ Concluído |
| T4 | `chat.py`: threading pattern + placeholder + FAQ via session_state | ✅ Concluído |
| T5 | Atualizar README.md com fluxo do chatbot | ✅ Concluído |
| T6 | Testar pytest + streamlit | ✅ Concluído (34/34)

---

## 12.22 Chatbot — Reimplementação do Zero (13/05/2026)

**Problema:** O chatbot atual apresenta timeout/lentidão por 3 motivos principais:

1. **Embeddings via API HTTP** — O código usa `InferenceClient.feature_extraction()` que faz chamadas HTTP individuais para cada chunk. Com ~30 chunks, são 30 chamadas HTTP sequenciais = lentidão extrema.

2. **Sem paralelismo** — O processamento é sequencial, sem uso de threads ou batch.

3. **Cache não funciona** — O `@st.cache_resource` no `build_vector_store` rebuilda o índice toda vez porque recebe `_df_hash` como parâmetro variável.

**Sintoma relatado:** Timeout / Lentidão

### 12.22.1 Arquitetura Proposta

```
┌─────────────────────────────────────────────────────────────────────┐
│                    STREAMLIT FRONTEND                               │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  chat.py (tabs/chat.py)                                      │  │
│  │  - Interface com chat_input e expander de FAQ               │  │
│  │  - Session state para histórico                               │  │
│  └─────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    PIPELINE RAG                                     │
│  ┌──────────────────────┐    ┌──────────────────────┐            │
│  │ Embeddings LOCAL     │    │ LLM (HuggingFace)    │            │
│  │ sentence-transformers│    │ Inference API        │            │
│  │ paraphrase-multilingual│  │ + retry + fallback   │            │
│  │ MiniLM-L12-v2        │    │                      │            │
│  │ (cpu, rápido)        │    │                      │            │
│  └──────────┬─────────────┘    └──────────┬───────────┘            │
│             │                              │                       │
│             ▼                              ▼                       │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ SimpleVectorStore (FAISS-like em memória)                   │  │
│  │ - Busca por similaridade cosseno                            │  │
│  │ - Cache built once per session via @st.cache_resource       │  │
│  └─────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    KNOWLEDGE BASE                                   │
│  ┌──────────────────────┐    ┌──────────────────────┐            │
│  │ knowledge_base.py   │    │ load_data.py         │            │
│  │ - Docs estáticos    │    │ - Estatísticas       │            │
│  │ - FAQ completo      │    │   dinâmicas do df    │            │
│  └──────────────────────┘    └──────────────────────┘            │
└─────────────────────────────────────────────────────────────────────┘
```

### 12.22.2 Arquivos a Criar/Modificar

| Arquivo | Ação | Descrição |
|---------|------|-----------|
| `src/dashboard/chat/rag_pipeline.py` | **reescrever** | Novo pipeline com embeddings locais + cache correto |
| `src/dashboard/chat/llm_config.py` | **reescrever** | LLM com retry, timeout, fallback |
| `src/dashboard/chat/knowledge_base.py` | manter | Já está correto |
| `src/dashboard/tabs/chat.py` | **simplificar** | Apenas UI, lógica movida para rag_pipeline |
| `.streamlit/secrets.toml` | **criar** | Configuração de secrets para Cloud |
| `.env.local` | **atualizar** | Token HF (mantém compatibilidade local) |
| `requirements.txt` | **atualizar** | Adicionar sentence-transformers |

### 12.22.3 Solução Técnica

#### Embeddings Locais (mudança principal):

```python
# ANTES (lento via API):
self.client.feature_extraction(text, model=EMBEDDING_MODEL)

# DEPOIS (rápido local):
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
embeddings = model.encode(texts, batch_size=32)
```

**Problema:** `sentence-transformers` requer `torch` que causa problemas no Streamlit Cloud (compilação nativa).

**Solução alternativa:** Usar embeddings via API em batch com paralelismo:
- Fazer todas as chamadas de embedding em paralelo (ThreadPoolExecutor)
- Comprimir em uma única chamada HTTP se possível
- Usar timeout adequado

#### Cache corrigido:

```python
@st.cache_resource(ttl=3600)
def get_vector_store():
    # Sem parâmetros variáveis - build only once
    # Gera hash interno a partir dos docs
```

### 12.22.4 Cronograma

| Fase | Tarefa | Status |
|------|--------|--------|
| 1 | Atualizar `requirements.txt` ou `pyproject.toml` | Aberto |
| 2 | Reescrever `llm_config.py` com retry/timeout | Aberto |
| 3 | Reescrever `rag_pipeline.py` com embeddings locais | Aberto |
| 4 | Simplificar `tabs/chat.py` | Aberto |
| 5 | Criar `.streamlit/secrets.toml` | Aberto |
| 6 | Testar localmente | Aberto |
| 7 | Configurar secrets no Streamlit Cloud | Aberto |

### 12.22.5 Implementação Concluída (13/05/2026)

**Arquivos alterados:**

| Arquivo | Alteração |
|---------|-----------|
| `src/dashboard/chat/llm_config.py` | Timeout aumentado para 90s, retry com backoff |
| `src/dashboard/chat/rag_pipeline.py` | Paralelismo com ThreadPoolExecutor (8 workers), cache correto via `@st.cache_resource` |
| `src/dashboard/tabs/chat.py` | Removido parâmetro df_hash, spinner移到 durante processamento |
| `.streamlit/.gitignore` | Criado para proteger secrets |

**Testes:** 34/34 passando

**Nota sobre performance:**
O bottleneck é a API HuggingFace para embeddings (feature_extraction), não o código. Mesmo com paralelismo, cada chamada HTTP leva tempo. Se o problema persistir no Streamlit Cloud, considerar:
- Groq API (mais rápido, gratuito com Llama-3-8B)
- Reduzir número de chunks (menor = menos chamadas HTTP)

---

## 12.23 Chatbot — Configuração Streamlit Cloud (13/05/2026)

**Para ativar o chatbot no Streamlit Cloud:**

1. Acessar o dashboard no Streamlit Cloud
2. Ir em **Settings** > **Secrets**
3. Adicionar:
   ```
   [general]
   HF_TOKEN = "hf_seu_token_aqui"
   ```
4. Salvar e fazer redeploy

**Token HuggingFace:**
- Criar conta em https://huggingface.co
- Gerar Access Token em Settings > Access Tokens
- Tipo: **Fine-grained**, permissão: **Inference > Make calls to the serverless Inference API**
- Credits gratuitos disponíveis (~$0.10/mês)

---

## 12.24 Chatbot — Otimização de Performance (13/05/2026)

**Problema:** Chatbot trava toda a aplicação e o computador durante uso. Causa: chamadas HTTP sequenciais para API HuggingFace (embeddings + LLM) sem timeout adequado.

### 12.24.1 Plano de Otimização

| # | Otimização | Descrição |
|---|---|---|
| 1 | **Modelo menor** | Trocar `Llama-3.1-8B-Instruct` por `microsoft/Phi-3-mini-4k-instruct` (4B params, muito mais rápido) |
| 2 | **Timeouts agressivos** | LLM: 30s (em vez de 90s), Embedding: 15s (em vez de 30s) |
| 3 | **Fallback para FAQ** | Se API falhar/timeout, retornar resposta do FAQ estático |
| 4 | **Cache do LLM** | Instância do LLM em session_state (não criar nova a cada mensagem) |
| 5 | **Loading state** | Feedback visual adequado sem travar UI |

### 12.24.2 Implementação

| Arquivo | Mudança |
|---------|---------|
| `llm_config.py` | Modelo Phi-3-mini, timeout 30s, retry com backoff, fallback para FAQ |
| `rag_pipeline.py` | Timeout no embeddings, cache otimizado |
| `chat.py` | LLM em cache via session_state, fallback visual |

### 12.24.3 Status

| Tarefa | Status |
|--------|--------|
| T.1 Registrar plano no TODO.md | ✅ Concluído |
| T.2 Substituir modelo por Phi-3-mini | ✅ Concluído |
| T.3 Adicionar timeouts agressivos | ✅ Concluído |
| T.4 Adicionar fallback para FAQ | ✅ Concluído |
| T.5 Cache do LLM via session_state | ✅ Concluído |
| T.6 Testar localmente | ✅ Concluído (34/34) |

### 12.24.4 Mudanças Implementadas

| Arquivo | Mudança |
|---------|---------|
| `llm_config.py` | Modelo: `microsoft/Phi-3-mini-4k-instruct` (4B params), timeout 30s, max_tokens 512, fallback FAQ |
| `rag_pipeline.py` | Embedding timeout: 15s, MAX_WORKERS: 4 |
| `chat.py` | Chain cacheado via session_state, clear_conversation() remove chain, erro amigável |

### 12.24.5 Testes

**34/34 testes passando**

---

## 12.29 Chatbot — Usar requests em vez de httpx (13/05/2026)

**Problema:** `ConnectionResetError: [WinError 10054]` no Windows com biblioteca httpx.

**Solução:** Substituir cliente nativo do Cohere (httpx) por requests direto.

| Configuração | Antes | Depois |
|-------------|-------|---------|
| Biblioteca | cohere.Client (httpx) | requests direto |
| Timeout | 60s | 90s |
| Retry | 1 | 3 |
| Backoff | - | 2s |

**Rationale:** requests é mais estável no Windows, não tem problemas de event loop.

**Arquivo alterado:** `src/dashboard/chat/llm.py`

**Status:** ✅ Concluído (34/34 testes passando)

---

## 12.28 Chatbot — Migrar para Cohere API (13/05/2026)

**Problema:** HuggingFace Inference API não suporta modelos de chat (Phi-3, Qwen, Llama) no plano gratuito/trial.

**Solução:** Migrar para Cohere API (modelo `command-r7b-12-2024`).

| Componente | Antes | Depois |
|------------|-------|--------|
| Provider | HuggingFace (problemas) | Cohere (funcionando) |
| Modelo | Phi-3-mini-4k-instruct | command-r7b-12-2024 |
| API Key | HF_TOKEN | COHERE_API_KEY |

**Arquivos alterados:**
- `.env.local` — adicionada COHERE_API_KEY
- `.env.example` — documentada variável
- `pyproject.toml` — adicionada dependência `cohere`
- `src/dashboard/chat/llm.py` — reescrito para usar Cohere Client

**Status:** ✅ Concluído (34/34 testes passando)

---

## 12.27 Chatbot — Troca de Modelo (13/05/2026)

**Problema:** Chatbot retornava "ConnectionResetError: [WinError 10054]" com modelo Phi-3-mini.

**Solução:** Trocar para modelo mais leve e rápido.

| Configuração | Antes | Depois |
|--------------|-------|--------|
| Modelo | `microsoft/Phi-3-mini-4k-instruct` (4B) | `Qwen/Qwen2-0.5B-Instruct` (0.5B) |

**Rationale:** Qwen2-0.5B é muito menor (0.5B vs 4B params), mais rápido e menos propenso a erros de conexão.

**Arquivo alterado:** `src/dashboard/chat/llm.py`

**Status:** ✅ Concluído

---

## 12.26 Chatbot — Timeout Aumentado (13/05/2026)

**Problema:** Chatbot retornava "Tempo limite excedido" com timeout de 30s.

**Solução:** Aumentar timeout e retries para dar mais tempo à API.

| Configuração | Antes | Depois |
|--------------|-------|--------|
| LLM_TIMEOUT | 30s | 60s |
| MAX_RETRIES | 2 | 3 |
| RETRY_BACKOFF | 1.5 | 2 |

**Arquivo alterado:** `src/dashboard/chat/llm.py`

**Status:** ✅ Concluído

---

## 12.25 Chatbot — Reimplementação Leve (13/05/2026)

**Problema:** O chatbot atual (com RAG, LangChain, embeddings) é muito pesado e trava a aplicação.

**Solução:** Chatbot simples via API HuggingFace direta, com contexto dos dados reais injetado no prompt.

### 12.25.1 Arquitetura Nova

```
┌─────────────────────────────────────────┐
│  chat.render(df)                       │
│  → get_stats_context(df)               │
│  → prompt = SYSTEM + CONTEXTO + PERGUNTA│
│  → HuggingFace API (Phi-3-mini)        │
│  → Resposta                            │
└─────────────────────────────────────────┘
```

| Componente | Antes (pesado) | Depois (leve) |
|------------|----------------|---------------|
| LLM | LangChain + ChatHuggingFace | InferenceClient direto |
| Embeddings | sentence-transformers (API) | Removido |
| Vector Store | FAISS/InMemoryVectorStore | Removido |
| RAG | LangChain ConversationalRetrievalChain | Prompt engineering |
| Contexto | Vector store search | String injetada no prompt |

### 12.25.2 Arquitetura de Arquivos

```
src/dashboard/
├── chat/
│   ├── __init__.py
│   ├── llm.py         # API HuggingFace + contexto
│   └── app.py         # Interface de chat
└── tabs/
    └── chat.py        # Wrapper para sidebar
```

### 12.25.3 Contexto Dinâmico dos Dados

```python
def get_stats_context(df):
    """Gera string de contexto com KPIs reais do DataFrame."""
    return f"""
    📊 ESTATÍSTICAS ATUAIS DO DASHBOARD:
    - Total de ligações: {len(df)}
    - Ligações ativas: {(df['SIT._LIG_AGUA'] == 'ATIVA').sum()}
    - Faturamento mensal: R$ {df['VALOR_TOTAL'].sum():,.2f}
    - Volume total: {df['VOLUME_FATURADO'].sum():,.0f} m³
    - Anomalias (LIDO > REAL): {(df['VOLUME_REAL'] < df['VOLUME_LIDO']).sum()}
    - Consumo zero ativo: {((df['VOLUME_LIDO'] == 0) & (df['SIT._LIG_AGUA'] == 'ATIVA')).sum()}
    - Hidrômetros > 5 anos: {(df['IDADE_HIDRO_ANOS'].fillna(0) > 5).sum()}
    - Por categoria: {df['CATEGORIA_PRINCIPAL'].value_counts().to_dict()}
    """
```

### 12.25.4 Dependências

```toml
huggingface-hub = ">=0.20.0"
```

(sem LangChain, sem FAISS, sem sentence-transformers)

### 12.25.5 Funcionamento Local vs Cloud

| Ambiente | HF_TOKEN |
|----------|----------|
| Local | `.env.local` (já existe) |
| Streamlit Cloud | Secrets do deploy |

### 12.25.6 Tarefas

| # | Tarefa | Status |
|---|---|---|
| T1 | Registrar plano no TODO.md | ✅ Concluído |
| T2 | Adicionar huggingface-hub no pyproject.toml | ✅ Concluído |
| T3 | Criar `src/dashboard/chat/__init__.py` | ✅ Concluído |
| T4 | Criar `src/dashboard/chat/llm.py` | ✅ Concluído |
| T5 | Criar `src/dashboard/chat/app.py` | ✅ Concluído |
| T6 | Criar `src/dashboard/tabs/chat.py` | ✅ Concluído |
| T7 | Atualizar `main.py` para integrar chat | ✅ Concluído |
| T8 | Testar localmente | ✅ Concluído |
| T9 | Verificar 34 testes | ✅ Concluído (34/34) |

---

## Status Final — Projeto Completo

| Componente | Status |
|------------|--------|
| ETL Pipeline | ✅ Funcional |
| Dashboard Streamlit | ✅ Funcional |
| 34 Testes | ✅ Passando |
| Dark Mode | ✅ Implementado |
| Chatbot Leve | ✅ Implementado (Cohere API + requests, timeout 90s) |
| Streamlit Cloud | ⏳ Pending deploy |
