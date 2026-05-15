# Documentação Técnica — Dados de Micromedição SANOVA

> Este documento descreve as características dos dados, o processo de ETL e a estrutura do dashboard. Criado para servir como referência técnica e material de entrevista.

---

## 1. Visão Geral do Projeto

### Qual é o contexto e objetivo deste projeto?

O projeto foi desenvolvido como teste prático para o cargo de Analista de Dados na **SANOVA** (sanova.com.br), empresa com quase 15 anos de atuação no mercado nacional de saneamento e mais de 150 clientes impactados.

O objetivo é demonstrar capacidade de **engenharia de dados e análise de sistemas comerciais de saneamento**, com foco em micromedição, detecção de anomalias e recuperação de receita.

### Qual é o escopo da análise?

A análise abrange **1.912 ligações de água** ao longo de **13 meses** (mês atual + 12 meses históricos). Cada ligação possui registros de consumo, faturamento, informações cadastrais do hidrômetro e status operacional.

### Quais perguntas estratégicas o dashboard responde?

| Pergunta | Aba do Dashboard |
|----------|-------------------|
| Quais ligações geram/pagam receita? | Visão Geral |
| Onde há sinais de fraude? | Anomalias & Fraudes |
| Quanto custa o consumo zero? | Consumo Zero |
| Quais hidrômetros precisam de troca? | Hidrômetros |
| Quanto podemos recuperar de receita? | Recuperação de Receita |
| Os dados são confiáveis? | Qualidade de Dados |
| Posso fazer perguntas em linguagem natural? | Chatbot IA |

---

## 2. Dados Originais — Estado Antes do Tratamento

### De onde vêm os dados?

Os dados originais estão no arquivo `data/raw/micromedicao.xlsx`, um arquivo Excel com **132 colunas** e **1.912 linhas** (uma por ligação).

### Quais são as principais categorias de dados presentes?

**Dados Cadastrais:**
- MATRICULA (identificador único da ligação)
- SIT._LIG_AGUA (status: Ativa, Cancelada, Cortada, Suprimida, etc.)
- SIT._LIG_ESGOTO
- CATEGORIA_PRINCIPAL (Residencial, Comercial, Industrial, Pública)
- NUMERO_HIDROMETRO, TIPO_HIDROMETRO, MARCA_HIDROMETRO
- CLASSE_METROLOGICA, DIAMETRO_HIDROMETRO
- DATA_INSTALACAO_HIDROMETRO
- NUMERO_ECONOMIAS_* (residencial, comercial, industrial, pública)

**Dados de Consumo (13 meses):**
- VOLUME_LIDO, VOLUME_REAL, VOLUME_FATURADO (mês atual)
- VOLUME_LIDO_01 a VOLUME_LIDO_12 (meses históricos)
- Mesma lógica para VOLUME_REAL e VOLUME_FATURADO

**Dados de Faturamento (13 meses):**
- VALOR_AGUA, VALOR_ESGOTO, VALOR_SERVICOS
- VALOR_IMPOSTOS, VALOR_DESCONTOS, VALOR_TOTAL
- Mesma estrutura para os 12 meses históricos (_01 a _12)

### Qual era a qualidade inicial dos dados?

O dados originais apresentavam alguns problemas identificados:

- **Texto com encoding inconsistente**:Caracteres acentuados e variações de maiúsculas/minúsculas
- **Números em formato brasileiro**: Vírgula como separador decimal (ex: "123,45")
- **Datas em formato brasileiro**: DD/MM/AAAA necessitando conversão
- **Missing values**: Colunas com dados ausentes, especialmente em campos cadastrais
- **Valores inconsistentes**: Algumas ligações sem número de hidrômetro

### Como os dados são distribuídos por categoria?

| Categoria | Quantidade | Percentual |
|-----------|------------|------------|
| Residencial | 1.664 | 87% |
| Comercial | 143 | 7,5% |
| Industrial | 83 | 4,3% |
| Pública | 5 | 0,3% |

### Quais são as situações das ligações?

| Situação | Quantidade |
|----------|------------|
| Ativa | 1.815 |
| Cancelada | 39 |
| Cortada Ramal | 20 |
| Cortada Cavalete | 9 |
| Suprimida | 6 |
| Cortada na Fita | 6 |
| Eliminada | 2 |

