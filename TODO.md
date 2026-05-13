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

*Documento atualizado em 12/05/2026 — Projeto completo: ETL + Dashboard + 34 testes + Dark Mode + Chatbot RAG*
