COR_CRITICO = '#D32F2F'
COR_ALERTA  = '#FFA000'
COR_OK      = '#00BFA5'
COR_INFO    = '#1976D2'
COR_NEUTRO  = '#95A5A6'

TARIFA_MINIMA = 89.03
CUSTO_UNITARIO_AGUA = 10.0
FATOR_SUBMEDICAO = 0.15
IDADE_HIDRO_CRITICA = 5
MESES_ZERO_CRONICO = 6

PLOTLY_TEMPLATE = 'plotly_dark'
COLOR_SEQUENCE = [COR_INFO, COR_OK, COR_ALERTA, COR_CRITICO, COR_NEUTRO]

PREMISSAS = """
**Premissas adotadas:**
- **Tarifa mínima:** R$ 89,03 (baseada no menor VALOR_TOTAL observado nos dados para consumo de ~10 m³) — validar com tarifa vigente da concessionária
- **Custo unitário da água:** ~R$ 10/m³ (estimativa para cálculo de receita perdida por divergência) — referência: custo operacional médio de saneamento
- **Fator de submedição em hidrómetros > 5 anos:** 15% (referência ABNT NBR 15538 e literatura técnica)
- **Consumo crônico zero:** ≥ 6 meses consecutivos ou alternados sem medição — padrão do setor
- **Anomalia de leitura:** VOLUME_LIDO > VOLUME_REAL em mais de 1 m³ no mês de referência — limiar empírico
- **Consumo implausível:** volume > média_12m + 3 × desvio_padrão_12m — método estatístico padrão
- **Período de referência:** 13 meses (mês atual + 12 meses históricos)

**Score de Prioridade (metodologia):**
O score é calculado empiricamente com os seguintes pesos:
- Anomalia de leitura (LIDO > REAL + 1m³): 50 pontos
- Ligação ativa sem hidrômetro: 40 pontos
- Consumo zero ativo: 30 pontos
- 3+ meses consumo zero: 20 pontos
- Hidrômetro > 5 anos: 10 pontos
⚠️ *Pesos definidos empiricamente e ajustáveis conforme validação de campo*

**Limitações dos dados:**
- Marcas de hidrômetro anonimizadas (MARCA A–F): não é possível correlação com padrões de desgaste por fabricante
- Endereços não disponíveis: análise geoespacial não aplicável
- Tarifa completa não fornecida: valores de recuperação são estimativas conservadoras
- Consumidores industriais podem ter falso positivo em "consumo implausível" devido à alta variabilidade
"""