---

## 3. Processo ETL — Pipeline de Engenharia de Dados

### O que é ETL e por que é necessário?

ETL (Extract, Transform, Load) é o processo de extrair dados da fonte original, transformá-los para análise e carregá-los em um formato adequado. No caso deste projeto, o Excel original com 132 colunas foi transformado em um CSV tratado com 151 colunas, pronto para análise no dashboard.

### Quais são as 10 etapas do pipeline?

#### Etapa 1: Normalização de Texto

**O que faz:** Converte todo texto para maiúsculas e remove acentos.

**Por que faz:** Garante consistência nas buscas e comparações. "Residencial" e "RESIDENCIAL" são treated como a mesma categoria.

**Código relevante (transformer.py):**
```python
def normalize_text(text: str) -> str:
    text = str(text).strip().upper()
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')
    return text
```

#### Etapa 2: Conversão Decimal Brasileiro

**O que faz:** Substitui vírgula por ponto em campos numéricos.

**Por que faz:** O Python e pandas usam ponto como separador decimal. "123,45" precisa virar 123.45 para operações matemáticas.

#### Etapa 3: Conversão de Datas

**O que faz:** Converte datas do formato brasileiro (DD/MM/AAAA) para datetime do pandas.

**Por que faz:** Permite cálculos de idade, sazonalidade e análise temporal.

**Campo convertido:** DATA_INSTALACAO_HIDROMETRO → DATA_INSTALACAO_HIDROMETRO_DT

#### Etapa 4: Tratamento de Missing Cadastral

**O que faz:** Identifica ligações com todos os campos de hidrômetro vazios e preenche com valores padrão.

**Por que faz:** Evita warnings e permite análise consistente. Se todos os campos de hidrômetro estão vazios, marca como "SEM_HIDROMETRO".

**Valores preenchidos:**
- TIPO_HIDROMETRO → "SEM_HIDROMETRO"
- MARCA_HIDROMETRO → "SEM_HIDROMETRO"
- CLASSE_METROLOGICA → "N/A"
- DIAMETRO_HIDROMETRO → "N/A"

#### Etapa 5: Tratamento de Missing em Economias

**O que faz:** Converte campos de número de economias para numérico e preenche zeros onde há missing.

**Por que faz:** Garante que operações matemáticas funcione. Se uma ligação não tem economias comerciais, assume 0.

#### Etapa 6: Conversão de Volumes e Valores para Numérico

**O que faz:** Converte todas as colunas de VOLUME_* e VALOR_* para tipo numérico.

**Por que faz:** Permite cálculos estatísticos, soma, média, etc. Dados em formato string não permitem operações matemáticas.

**Colunas afetadas (26 colunas × 13 meses = centenas de colunas):**
- VOLUME_LIDO, VOLUME_REAL, VOLUME_FATURADO (+ _01 a _12)
- VALOR_AGUA, VALOR_ESGOTO, VALOR_SERVICOS, VALOR_IMPOSTOS, VALOR_DESCONTOS, VALOR_TOTAL (+ _01 a _12)

#### Etapa 7: Tratamento de Outliers

**O que faz:** Identifica volumes extremamente altos (acima do percentil 99) e cria flag.

**Por que faz:** Consumos muito acima da média podem indicar erro de leitura, vazamento, ou até fraude reversa.

**Lógica:** FLAG_OUTLIER_EXTREMO = VOLUME_LIDO > P99

#### Etapa 8: Enriquecimento com Campos Calculados

**O que faz:** Cria 14 novas colunas derivadas dos dados originais.

**Por que faz:** Permite análises que não seriam possíveis com os dados brutos.

**Campos criados:**

