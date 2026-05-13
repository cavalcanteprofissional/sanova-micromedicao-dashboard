"""
Base de conhecimento do sistema comercial de saneamento.
Dividida em chunks tematicos para indexacao vetorial.
Cada item da lista e um chunk independente.
"""

KNOWLEDGE_BASE_DOCS = [

    # -- GLOSSARIO --------------------------------------------------------------
    """
    GLOSSARIO DO SISTEMA COMERCIAL DE SANEAMENTO

    MATRICULA: Identificador unico de cada ligacao de agua/esgoto. Cada imovel
    possui uma matricula distinta no sistema comercial.

    VOLUME_LIDO: Volume medido fisicamente pelo hidrometro na leitura de campo,
    expresso em metros cubicos (m3).

    VOLUME_REAL: Volume aceito e validado pelo sistema apos analise. Pode diferir
    do volume lido quando ha suspeita de leitura incorreta ou fraude. Nunca deve
    ser maior que o VOLUME_LIDO em condicoes normais.

    VOLUME_FATURADO: Volume efetivamente cobrado na fatura. Nunca e inferior ao
    consumo minimo tarifario (10 m3), mesmo que o consumo real seja menor.

    VALOR_AGUA: Valor cobrado pelo fornecimento de agua.
    VALOR_ESGOTO: Valor cobrado pelo servico de coleta e tratamento de esgoto.
    VALOR_SERVICOS: Cobrancas adicionais por servicos especificos.
    VALOR_IMPOSTOS: Tributos incidentes sobre o faturamento.
    VALOR_DESCONTOS: Descontos concedidos (tarifa social, isencoes).
    VALOR_TOTAL: Soma de todos os componentes menos os descontos. E o valor final
    da fatura do cliente.
    """,

    # -- SITUACOES DE LIGACAO ---------------------------------------------------
    """
    SITUACOES POSSIVEIS DE UMA LIGACAO DE AGUA

    ATIVA: Ligacao funcionando normalmente, com fornecimento de agua e geracao
    de fatura mensal. A grande maioria das ligacoes esta nesta situacao.

    CANCELADA: Ligacao desativada a pedido do cliente ou por decisao administrativa.
    Nao gera faturamento. O hidrometro geralmente e retirado.

    CORTADA RAMAL: Corte realizado diretamente na rede de distribuicao (ramal),
    geralmente por inadimplencia grave ou por questoes tecnicas. E uma intervencao
    mais severa que o corte no cavalete.

    CORTADA CAVALETE: Corte realizado no cavalete do imovel (ponto de entrada da
    ligacao). E o corte mais comum por inadimplencia. O hidrometro permanece instalado.

    SUPRIMIDA: Ligacao temporariamente sem fornecimento por razoes tecnicas ou
    operacionais, sem ser considerada cancelada oficialmente.

    CORTADA NA FITA: Corte realizado com fita de seguranca no hidrometro, impedindo
    a passagem de agua. Tecnica usada como medida preventiva ou administrativa.

    ELIMINADA: Ligacao definitivamente removida do cadastro e da rede fisica.
    NAO INFORMADA: Ligacao sem informacao de situacao cadastrada no sistema.
    """,

    # -- CATEGORIAS DE CONSUMO -------------------------------------------------
    """
    CATEGORIAS DE CONSUMO E SEUS PERFIS

    RESIDENCIAL: Categoria mais numerosa, com 1.664 ligacoes (87% do total).
    Inclui apartamentos, casas e condominios residenciais.

    COMERCIAL: 143 ligacoes (7,5% do total). Exemplos: estabelecimentos comerciais,
    lojas, restaurantes, hoteis.

    INDUSTRIAL: 83 ligacoes (4,3% do total). Engloba industrias e grandes
    consumidores com processos produtivos.

    PUBLICA: 5 ligacoes (0,3% do total). Orgaos e instalacoes do poder publico.
    Geralmente possuem tratamento tarifario diferenciado.
    """,

    # -- HIDROMETROS -----------------------------------------------------------
    """
    HIDROMETROS: TIPOS, MARCAS E CLASSES METROLOGICAS

    TIPOS DE HIDROMETRO:
    - Unijato: Mais comum, com 1.348 unidades (72,6%). Funciona com um unico jato
      d'agua impulsionando a turbina. Indicado para ligacoes residenciais e
      pequenos comercios. Menor custo.
    - Unijato Pre-equipado: 284 unidades (15,3%). Versao do unijato preparada para
      leitura remota ou telemetria.
    - Multijato: 136 unidades (7,3%). Multiplos jatos de agua aumentam a precisao
      de medicao em faixas de consumo variadas. Usado em comercios e industrias.
    - Ultrassonico: 62 unidades (3,3%). Tecnologia mais avancada, sem partes moveis.
      Alta precisao e durabilidade. Indicado para grandes consumidores.

    MARCAS: O parque de hidrometros possui 6 marcas (A a F). A Marca A e dominante.
    As marcas foram anonimizadas para fins de analise.

    CLASSES METROLOGICAS (conforme ABNT NBR 15538):
    - Classe A: Padrao mais basico. 276 unidades (14,9%). Menor faixa de medicao
      precisa. Adequada para consumos muito baixos.
    - Classe B: Padrao intermediario e mais comum. 1.499 unidades (80,8%).
      Equilibrio entre custo e precisao. Recomendado para uso geral.
    - Classe C: Maior precisao. 55 unidades (3,0%). Detecta consumos muito baixos
      com maior exatidao.

    DIAMETROS DISPONIVEIS: 3/4" (mais comum - residencial), 1", 1_1/2" e 2"
    (para maiores vazoes - industrial e comercial).

    IDADE MEDIA DO PARQUE: 2,1 anos.
    HIDROMETROS COM MAIS DE 5 ANOS: 414 unidades - candidatos a substituicao por
    submediacao progressiva (equipamentos velhos tendem a medir menos do que o
    volume real, gerando perda de receita para a concessionaria).
    """,

    # -- ANOMALIAS E FRAUDES --------------------------------------------------
    """
    ANOMALIAS, FRAUDES E INCONSISTENCIAS DETECTADAS

    DIVERGENCIA LIDO vs REAL (Fraude/Adulteracao):
    Ocorre quando VOLUME_LIDO e maior que VOLUME_REAL. Em condicoes normais,
    o sistema nunca deve validar um volume real superior ao lido - o que indica
    que houve intervencao manual no sistema para reduzir artificialmente o volume
    faturado. Foram detectados 144 casos nesta situacao, representando possivel
    fraude ou erro sistmico grave.

    LIGACOES ATIVAS COM CONSUMO ZERO:
    Ligacoes com SIT._LIG_AGUA = 'ATIVA' e VOLUME_LIDO = 0 no mes de referencia.
    Causas possiveis: hidrometro parado/travado, fraude (derivacao antes do
    hidrometro), leitura nao realizada, ou imovel desoccupado ainda ativo no
    cadastro. Cada caso representa receita potencial nao capturada.

    CONSUMO CONSTANTE EXATO POR VARIOS MESES:
    Quando o volume lido e exatamente o mesmo por 6 meses ou mais, pode indicar
    que o operador esta estimando o consumo em vez de realizar a leitura efetiva
    (pratica de "consumo estimado" nao autorizada).

    CONSUMO IMPLAUSIVEL (OUTLIER ESTATISTICO):
    Volumes que excedem a media historica da ligacao em mais de 3 desvios-padrao
    podem indicar vazamento nao comunicado, fraude reversa ou erro de leitura.

    LIGACOES SEM HIDROMETRO (ativas):
    Ligacoes ativas sem NUMERO_HIDROMETRO cadastrado. Representa consumo nao
    medido e, portanto, receita nao capturada.
    """,

    # -- CONSUMO MINIMO E TARIFA -----------------------------------------------
    """
    CONSUMO MINIMO E ESTRUTURA TARIFARIA

    CONSUMO MINIMO TARIFARIO: 10 m3 por mes.
    Independentemente do volume lido, o cliente e cobrado por no minimo 10 m3.
    O VALOR_TOTAL minimo observado na base e de aproximadamente R$ 89,03
    (referencia para ligacoes residenciais no consumo minimo).

    ESTRUTURA DO FATURAMENTO:
    A fatura e composta por: VALOR_AGUA + VALOR_ESGOTO + VALOR_SERVICOS
    + VALOR_IMPOSTOS - VALOR_DESCONTOS = VALOR_TOTAL
    """,

    # -- RECUPERACAO DE RECEITA ------------------------------------------------
    """
    OPORTUNIDADES DE RECUPERACAO DE RECEITA

    1. SUBSTITUICAO DE HIDROMETROS VELHOS (414 com mais de 5 anos):
    Hidrometros envelhecidos submedem progressivamente. Premissa tecnica: 15% de
    submediacao em equipamentos com mais de 5 anos (referencia literatura tecnica
    e ABNT NBR 15538). Receita potencial estimada em R$ 1,87 milhoes/ano.

    2. REGULARIZACAO DE CONSUMO ZERO:
    Estimativa conservadora: 224 ligacoes ativas com 6+ meses sem consumo.
    Cada ligacao gera R$ 89,03/mês de receita potencial nao capturada.
    Em 12 meses: aproximadamente R$ 119.655 de potencial.

    3. FISCALIZACAO DE ANOMALIAS DE LEITURA:
    144 casos com VOLUME_LIDO > VOLUME_REAL representam divergencia que pode
    indicar adulteracao do sistema. Prioridade ALTA. Acao: auditoria de campo
    e revisao dos lancamentos.

    4. INSTALACAO DE HIDROMETRO:
    1 ligacao ativa sem NUMERO_HIDROMETRO cadastrado. Receita potencial de
    R$ 1.068/ano com tarifa minima.

    RECEITA PERDIDA POR DADOS AUSENTES:
    Ligacoes com dados mensais incompletos (missing data) geram perda estimada
    de aproximadamente R$ 362.146.

    TOTAL ESTIMADO DE RECUPERACAO: R$ 2,49 milhoes em 12 meses.
    """,

    # -- FAQ DIRETO -----------------------------------------------------------
    """
    PERGUNTAS FREQUENTES - FAQ DO SISTEMA COMERCIAL

    P: Quantas ligacoes existem na base de dados?
    R: A base contem 1.912 ligacoes no total.

    P: Qual e o faturamento total mensal?
    R: O faturamento e calculado a partir da soma de VALOR_TOTAL das ligacoes ativas.

    P: Quantas anomalias foram detectadas?
    R: 144 casos com divergencia entre volume lido e volume real (possivel fraude),
    224 ligacoes com 6+ meses de consumo zero, e 414 hidrometros com mais de
    5 anos (risco de submediacao).

    P: Qual categoria consome mais?
    R: A categoria Industrial tem o maior consumo medio individual, seguida de
    Comercial. Porem, Residencial representa a maior fatia da receita pelo volume
    absoluto de clientes.

    P: O que e consumo minimo?
    R: E o volume de 10 m3 cobrado mensalmente mesmo que o consumo real seja
    inferior. Representa uma garantia de receita minima por ligacao e cobre os
    custos fixos de disponibilizacao do servico.

    P: Qual o potencial de recuperacao de receita?
    R: Estimativa consolidada de aproximadamente R$ 2,49 milhoes em 12 meses,
    considerando substituicao de hidrometros, regularizacao de consumo zero,
    fiscalizacao de anomalias e instalacao de medidores em ligacoes ativas.

    P: Qual tipo de hidrometro e mais comum?
    R: O hidrometro Unijato e o mais comum, representando 72,6% do parque
    (1.348 unidades). A classe metrologica B e a predominante (80,8%).

    P: Como identificar uma fraude no sistema?
    R: Os principais indicadores sao: VOLUME_LIDO superior ao VOLUME_REAL,
    consumo zero persistente em ligacao ativa, consumo constante
    exato por muitos meses (indica estimativa em vez de leitura), e consumo que
    supera em mais de 3 desvios-padrao a media historica da propria ligacao.

    P: O que significa substituicao de hidrometro por submediacao?
    R: Hidrometros com mais de 5 anos de idade tendem a submedir (medir menos
    do que o volume real) devido ao desgaste mecanico. Estudos tecnicos indicam
    que a submediacao media e de 15% ao ano. A substituicao de equipamentos
    velhos recupera essa perda de receita para a concessionaria.

    P: O que e o Indice de Qualidade de Dados (IQD)?
    R: E o percentual de registros completos no dataset. Um IQD alto indica que
    a base de dados e confiavel para tomada de decisoes. IQD acima de 90% e
    considerado bom, entre 70-90% requer atencao, e abaixo de 70% indica problemas
    graves de qualidade de dados.
    """,
]


