---
name: micromedição-dashboard-streamlit
description: >
  Use esta skill para construir um dashboard completo em Streamlit para análise técnica e
  estratégica de sistemas comerciais de saneamento, com foco em micromedição, detecção de
  anomalias, fraudes e recuperação de receita. Acione sempre que o usuário mencionar:
  dashboard de micromedição, análise comercial de saneamento, estudo de perdas comerciais,
  detecção de fraudes em consumo de água, análise de hidrômetros, recuperação de receita em
  saneamento, ou qualquer variação de análise de sistema comercial com dados de volume e
  faturamento. Inclui estrutura de abas, KPIs executivos, visualizações interativas com
  Plotly, filtros dinâmicos e tabelas de priorização de ações.
---

# SKILL: Dashboard Streamlit — Estudo de Micromedição / Sistema Comercial de Saneamento

## 1. CONTEXTO DO DOMÍNIO

Este dashboard analisa dados comerciais de uma concessionária de saneamento. O objetivo é
identificar oportunidades de **recuperação de receita** e **perdas comerciais** com base em
12 meses de histórico de consumo e faturamento.

### Glossário técnico obrigatório
| Termo | Definição |
|---|---|
| **Matrícula** | Identificador único de cada ligação (cliente) |
| **VOLUME_LIDO** | Volume medido pelo hidrômetro (m³) |
| **VOLUME_REAL** | Volume aceito pelo sistema após validação (m³) |
| **VOLUME_FATURADO** | Volume efetivamente cobrado (pode ser mínimo tarifário) |
| **VALOR_TOTAL** | Valor total faturado (água + esgoto + serviços + impostos − descontos) |
| **SIT._LIG_AGUA** | Situação da ligação: Ativa, Cancelada, Cortada Ramal, Cortada Cavalete, Suprimida, Cortada na Fita, Eliminada |
| **CATEGORIA_PRINCIPAL** | Residencial, Comercial, Industrial, Pública |
| **CLASSE_METROLOGICA** | Classe A (básica), Classe B (padrão), Classe C (alta precisão) |
| **Mínimo tarifário** | Consumo mínimo cobrado mesmo quando o lido for inferior (tipicamente 10 m³) |

---

## 2. ESTRUTURA DE DADOS DO ARQUIVO

**Arquivo:** `Dados_-_Estudo_Micromedição.xlsx` — 1 aba (`Planilha1`), **1.912 linhas × 132 colunas**

### 2.1 Colunas cadastrais (fixas)
```
MATRICULA, SIT._LIG_AGUA, SIT._LIG_ESGOTO, NUMERO_HIDROMETRO,
TIPO_HIDROMETRO, MARCA_HIDROMETRO, CAPACIDADE_HIDROMETRO,
DIAMETRO_HIDROMETRO, CLASSE_METROLOGICA, DATA_INSTALACAO_HIDROMETRO,
CATEGORIA_PRINCIPAL, NUMERO_ECONOMIAS_RES, NUMERO_ECONOMIAS_COM,
NUMERO_ECONOMIAS_IND, NUMERO_ECONOMIAS_PUB
```

### 2.2 Padrão das colunas mensais (12 meses: sufixo _01 a _12; mês atual sem sufixo)
```
VOLUME_LIDO[_XX], VOLUME_REAL[_XX], VOLUME_FATURADO[_XX],
VALOR_AGUA[_XX], VALOR_ESGOTO[_XX], VALOR_SERVICOS[_XX],
VALOR_IMPOSTOS[_XX], VALOR_DESCONTOS[_XX], VALOR_TOTAL[_XX]
```
> **Nota:** Mês mais recente = colunas sem sufixo. `_01` = mês anterior, `_12` = mês mais antigo.

---

## 3. PRÉ-PROCESSAMENTO OBRIGATÓRIO