| Campo | Descrição |
|-------|-----------|
| IDADE_HIDRO_ANOS | Idade do hidrômetro em anos |
| RECEITA_TOTAL_12M | Soma do VALOR_TOTAL dos 12 meses |
| VOLUME_TOTAL_12M | Soma do VOLUME_FATURADO dos 12 meses |
| MESES_DADOS_AUSENTES | Quantos meses não possuem leitura |
| MESES_CONSUMO_ZERO | Quantos meses com consumo = 0 |
| DIVERGENCIA_VOL | VOLUME_REAL - VOLUME_LIDO |
| FLAG_ANOMALIA_LEITURA | True se LIDO > REAL + 1m³ |
| FLAG_SEM_HIDROMETRO | True se ativa sem número de hidrômetro |
| FLAG_CONSUMO_ZERO | True se ativa com volume = 0 |
| MEDIA_VOL_12M | Média de volume dos 12 meses |
| STD_VOL_12M | Desvio padrão do volume dos 12 meses |
| FLAG_DADOS_INCOMPLETOS | True se há meses sem dados |
| SCORE_PRIORIDADE | Pontuação para priorização (50/40/30/20/10) |
| RECEITA_POTENCIAL_SUBMED | Receita perdida por submedição (15% × 12m) |
| FLAG_CONSUMO_CONSTANTE | True se mesmo consumo por 6+ meses |
| FLAG_CONSUMO_IMPLAUSIVEL | True se consumo > média + 3 desvios |

#### Etapa 9: Cálculo do Score de Prioridade

**O que faz:** Atribui uma pontuação numérica a cada ligação para priorização de ações.

**Por que faz:** Permite ordenar as ligações por criticidade, focando primeiro nos casos mais graves.

**Fórmula:**
```
SCORE_PRIORIDADE =
  FLAG_ANOMALIA_LEITURA × 50
  + FLAG_SEM_HIDROMETRO × 40
  + FLAG_CONSUMO_ZERO × 30
  + (MESES_CONSUMO_ZERO ≥ 3) × 20
  + (IDADE_HIDRO_ANOS > 5) × 10
```

#### Etapa 10: Validação e Logging

**O que faz:** Verifica a qualidade do dado processado e gera um relatório.

**Por que faz:** Garante que o pipeline funcionou corretamente e identifica problemas.

**Validações realizadas (código em loader.py):**

| Código | Verificação | Flag Criada |
|--------|-------------|-------------|
| Q001 | MATRICULA duplicada | — |
| Q002 | Datas de instalação futuras | — |
| Q003 | Inconsistências em VALOR_TOTAL | `FLAG_INCONSIST_FATURAMENTO` |
| Q004 | VOLUME_FATURADO < VOLUME_REAL | `FLAG_FATURADO_MENOR_REAL` |
| Q005 | Outliers extremos detectados | `FLAG_OUTLIER_EXTREMO` |
| Q006 | Volumes/valores negativos | `FLAG_VOLUME_NEGATIVO`, `FLAG_VALOR_NEGATIVO` |
| Q007 | Ligação ativa sem receita | `FLAG_ATIVA_SEM_RECEITA` |
| Q008 | Categoria ausente | `FLAG_SEM_CATEGORIA` |
| Q009 | Data de instalação inválida | `FLAG_DATA_INVALIDA` |
| Q010 | Zero economias (ativa) | `FLAG_ZERO_ECONOMIAS` |
| Q012 | VOLUME_REAL > VOLUME_LIDO | `FLAG_REAL_MAIOR_LIDO` |

**Log gerado:** `data/stage/validation_log.json` (detalhado com MATRÍCULAS afetadas para Q003, Q004, Q008, Q012)

### Qual é o resultado final do ETL?

| Métrica | Valor |
|---------|-------|
| Total de linhas | 1.912 |
| Total de colunas | ~170 (antes: 132, depois: 151) |
| Arquivo de saída | `data/processed/micromedicao_tratado.csv` |
| Validações implementadas | Q001-Q012 (12 códigos) |

---

## 4. Dados Tratados — Estado Após o Tratamento

### Quais são os campos derivados mais importantes?

**Campos de Detecção de Anomalias:**
- FLAG_ANOMALIA_LEITURA: 144 casos detectados (LIDO > REAL + 1m³)
- FLAG_CONSUMO_ZERO: 77 ligações ativas com consumo zero no mês
- FLAG_SEM_HIDROMETRO: 1 ligação ativa sem hidrômetro
- FLAG_OUTLIER_EXTREMO: volumes acima do P99
- FLAG_CONSUMO_CONSTANTE: mesmo consumo por 6+ meses
- FLAG_CONSUMO_IMPLAUSIVEL: consumo > média + 3 desvios

