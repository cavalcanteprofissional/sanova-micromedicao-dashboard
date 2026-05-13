COR_CRITICO = '#E74C3C'
COR_ALERTA  = '#F39C12'
COR_OK      = '#27AE60'
COR_INFO    = '#2980B9'
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
- **Tarifa mínima:** R$ 89,03 (baseada no menor VALOR_TOTAL observado nos dados para consumo de ~10 m³)
- **Custo unitário da água:** ~R$ 10/m³ (estimativa para cálculo de receita perdida por divergência)
- **Fator de submedição em hidrómetros > 5 anos:** 15% (referência ABNT NBR 15538 e literatura técnica)
- **Consumo crônico zero:** ≥ 6 meses consecutivos ou alternados sem medição
- **Anomalia de leitura:** VOLUME_LIDO > VOLUME_REAL em mais de 1 m³ no mês de referência
- **Consumo implausível:** volume > média_12m + 3 × desvio_padrão_12m
- **Período de referência:** 13 meses (mês atual + 12 meses históricos)

**Limitações dos dados:**
- Marcas de hidrómetro anonimizadas (MARCA A–F): não é possível correlação com padrões de desgaste por fabricante
- Endereços não disponíveis: análise geoespacial não aplicável
- Tarifa completa não fornecida: valores de recuperação são estimativas conservadoras
"""