```python
import pandas as pd
import numpy as np
import streamlit as st

@st.cache_data
def load_data(filepath: str) -> pd.DataFrame:
    df = pd.read_excel(filepath)
    
    # Padronizar situação
    df['SIT._LIG_AGUA'] = df['SIT._LIG_AGUA'].fillna('Não Informada')
    df['CATEGORIA_PRINCIPAL'] = df['CATEGORIA_PRINCIPAL'].fillna('Não Informada')
    
    # Data de instalação
    df['DATA_INSTALACAO_HIDROMETRO'] = pd.to_datetime(
        df['DATA_INSTALACAO_HIDROMETRO'], dayfirst=True, errors='coerce'
    )
    df['IDADE_HIDRO_ANOS'] = (
        pd.Timestamp.today() - df['DATA_INSTALACAO_HIDROMETRO']
    ).dt.days / 365.25
    
    # Colunas de volume por mês em formato longo (para séries temporais)
    # Construir lista de meses: mês atual sem sufixo, depois _01 a _12
    meses = [''] + [f'_{i:02d}' for i in range(1, 13)]
    
    # Acumular receita e volume totais (12 meses)
    df['RECEITA_TOTAL_12M'] = sum(
        df[f'VALOR_TOTAL{s}'].fillna(0) for s in meses
    )
    df['VOLUME_TOTAL_12M'] = sum(
        df[f'VOLUME_FATURADO{s}'].fillna(0) for s in meses
    )
    
    # Flag: ligação ativa sem hidrômetro
    df['SEM_HIDROMETRO'] = (
        df['NUMERO_HIDROMETRO'].isnull() & (df['SIT._LIG_AGUA'] == 'Ativa')
    )
    
    # Flag: consumo zero no mês atual (ligação ativa)
    df['CONSUMO_ZERO_ATIVO'] = (
        (df['VOLUME_LIDO'].fillna(0) == 0) & (df['SIT._LIG_AGUA'] == 'Ativa')
    )
    
    # Flag: divergência lido vs real (possível fraude/adulteração)
    df['DIVERGENCIA_VOL'] = df['VOLUME_REAL'].fillna(0) - df['VOLUME_LIDO'].fillna(0)
    df['ANOMALIA_LEITURA'] = df['DIVERGENCIA_VOL'] < -1  # lido > real
    
    # Contagem de meses com consumo zero nos últimos 12 meses
    vol_lido_cols = ['VOLUME_LIDO'] + [f'VOLUME_LIDO_{i:02d}' for i in range(1, 13)]
    df['MESES_CONSUMO_ZERO'] = (df[vol_lido_cols].fillna(0) == 0).sum(axis=1)
    
    # Score de prioridade (quanto maior, mais urgente a ação)
    df['SCORE_PRIORIDADE'] = (
        df['ANOMALIA_LEITURA'].astype(int) * 50 +
        df['CONSUMO_ZERO_ATIVO'].astype(int) * 30 +
        (df['MESES_CONSUMO_ZERO'] >= 3).astype(int) * 20 +
        (df['IDADE_HIDRO_ANOS'].fillna(0) > 5).astype(int) * 10 +
        df['SEM_HIDROMETRO'].astype(int) * 40
    )
    
    return df
```

---

## 4. ESTRUTURA DO DASHBOARD (ABAS)

```python
st.set_page_config(page_title="Micromedição — Análise Comercial", layout="wide", page_icon="💧")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Visão Geral",
    "🚨 Anomalias & Fraudes",
    "📉 Consumo Zero",
    "🔧 Hidrômetros",
    "💰 Recuperação de Receita"
])
```

---

## 5. ABA 1 — VISÃO GERAL (KPIs Executivos)