**Campos de Validação de Qualidade (Q004-Q012):**
- FLAG_FATURADO_MENOR_REAL: VOLUME_FATURADO < VOLUME_REAL
- FLAG_VOLUME_NEGATIVO: Volumes negativos (impossível fisicamente)
- FLAG_VALOR_NEGATIVO: Valores monetários negativos
- FLAG_ATIVA_SEM_RECEITA: Ligação ativa com VALOR_TOTAL = 0
- FLAG_SEM_CATEGORIA: CATEGORIA_PRINCIPAL ausente
- FLAG_DATA_INVALIDA: Data de instalação nula ou futura
- FLAG_ZERO_ECONOMIAS: Ligação ativa com 0 economias
- FLAG_REAL_MAIOR_LIDO: VOLUME_REAL > VOLUME_LIDO (matematicamente impossível)
- FLAG_INCONSIST_FATURAMENTO: VALOR_TOTAL ≠ soma dos componentes
- VALOR_TOTAL_CALCULADO: Soma: ÁGUA + ESGOTO + SERVIÇOS + IMPOSTOS - DESCONTOS
- DIFERENCA_FATURAMENTO: Diferença absoluta entre TOTAL e CALCULADO

**Campos de Análise Temporal:**
- MESES_CONSUMO_ZERO: quantos meses com volume = 0
- IDADE_HIDRO_ANOS: idade do hidrômetro

**Campos de Receita:**
- RECEITA_TOTAL_12M: faturamento acumulado em 12 meses
- RECEITA_POTENCIAL_SUBMED: receita perdida por submedição

### Quais são as métricas agregadas do banco tratado?

| Métrica | Valor |
|---------|-------|
| Ligações ativas | 1.815 (94,9%) |
| Faturamento mensal (ativas) | R$ 1.167.995,44 |
| Volume médio faturado | 46,2 m³/ligação/mês |
| Índice de Consumo Zero (ICZ) | 4,2% (77/1.815) |
| Taxa de Anomalia de Leitura | 0,57% (11/1.912) |

---

## 5. Dashboard — Descrição dos Gráficos por Aba

### Aba 1: Visão Geral

**KPIs exibidos:**
- 💧 Ligações Ativas: 1.815
- 💰 Faturamento Mensal: R$ 1.167.995,44
- 📊 Volume Faturado: 83.871 m³
- 🚨 Casos Comerciais: anomalias + consumo zero
- 📋 IQD (Índice de Qualidade de Dados): ~88,4%

**Gráfico 1: Distribuição por Categoria (Pizza)**
- Mostra a proporção de ligações por categoria (Residencial, Comercial, Industrial, Pública)
- Cores: azul (info), verde água (ativo), cinza (neutro), laranja (alerta)
- Interativo: hovering mostra detalhes

**Gráfico 2: Distribuição por Situação da Ligação (Barras horizontais)**
- Status operacional das ligações
- Cores semânticas: Ativa (verde), Cancelada (cinza), Cortada (vermelho)
- Permite identificar rapidamente o volume de ligações inativas

**Gráfico 3: Evolução do Faturamento (Área)**
- Linha temporal de 13 meses
- Eixo Y: valor em R$
- mostra sazonalidade e tendências de receita

**Gráfico 4: Consumo Médio por Categoria × Mês (Heatmap)**
- Eixo X: meses do período
- Eixo Y: categorias
- Cor: vermelho = alto consumo, verde = baixo
- Permite identificar padrões sazonais por tipo de cliente

### Aba 2: Anomalias & Fraudes

**O que detecta esta aba?**
- Divergência entre VOLUME_LIDO e VOLUME_REAL (possível fraude)
- Ligações ativas sem hidrômetro
- Outliers extremos (consumo anômalo)
- Consumo implausível (acima da média + 3 desvios)
- Consumo constante exato por múltiplos meses (leitura estimada)