def generate_dynamic_stats(df=None):
    """
    Gera um chunk de estatisticas dinamicas a partir do DataFrame.
    Chamado em tempo de execucao para alimentar o RAG com dados reais.
    """
    if df is None:
        return ""

    ativas = (df['SIT._LIG_AGUA'] == 'ATIVA').sum() if 'SIT._LIG_AGUA' in df.columns else 0
    fat_total = df['VALOR_TOTAL'].sum() if 'VALOR_TOTAL' in df.columns else 0
    vol_fat = df['VOLUME_FATURADO'].sum() if 'VOLUME_FATURADO' in df.columns else 0
    completas = df.notna().all(axis=1).sum()
    total = len(df)
    iqd = round(completas / total * 100, 1) if total > 0 else 0

    anom_leitura = int(df['FLAG_ANOMALIA_LEITURA'].sum()) if 'FLAG_ANOMALIA_LEITURA' in df.columns else 0
    zero_meses = int((df['MESES_CONSUMO_ZERO'] >= 6).sum()) if 'MESES_CONSUMO_ZERO' in df.columns else 0
    hidro_velhos = int((df['IDADE_HIDRO_ANOS'].fillna(0) > 5).sum()) if 'IDADE_HIDRO_ANOS' in df.columns else 0

    cats = df['CATEGORIA_PRINCIPAL'].value_counts().to_dict() if 'CATEGORIA_PRINCIPAL' in df.columns else {}

    return f"""
    ESTATISTICAS DINAMICAS DA BASE DE DADOS (em tempo real):

    Total de ligacoes: {total:,}
    Ligacoes ativas: {ativas:,} ({round(ativas/total*100, 1) if total > 0 else 0}% do total)
    Faturamento mensal (ativas): R$ {fat_total:,.2f}
    Volume total faturado: {vol_fat:,.1f} m3
    Indice de Qualidade de Dados (IQD): {iqd}%
    Registros completos: {completas:,} de {total:,}

    Anomalias de leitura detectadas (LIDO > REAL): {anom_leitura:,} casos
    Ligacoes com 6+ meses de consumo zero: {zero_meses:,} casos
    Hidrometros com mais de 5 anos: {hidro_velhos:,} unidades

    Distribuicao por categoria:
    {chr(10).join(f"    - {cat}: {count:,} ligacoes" for cat, count in cats.items())}
    """