### KPIs principais (usar `st.metric`)
```python
col1, col2, col3, col4 = st.columns(4)

with col1:
    ativas = (df['SIT._LIG_AGUA'] == 'Ativa').sum()
    st.metric("Ligações Ativas", f"{ativas:,}")

with col2:
    receita = df[df['SIT._LIG_AGUA'] == 'Ativa']['VALOR_TOTAL'].sum()
    st.metric("Faturamento Mês Atual", f"R$ {receita:,.2f}")

with col3:
    vol_total = df[df['SIT._LIG_AGUA'] == 'Ativa']['VOLUME_FATURADO'].sum()
    st.metric("Volume Faturado (m³)", f"{vol_total:,.0f}")

with col4:
    anomalias = df['ANOMALIA_LEITURA'].sum() + df['CONSUMO_ZERO_ATIVO'].sum()
    st.metric("Casos Críticos Detectados", f"{anomalias}", delta="⚠️ Requer Ação")
```

### Gráficos da Visão Geral
- **Distribuição por categoria** (pizza — Residencial / Comercial / Industrial / Pública)
- **Distribuição por situação da ligação** (barras horizontais)
- **Evolução do faturamento total nos 12 meses** (linha — soma de `VALOR_TOTAL[_XX]`)
- **Mapa de calor de consumo médio por categoria × mês** (heatmap Plotly)

---

## 6. ABA 2 — ANOMALIAS & FRAUDES

### Critérios de detecção a implementar

| Tipo de Anomalia | Critério | Variável de Flag |
|---|---|---|
| Leitura fraudada | `VOLUME_LIDO > VOLUME_REAL` em mais de 1 m³ | `ANOMALIA_LEITURA` |
| Ligação ativa sem hidrômetro | `SIT._LIG_AGUA == 'Ativa'` e `NUMERO_HIDROMETRO` nulo | `SEM_HIDROMETRO` |
| Consumo implausível | `VOLUME_LIDO` no mês atual > média_12m + 3×desvio_12m | Calcular inline |
| Consumo constante exato | Mesmos valores nos últimos 6 meses | Calcular inline |

```python
# Detecção de consumo constante suspeito (indica estimativa em vez de leitura real)
vol_cols_6m = [f'VOLUME_LIDO_{i:02d}' for i in range(1, 7)]
df['CONSUMO_CONSTANTE'] = (
    df[vol_cols_6m].nunique(axis=1) == 1
) & (df['VOLUME_LIDO_01'].notna())

# Consumo implausível (outlier estatístico)
vol_cols_12m = ['VOLUME_LIDO'] + [f'VOLUME_LIDO_{i:02d}' for i in range(1, 13)]
df['MEDIA_VOL_12M'] = df[vol_cols_12m].mean(axis=1)
df['STD_VOL_12M'] = df[vol_cols_12m].std(axis=1)
df['CONSUMO_IMPLAUSIVELMENTE_ALTO'] = (
    df['VOLUME_LIDO'] > df['MEDIA_VOL_12M'] + 3 * df['STD_VOL_12M']
) & (df['STD_VOL_12M'] > 0)
```

### Visualizações desta aba
- **Tabela interativa** com todos os casos anômalo, ordenados por `SCORE_PRIORIDADE` (usar `st.dataframe` com destaque de cor via `st.data_editor` ou `AgGrid`)
- **Scatter plot**: VOLUME_LIDO × VOLUME_REAL colorido por categoria (outliers destacados)
- **Bar chart**: contagem de anomalias por tipo

---

## 7. ABA 3 — CONSUMO ZERO

```python
# Ligações ativas com histórico de consumo zero
zero_df = df[df['SIT._LIG_AGUA'] == 'Ativa'].copy()
zero_df['MESES_ZERO'] = zero_df[vol_lido_cols].fillna(0).eq(0).sum(axis=1)
```

### Visualizações
- **Distribuição de meses com consumo zero** (histograma: 0 a 13 meses)
- **Tabela de ligações com ≥ 3 meses consecutivos de zero** (prioridade alta)
- **Breakdown por categoria** (quem tem mais zeros: residencial vs comercial)
- **Estimativa de receita perdida** = `n_meses_zero × tarifa_mínima` (R$ por ligação)