**Gráfico 1: Dispersão Volume Lido × Volume Real (Scatter)**
- Cada ponto é uma ligação
- Linha diagonal vermelha: LIDO = REAL (esperado)
- Pontos à esquerda da linha: LIDO > REAL = possível subcobrança (fraude)
- Cores: verde = dentro do esperado, vermelho = divergência negativa

**Gráfico 2: Contagem por Tipo de Anomalia (Barras)**
- Anomalia de Leitura (LIDO > REAL)
- Sem Hidrômetro (Ativa)
- Outlier Extremo
- Consumo Implausível

**Tabela: Casos Prioritários**
- Lista ordenada por SCORE_PRIORIDADE
- Colunas: MATRICULA, Categoria, Situação, Volumes, Flags, Score
- Paginação para casos acima de 50 linhas

### Aba 3: Consumo Zero

**O que analisa esta aba?**
- Ligações ativas com consumo zero
- Quantos meses sem consumo
- Receita perdida por consumo mínimo não faturado

**KPIs:**
- Total de Ligações Ativas
- Com Consumo Zero (quantidade e percentual)
- Receita Potencial Perdida (meses × tarifa mínima R$ 89,03)

**Gráfico 1: Distribuição de Meses com Consumo Zero (Barras)**
- Eixo X: quantidade de meses (1, 2, 3... até 13)
- Eixo Y: quantidade de ligações
- Identifica ligações com consumo zero crônico

**Gráfico 2: Consumo Zero por Categoria (Barras)**
- Percentual de ligações com ao menos 1 mês de consumo zero
- Por categoria (Residencial, Comercial, Industrial)
- Identifica qual categoria tem maior problema

**Tabela: Ligações Críticas (≥ 3 meses zero)**
- MATRICULA, Categoria, Meses Zero, Volumes
- Receita Perdida Estimada
- Colorização: vermelho (≥12 meses), laranja (≥6 meses)

### Aba 4: Hidrômetros

**O que analisa esta aba?**
- Tipo, marca, classe metrológica
- Idade do parque de hidrômetros
- Candidatos a substituição

**KPIs:**
- Total de Hidrômetros instalados
- Candidatos a Substituição (>5 anos)
- Idade Média do parque

**Gráfico 1: Distribuição por Tipo (Pizza)**
- Unijato (72,6%)
- Unijato Pré-equipado (15,3%)
- Multijato (7,3%)
- Ultrassônico (3,3%)

**Gráfico 2: Distribuição por Marca (Barras)**
- 6 marcas (anonimizadas: A, B, C, D, E, F)
- Marca A é dominante

**Gráfico 3: Distribuição por Classe Metrológica (Barras)**
- Classe A (14,9%)
- Classe B (80,8%) - mais comum
- Classe C (3,0%)

**Gráfico 4: Distribuição de Idade (Histograma)**
- Eixo X: anos de idade
- Linha tracejada: limiar de 5 anos
- Identifica hidrômetros velhos

**Tabela: Candidatos a Substituição (>5 anos)**
- MATRICULA, Marca, Tipo, Classe, Idade, Volumes, Valores
- Receita Potencial por Submedição (15% × 12 meses)
- Total: 414 hidrômetros, R$ 1,87M potencial

### Aba 5: Recuperação de Receita

**O que mostra esta aba?**
- Oportunidades de recuperação de receita
- Ações priorizadas por impacto

**KPIs:**
- Receita Potencial (12 meses)
- Faturamento Atual (12 meses)
- Percentual do potencial vs faturamento

**Gráfico 1: Tabela de Ações Priorizadas**

| Ação | Qtd Ligações | Receita Potencial | Prioridade |
|------|--------------|-------------------|------------|
| Substituir hidrômetros >5 anos | 414 | R$ 1.870.000 | Média |
| Vistoriar 6+ meses sem consumo | 224 | R$ 120.000 | Média |
| Fiscalizar divergência LIDO×REAL | 144 | R$ 144.000 | Alta |
| Instalar hidrômetro (ativa) | 1 | R$ 1.000 | Alta |

**Gráfico 2: Waterfall — Recuperação Potencial por Ação**
- Mostra cada ação como uma redução do faturamento potencial
- Visualiza o impacto de cada ação isoladamente

