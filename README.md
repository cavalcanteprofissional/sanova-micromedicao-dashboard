# Analise Comercial de Micromedicao

**Dashboard interativo para analise strategica de micromedicao de saneamento.**

> :zap: Teste pratico para Analista de Dados | **SANOVA** - Inovacao em Saneamento

---

## O que esse projeto faz?

Analisa **1.912 ligacoes** de agua ao longo de **13 meses** e responde:

| # | Pergunta estrategica | Onde? |
|---|---|---|
| 1 | Quais ligacoes geram e quais perdem receita? | Visao Geral |
| 2 | Onde ha sinais de fraude ou adulteracao? | Anomalias & Fraudes |
| 3 | Quantas ligacoes tem consumo zero e quanto custa? | Consumo Zero |
| 4 | Quais hidrometros estao velhos demais? | Hidrometros |
| 5 | Quanto a concessionaria pode recuperar? | Recuperacao de Receita |
| 6 | Os dados sao confiaveis para decisoes? | Qualidade de Dados |

**Receita potencial identificada: R$ 2,49 milhoes**

---

## Quickstart

```bash
# 1. Instalar dependencias
poetry install

# 2. Abrir dashboard (dados ja tratados)
python run.py

# Abrir em http://localhost:8501
```

> O pipeline ETL ja foi executado. So rode `python src/etl/run_pipeline.py` se quiser reprocessar os dados a partir do Excel.

---

## As 6 abas do dashboard

Todas conectadas aos filtros globais da sidebar.

### 1. :chart_with_upwards_trend: Visao Geral

KPIs executivos atualizados em tempo real: ligacoes ativas, faturamento, volume, casos criticos e o Indice de Qualidade de Dados (IQD). Grafico de area com a evolucao do faturamento ao longo dos 13 meses e heatmaps com o consumo medio por categoria. Grafico de barras horizontais com cores semanticas: verde para ligacoes ativas, vermelho para cortadas, laranja para nao informadas.

---

### 2. :mag_right: Anomalias & Fraudes

Deteccao de anomalias que podem indicar fraude ou falhas de medicao. Cruza tres fontes de evidencia: divergencia entre volume lido e real (LIDO > REAL sugere adulteracao), ausencia de hidrometro em ligacoes ativas, e outliers estatisticos. Scatter plot interativo com opcao de filtrar outliers, barras com a contagem por tipo de anomalia, e tabela de casos priorizados ordenada por score.

---

### 3. :droplet: Consumo Zero

Analise de ligacoes com consumo zero ao longo dos meses. Contabiliza a receita perdida pela tarifa minima aplicada a cada mes sem medicao. Histograma com a distribuicao de meses sem consumo, grafico de barras por categoria, e lista de casos criticos (3+ meses) com receita perdida estimada por ligacao.

---

### 4. :wrench: Hidrometros

Inventario completo dos equipamentos de medicao: distribuicao por tipo, marca (MARCA A-F), classe metrologica e idade. Hidrometros com mais de 5 anos sao marcados como candidatos a substituicao. Tabela paginada lista todos os candidatos com receita potencial de submediacao estimada em 15% ao ano (referencia ABNT NBR 15538).

---

### 5. :money_with_wings: Recuperacao de Receita

Painel estrategico com 4 eixos de acao e o potencial de receita associado:

| Acao | Ligacoes | Receita (12m) |
|---|---|---|
| Substituir hidrometros > 5 anos | 414 | R$ 1,87M |
| Vistoriar ligacoes 6+ meses sem consumo | 224 | R$ 119,6K |
| Fiscalizar divergencia LIDO > REAL | 144 | R$ 144K |
| Instalar hidrometro em ligacao ativa | 1 | R$ 1K |

Waterfall chart com o impacto acumulado, gauge com o potencial vs faturamento atual, e tabela de acoes priorizadas colorizada: Alta (vermelho), Media (laranja), Baixa (verde).

---

### 6. :clipboard: Qualidade de Dados

Monitora a integridade do dataset. IQD com indicador visual, heatmaps de missing ao longo dos 13 meses por coluna, tabela de inconsistencias classificada por impacto, e ranking das 10 colunas com maior missing para priorizacao de correcao cadastral.

---

## Como funciona

```
micromedicao.xlsx (1.912 x 132)
    |
    v
[ Pipeline ETL - 10 passos ]
    | Normalizacao de texto
    | Correcao de decimais e datas
    | Tratamento de missing
    | Enriquecimento (14 colunas calculadas)
    v
micromedicao_tratado.csv (1.912 x 151)
    |
    v
[ Dashboard Streamlit ]
    | @st.cache_data (leitura + cache)
    | Sidebar com filtros globais
    v
[ 6 abas interativas com Plotly ]
```

---

## Stack

| | |
|---|---|
| **Python** | Linguagem base |
| **Streamlit** | Dashboard interativo |
| **Pandas** | Processamento de dados |
| **Plotly** | Graficos interativos |
| **Poetry** | Gestao de dependencias |
| **Pytest** | 34 testes automatizados |

---

## Premissas tecnicas

| Premissa | Valor |
|---|---|
| Tarifa minima | R$ 89,03 |
| Custo unitario da agua | R$ 10/m³ |
| Fator de submedição (> 5 anos) | 15% (ABNT NBR 15538) |
| Anomalia de leitura | LIDO > REAL + 1 m³ |
| Outlier extremo | Volume > percentil 99 |

---

## Estrutura do projeto

```
dashboard-sanova/
├── run.py                  # python run.py
├── pyproject.toml          # Poetry
├── src/
│   ├── dashboard/           # Aplicacao Streamlit
│   │   ├── main.py         # 6 abas + sidebar
│   │   ├── load_data.py    # Leitura CSV com cache
│   │   ├── config.py       # Premissas e cores
│   │   └── tabs/           # overview | anomalies | ...
│   └── etl/                 # Pipeline de dados
│       ├── extractor.py     # Leitura Excel
│       ├── transformer.py   # Limpeza + enriquecimento
│       └── loader.py       # Exportacao + validacao
├── data/
│   ├── raw/                # micromedicao.xlsx
│   ├── processed/           # micromedicao_tratado.csv
│   └── stage/              # validation_log.json
└── tests/                  # 34 testes pytest
```

---

## Competencias demonstradas

- **Engenharia de dados**: pipeline ETL com tratamento de missing, normalizacao de formato, enriquecimento de 14 colunas
- **Analise exploratoria**: diagnostico de problemas de qualidade, outliers e inconsistencias
- **Visualizacao**: KPIs, graficos de series temporais, heatmaps, waterfall charts e gauges
- **Python**: modularizacao com imports absolutos, cache com `@st.cache_data`, testes automatizados
- **Dominio de saneamento**: matricula, volume lido/real/faturado, classes metrologicas, tarifa minima

---

> Desenvolvido como teste pratico para Analista de Dados | **SANOVA** (sanova.com.br) | Palhoca/SC | 2026