### Cálculo do potencial de recuperação
```python
TARIFA_MINIMA = 89.03  # R$ — premissa baseada nos dados (consumo mínimo ~10m³)

zero_df['RECEITA_POTENCIAL_PERDIDA'] = (
    zero_df['MESES_CONSUMO_ZERO'] * TARIFA_MINIMA
)
```

---

## 8. ABA 4 — HIDRÔMETROS

### Análises a apresentar
- **Distribuição por tipo** (Unijato / Multijato / Ultrassônico)
- **Distribuição por marca** (A, B, C, D, E, F — anonimizadas)
- **Distribuição por classe metrológica** (A, B, C)
- **Distribuição por diâmetro** (3/4", 1", 1½", 2")
- **Distribuição de idade** (histograma em anos)
- **Tabela de hidrômetros com > 5 anos** (candidatos a substituição)

```python
# Hidrômetros candidatos à substituição
substituicao = df[df['IDADE_HIDRO_ANOS'] > 5].copy()
substituicao = substituicao.sort_values('IDADE_HIDRO_ANOS', ascending=False)

# Impacto estimado: hidrômetros velhos submedem — premissa de 15% de submedição
FATOR_SUBMED = 0.15
substituicao['RECEITA_POTENCIAL_SUBMED'] = (
    substituicao['VALOR_TOTAL'].fillna(0) * FATOR_SUBMED * 12
)
```

---

## 9. ABA 5 — RECUPERAÇÃO DE RECEITA

### Painel de priorização (tabela principal desta aba)
Consolidar todos os casos com oportunidade de recuperação:

```python
acoes = []

# Ação 1: Ligações ativas sem hidrômetro
sem_hidro_ativas = df[df['SEM_HIDROMETRO']]
acoes.append({
    'Ação': 'Instalar hidrômetro em ligações ativas',
    'Qtd Ligações': len(sem_hidro_ativas),
    'Receita Potencial (12m)': len(sem_hidro_ativas) * TARIFA_MINIMA * 12,
    'Prioridade': 'Alta'
})

# Ação 2: Recuperar ligações com anomalia de leitura
anomalias = df[df['ANOMALIA_LEITURA']]
receita_anomalia = anomalias['DIVERGENCIA_VOL'].abs().sum() * 10  # premissa R$/m³
acoes.append({
    'Ação': 'Fiscalizar ligações com divergência lido × real',
    'Qtd Ligações': len(anomalias),
    'Receita Potencial (12m)': receita_anomalia * 12,
    'Prioridade': 'Alta'
})

# Ação 3: Reativar ligações com consumo zero crônico
zero_cronico = df[df['MESES_CONSUMO_ZERO'] >= 6]
acoes.append({
    'Ação': 'Vistoriar/reativar ligações c/ 6+ meses sem consumo',
    'Qtd Ligações': len(zero_cronico),
    'Receita Potencial (12m)': len(zero_cronico) * TARIFA_MINIMA * 6,
    'Prioridade': 'Média'
})

# Ação 4: Substituir hidrômetros velhos
acoes.append({
    'Ação': 'Substituir hidrômetros com > 5 anos (submedição)',
    'Qtd Ligações': len(substituicao),
    'Receita Potencial (12m)': substituicao['RECEITA_POTENCIAL_SUBMED'].sum(),
    'Prioridade': 'Média'
})

acoes_df = pd.DataFrame(acoes).sort_values('Receita Potencial (12m)', ascending=False)
```

### Visualizações
- **Tabela de ações priorizadas** com receita potencial e ROI estimado
- **Waterfall chart** de recuperação potencial por tipo de ação
- **Gauge de receita potencial total** vs faturamento atual

---

## 10. FILTROS GLOBAIS NA SIDEBAR