**Gráfico 3: Gauge — Potencial vs Faturamento**
- Indicador visual do valor absoluto de recuperação
- Faixas: verde (<20%), laranja (20-40%), vermelho (>40%)

### Aba 6: Qualidade de Dados

**O que avalia esta aba?**
- Índice de Qualidade de Dados (IQD)
- Missing values por coluna e por mês
- Validações Q001-Q012

**KPIs de Qualidade:**
- IQD: percentual de registros completos
- Registros Completos vs Total
- Registros Incompletos
- Receita Perdida por Missing

**KPIs de Inconsistências (Q001-Q012):**
| KPI | Código | Descrição |
|-----|--------|------------|
| Q003 Faturamento | Q003 | VALOR_TOTAL ≠ soma componentes |
| Q004 Fat < Real | Q004 | VOLUME_FATURADO < VOLUME_REAL |
| Q006 Negativos | Q006 | Volumes/valores negativos |
| Q007 Sem Receita | Q007 | Ligação ativa com valor = 0 |
| Q008 Sem Categoria | Q008 | CATEGORIA_PRINCIPAL ausente |
| Q009 Data Inválida | Q009 | Dataausente ou futura |
| Q010 Zero Economias | Q010 | Ativa com 0 economias |
| Q012 Real > Lido | Q012 | VOLUME_REAL > VOLUME_LIDO |

**Gráfico 1: Evolução do Missing ao Longo do Tempo (Linha)**
- Eixo X: meses
- Eixo Y: percentual de missing em VOLUME_LIDO
- Identifica meses com problemas de leitura

**Gráfico 2: Heatmap de Missing por Coluna × Mês**
- Colunas: VOLUME_LIDO, VOLUME_REAL, VOLUME_FATURADO, VALOR_*
- Meses: 13 meses
- Escala de cores: mais vermelho = mais missing
- Identifica padrões sistêmicos

**Gráfico 3: Inconsistências Detectadas — Tabela Consolidada Q001-Q012**
- 12 códigos de validação em uma única tabela
- Códigos com valor > 0 destacados em vermelho
- Inclui: Q001, Q002, Q003, Q004, Q005, Q006, Q007, Q008, Q009, Q010, Q012

**Tabelas Detalhadas por Validação:**
- Q003: Inconsistências de Faturamento — MATRICULA, componentes, valores
- Q004: VOLUME_FATURADO < VOLUME_REAL — MATRICULA, volumes
- Q007: Ligações Ativas sem Receita — MATRICULA, categoria, valor
- Q008: Sem Categoria — MATRICULA, situação
- Q012: VOLUME_REAL > VOLUME_LIDO — MATRICULA, volumes

**Gráfico 4: Registros por Tipo de Inconsistência (Barras)**
- Agrupado por SIT._LIG_AGUA
- Mostra onde as inconsistências estão concentradas

**Tabela: Top 10 Colunas com Maior Missing**
- Coluna, Quantidade missing, Percentual
- Colorização: vermelho (>20%), laranja (5-20%)

---

## 6. Premissas Técnicas e Metodologia

### Quais premissas foram adotadas?

| Premissa | Valor | Justificativa |
|----------|-------|---------------|
| Tarifa mínima | R$ 89,03 | Menor VALOR_TOTAL observado (~10m³) nos dados reais |
| Custo unitário água | R$ 10/m³ | Estimativa de custo operacional médio |
| Fator de submedição | 15% | Referência ABNT NBR 15538 e literatura técnica |
| Idade crítica hidrômetro | >5 anos | Limiar para considerar substituição |
| Anomalia de leitura | LIDO > REAL + 1m³ | Critério empírico para detecção |
| Consumo crônico zero | ≥6 meses | Padrão do setor de saneamento |

### Como funciona o Score de Prioridade?

O score é calculado empiricamente com pesos definidos para priorizar ações:

| Flag | Peso | Justificativa |
|------|------|---------------|
| Anomalia de leitura | 50 | Alto impacto direto em receita (fraude) |
| Sem hidrômetro (ativa) | 40 | Sem medição = sem controle = perda |
| Consumo zero ativo | 30 | Possível perda de receita potencial |
| 3+ meses consumo zero | 20 | Padrão crônico confirmado |
| Hidrômetro >5 anos | 10 | Submedição gradual, impacto distribuído |

