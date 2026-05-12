import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from dashboard.config import TARIFA_MINIMA, CUSTO_UNITARIO_AGUA, FATOR_SUBMEDICAO, IDADE_HIDRO_CRITICA, COR_CRITICO, COR_ALERTA, COR_OK, COR_INFO
from dashboard.utils import format_currency, get_plotly_template


def _color_priority(val):
    if val == 'Alta':
        return 'background-color: #2D1F1F; color: #E74C3C'
    if val == 'Media':
        return 'background-color: #2D2A1A; color: #F39C12'
    return 'background-color: #1A2D1F; color: #27AE60'


def render(df):
    st.subheader("Recuperacao de Receita - Painel de Priorizacao")

    acoes = []

    sem_hidro_ativas = df[df.get('FLAG_SEM_HIDROMETRO', pd.Series([False]*len(df))) == True]
    acoes.append({
        'Acao': 'Instalar hidrometro em ligacoes ativas',
        'Qtd_Ligacoes': len(sem_hidro_ativas),
        'Receita_Potencial_12m': len(sem_hidro_ativas) * TARIFA_MINIMA * 12,
        'Prioridade': 'Alta'
    })

    anomalias = df[df.get('FLAG_ANOMALIA_LEITURA', pd.Series([False]*len(df))) == True]
    receita_anomalia = anomalias['DIVERGENCIA_VOL'].abs().sum() * CUSTO_UNITARIO_AGUA
    acoes.append({
        'Acao': 'Fiscalizar ligacoes com divergencia lido x real',
        'Qtd_Ligacoes': len(anomalias),
        'Receita_Potencial_12m': receita_anomalia * 12,
        'Prioridade': 'Alta'
    })

    zero_cronico = df[df.get('MESES_CONSUMO_ZERO', pd.Series([0]*len(df))) >= 6]
    acoes.append({
        'Acao': 'Vistoriar/reativar ligacoes c/ 6+ meses sem consumo',
        'Qtd_Ligacoes': len(zero_cronico),
        'Receita_Potencial_12m': len(zero_cronico) * TARIFA_MINIMA * 6,
        'Prioridade': 'Media'
    })

    substituicao = df[df.get('IDADE_HIDRO_ANOS', pd.Series([0]*len(df))) > IDADE_HIDRO_CRITICA].copy()
    if 'RECEITA_POTENCIAL_SUBMED' in substituicao.columns:
        receita_sub = substituicao['RECEITA_POTENCIAL_SUBMED'].sum()
    else:
        receita_sub = (substituicao['VALOR_TOTAL'].fillna(0) * FATOR_SUBMEDICAO * 12).sum()
    acoes.append({
        'Acao': 'Substituir hidrometros com > 5 anos (submedição)',
        'Qtd_Ligacoes': len(substituicao),
        'Receita_Potencial_12m': receita_sub,
        'Prioridade': 'Media'
    })

    acoes_df = pd.DataFrame(acoes).sort_values('Receita_Potencial_12m', ascending=False)

    total_receita = acoes_df['Receita_Potencial_12m'].sum()
    faturamento_12m = df['RECEITA_TOTAL_12M'].sum()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Receita Potencial (12m)", format_currency(total_receita))
    with col2:
        st.metric("Faturamento Atual (12m)", format_currency(faturamento_12m))
    with col3:
        pct = total_receita / faturamento_12m * 100 if faturamento_12m > 0 else 0
        st.metric("% Potencial vs Faturamento", f"{pct:.1f}%")

    st.divider()

    st.markdown("**Tabela de Acoes Priorizadas**")
    display_df = acoes_df.copy()
    display_df['Receita_Potencial_12m_fmt'] = display_df['Receita_Potencial_12m'].apply(format_currency)
    styled = display_df[['Acao', 'Qtd_Ligacoes', 'Receita_Potencial_12m_fmt', 'Prioridade']].style.map(
        _color_priority, subset=['Prioridade']
    )
    st.dataframe(styled, width='stretch', hide_index=True)

    st.divider()
    st.markdown("**Waterfall - Recuperacao Potencial por Acao**")

    labels = ['Faturamento Atual'] + [a['Acao'].split('(')[0].strip()[:25] for a in acoes] + ['Total Recuperacao']
    values = [faturamento_12m] + [-a['Receita_Potencial_12m'] for a in acoes] + [-total_receita]

    fig_waterfall = go.Figure(go.Waterfall(
        name="Receita",
        orientation="v",
        x=labels,
        measure=["absolute"] + ["relative"] * (len(acoes)) + ["total"],
        y=values,
        connector={"line": {"color": "#95A5A6"}},
        increasing={"marker": {"color": COR_OK}},
        decreasing={"marker": {"color": COR_CRITICO}},
        totals={"marker": {"color": COR_INFO}}
    ))
    fig_waterfall.update_layout(
        template=get_plotly_template(),
        height=400,
        yaxis_tickprefix='R$ '
    )
    st.plotly_chart(fig_waterfall, width='stretch')

    st.divider()
    st.markdown("**Gauge - Potencial de Recuperacao vs Faturamento Atual**")

    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=total_receita,
        delta={'reference': faturamento_12m},
        gauge={
            'axis': {'range': [0, max(faturamento_12m * 1.5, 100000)]},
            'bar': {'color': COR_INFO},
            'steps': [
                {'range': [0, faturamento_12m * 0.2], 'color': COR_OK},
                {'range': [faturamento_12m * 0.2, faturamento_12m * 0.4], 'color': COR_ALERTA},
                {'range': [faturamento_12m * 0.4, faturamento_12m * 0.6], 'color': COR_CRITICO},
            ],
        },
        title={'text': "Receita Potencial (R$)"}
    ))
    fig_gauge.update_layout(height=300)
    st.plotly_chart(fig_gauge, width='stretch')