```python
st.sidebar.header("🔍 Filtros")

categorias = st.sidebar.multiselect(
    "Categoria",
    options=df['CATEGORIA_PRINCIPAL'].unique(),
    default=df['CATEGORIA_PRINCIPAL'].unique()
)

situacoes = st.sidebar.multiselect(
    "Situação da Ligação",
    options=df['SIT._LIG_AGUA'].unique(),
    default=['Ativa']
)

marcas = st.sidebar.multiselect(
    "Marca do Hidrômetro",
    options=df['MARCA_HIDROMETRO'].dropna().unique(),
    default=df['MARCA_HIDROMETRO'].dropna().unique()
)

# Aplicar filtros
df_filtered = df[
    df['CATEGORIA_PRINCIPAL'].isin(categorias) &
    df['SIT._LIG_AGUA'].isin(situacoes) &
    (df['MARCA_HIDROMETRO'].isin(marcas) | df['MARCA_HIDROMETRO'].isnull())
]
```

---

## 11. PALETA DE CORES E ESTILO

```python
# Cores padronizadas para status
COR_CRITICO = '#E74C3C'   # Vermelho — anomalia/fraude
COR_ALERTA  = '#F39C12'   # Laranja — atenção
COR_OK      = '#27AE60'   # Verde — normal
COR_INFO    = '#2980B9'   # Azul — informativo
COR_NEUTRO  = '#95A5A6'   # Cinza — inativo/cancelado

# Configurar tema Plotly
import plotly.express as px
import plotly.graph_objects as go

PLOTLY_TEMPLATE = 'plotly_white'
COLOR_SEQUENCE = [COR_INFO, COR_OK, COR_ALERTA, COR_CRITICO, COR_NEUTRO]
```

---

## 12. PREMISSAS TÉCNICAS DOCUMENTADAS

Incluir sempre este bloco como `st.expander("📋 Premissas e Metodologia")`:

```python
with st.expander("📋 Premissas e Metodologia"):
    st.markdown("""
    **Premissas adotadas:**
    - **Tarifa mínima:** R$ 89,03 (baseada no menor VALOR_TOTAL observado nos dados para consumo de 10 m³)
    - **Custo unitário da água:** ~R$ 10/m³ (estimativa para cálculo de receita perdida por divergência)
    - **Fator de submedição em hidrômetros > 5 anos:** 15% (referência ABNT NBR 15538 e literatura técnica)
    - **Consumo crônico zero:** ≥ 6 meses consecutivos ou alternados sem medição
    - **Anomalia de leitura:** VOLUME_LIDO > VOLUME_REAL em mais de 1 m³ no mês de referência
    - **Consumo implausível:** volume > média_12m + 3×desvio_padrão_12m
    - **Período de referência:** 13 meses (mês atual + 12 meses históricos)
    
    **Limitações dos dados:**
    - Marcas de hidrômetro anonimizadas (MARCA A–F): não é possível correlação com padrões de desgaste por fabricante
    - Endereços não disponíveis: análise geoespacial não aplicável
    - Tarifa completa não fornecida: valores de recuperação são estimativas conservadoras
    """)
```

---

## 13. DEPENDÊNCIAS (requirements.txt)

```
streamlit>=1.35.0
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.18.0
openpyxl>=3.1.0
```

---

## 14. COMO EXECUTAR

```bash
pip install -r requirements.txt
streamlit run dashboard.py
```

O arquivo de dados deve estar no mesmo diretório que `dashboard.py` ou o caminho deve ser
ajustado na chamada `load_data(filepath)`.

---

## 15. ANTIPADRÕES A EVITAR

- ❌ **Não** usar `st.write(df)` para tabelas grandes — usar `st.dataframe(df, use_container_width=True)`
- ❌ **Não** calcular métricas fora do `@st.cache_data` — o dashboard vai recalcular a cada interação
- ❌ **Não** usar `fig.show()` do Plotly — usar `st.plotly_chart(fig, use_container_width=True)`
- ❌ **Não** hardcodar nomes de colunas mensais sem verificar existência — usar list comprehension com verificação
- ❌ **Não** misturar filtragem global e local de DataFrames — passar sempre `df_filtered` para cada aba