### Quais são as limitações dos dados?

- **Marcas anonimizadas**: As 6 marcas de hidrômetro estão codificadas como A, B, C, D, E, F — não é possível correlacionar com padrões de desgaste por fabricante.

- **Endereços não disponíveis**: A análise geoespacial não é aplicável, limiting a capacidade de identificar padrões espaciais.

- **Tarifa completa não fornecida**: Os valores de recuperação são estimativas conservadoras baseadas na tarifa mínima observada.

- **Falsos positivos industriais**: Consumidores industriais podem ter consumo muito variável, gerando falsos positivos em "consumo implausível".

---

## 7. Chatbot IA — Propósito e Funcionalidade

### Qual é o propósito do chatbot?

O chatbot foi desenvolvido para permitir que usuários façam **perguntas em linguagem natural** sobre os dados de micromedição, sem necessidade de conhecimento técnico ou de consultas SQL.

Ele responde perguntas como:
- "Quantas ligações existem na base?"
- "Qual é o faturamento total mensal?"
- "Quantas anomalias foram detectadas?"
- "Qual categoria consome mais?"
- "O que é consumo mínimo?"
- "Qual o potencial de recuperação de receita?"

### Qual é a arquitetura do chatbot?

**Versão Leve (atual):**
- **Provider**: Cohere API
- **Modelo**: command-r7b-12-2024 (128K context)
- **Sem RAG**: Não usa embeddings ou vector store
- **Sem LangChain**: Arquitetura simplificada

**Comparação com versão anterior:**

| Componente | Antes (RAG) | Depois (Leve) |
|------------|-------------|---------------|
| Provider | HuggingFace | Cohere |
| Modelo | Phi-3-mini (problemas) | command-r7b-12-2024 |
| Embeddings | sentence-transformers | Removido |
| Vector Store | FAISS | Removido |
| Dependencies | 126+ packages | 66 packages |

A versão leve foi implementada para evitar travamentos e lentidão que ocorriam com a versão anterior baseada em RAG.

### Como o chatbot obtém contexto dos dados?

O chatbotrecebe um **contexto dinâmico** gerado a partir do DataFrame atual:

```python
def get_stats_context(df) -> str:
    return f"""
    📊 ESTATÍSTICAS ATUAIS:
    - Total de ligações: {len(df)}
    - Ligações ativas: {ativas}
    - Faturamento mensal: R$ {faturamento_mensal}
    - Volume total: {vol_total} m³
    - Anomalias (LIDO > REAL): {anomalias} casos
    - Consumo zero ativo: {consumo_zero} casos
    - Hidrômetros > 5 anos: {hidro_velhos} unidades
    """
```

### Como funciona o fluxo de execução?

1. **Usuário envia pergunta** em português
2. **Sistema gera contexto** com KPIs dinâmicos do DataFrame
3. **Prompt é construído** com SYSTEM_PROMPT + contexto + pergunta
4. **API Cohere é chamada** com timeout de 90 segundos
5. **Resposta é retornada** ou fallback é acionado

### Quais são os fallbacks implementados?

Se a API falhar (timeout, rate limit, erro de conexão), o sistema usa **9 respostas predefinidas** para tópicos conhecidos:

| Tópico | Resposta |
|--------|----------|
| "quantas ligações" | 1.912 ligações (1.664 residenciais, 143 comerciais, 83 industriais, 5 públicas) |
| "faturamento" | Soma do VALOR_TOTAL das ligações ativas |
| "anomalias" | 144 divergências, 224 consumo zero 6+ meses, 414 hidrômetros velhos |
| "consumo médio" | Industrial > Comercial > Residencial |
| "consumo mínimo" | 10 m³ cobrados independentemente do consumo |
| "recuperação" | ~R$ 2,49M em 12 meses |
| "hidrômetro" | Unijato (72,6%), Classe B (80,8%), idade média 2,1 anos |
| "fraude" | LIDO > REAL, consumo zero persistente, consumo constante exato |
| "submedição" | 15% de submedição ao ano em hidrômetros >5 anos |

### Como configurar o chatbot?

1. Criar conta em [cohere.com](https://cohere.com) (gratuito)
2. Gerar API Key em https://dashboard.cohere.com/
3. Adicionar ao arquivo `.env.local`:

```bash
COHERE_API_KEY=seu_token_aqui
```

Ou configurar nos Secrets do Streamlit Cloud para deploy.

### Quais são os recursos de sessão?

- **Cache via session_state**: A instância do LLM é criada uma única vez por sessão
- **Histórico de conversa**: Mensagens anteriores são mantidas na sessão
- **Fallback FAQ**: Respostas predefinidas paraTopics conhecidos
- **Timeout robusto**: 90 segundos com 3 tentativas de retry

---

## Resumo Técnico

| Aspecto | Detalhe |
|---------|---------|
| **Dados originais** | Excel 1.912 × 132 colunas |
| **Dados tratados** | CSV ~170 colunas |
| **Pipeline ETL** | 12 etapas (normalização → enriquecimento → validação Q001-Q012) |
| **Validações** | Q001-Q012 (12 códigos de verificação de qualidade) |
| **Stack** | Python, Pandas, Streamlit, Plotly |
| **Chatbot** | Cohere API (command-r7b-12-2024), Prompt Engineering |
| **Dashboard** | 6 abas analíticas + chatbot, 12 KPIs de inconsistências |
| **Testes** | 34 testes pytest |

---

## 8. Resultados Coletados e Dados do Dataset

### Métricas do Dataset Original

| Métrica | Valor |
|---------|-------|
| Total de registros | 1.912 |
| Período | 13 meses (atual + 12 históricos) |
| Colunas originais | 132 |
| Duplicatas de MATRICULA | 0 |

### Distribuição por Categoria

| Categoria | Quantidade | Percentual |
|-----------|------------|------------|
| Residencial | 1.664 | 87% |
| Comercial | 143 | 7,5% |
| Industrial | 83 | 4,3% |
| Pública | 5 | 0,3% |

### Distribuição por Situação da Ligação

| Situação | Quantidade |
|----------|------------|
| Ativa | 1.815 |
| Cancelada | 39 |
| Cortada Ramal | 20 |
| Cortada Cavalete | 9 |
| Suprimida | 6 |
| Cortada na Fita | 6 |
| Eliminada | 2 |

### Resultados das Validações Q001-Q012

| Código | Validação | Quantidade | Status |
|--------|-----------|-------------|--------|
| Q001 | MATRÍCULA duplicada | 0 | ✅ OK |
| Q002 | Data futura | 0 | ✅ OK |
| Q003 | Inconsistência faturamento | 1 | ⚠️ 1 caso |
| Q004 | VOLUME_FATURADO < VOLUME_REAL | 0 | ✅ OK |
| Q005 | Outliers extremos | 19 | ⚠️ Detectados |
| Q006 | Valores negativos | 0 | ✅ OK |
| Q007 | Ativa sem receita | 0 | ✅ OK |
| Q008 | Sem categoria | 17 | ⚠️ Detectados |
| Q009 | Data inválida | 82 | ⚠️ Ausentes |
| Q010 | Zero economias | 0 | ✅ OK |
| Q012 | REAL > LIDO | 0 | ✅ OK |

### KPIs Financeiros do Dataset

| Métrica | Valor |
|---------|-------|
| Faturamento mensal (ativas) | R$ 1.167.995,44 |
| Volume médio faturado | 46,2 m³/ligação/mês |
| Índice de Consumo Zero (ICZ) | 4,2% (77/1.815) |
| Taxa de Anomalia de Leitura | 0,57% |

### Oportunidades de Recuperação de Receita

| Oportunidade | Quantidade | Receita Potencial (12m) |
|--------------|------------|-------------------------|
| Substituir hidrômetros >5 anos | 414 | R$ 1.870.000 |
| Vistoriar 6+ meses sem consumo | 224 | R$ 120.000 |
| Fiscalizar divergência LIDO×REAL | 144 | R$ 144.000 |
| Instalar hidrômetro (ativa) | 1 | R$ 1.000 |
| **Total estimado** | | **~R$ 2,5M** |

---

*Documento atualizado em maio de 2026 para referência técnica e entrevistas.*