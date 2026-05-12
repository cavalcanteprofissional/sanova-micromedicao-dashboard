import streamlit as st
import plotly.express as px
import pandas as pd
from dashboard.config import TARIFA_MINIMA, COR_ALERTA, COR_CRITICO, COR_OK, COR_INFO, COR_NEUTRO
from dashboard.utils import get_plotly_template, format_currency, format_currency


def render(df):
    st.subheader("Consumo Zero — Analise de Perdas Comerciais")

    zero_df = df[df['SIT._LIG_AGUA'] == 'ATIVA'].copy()
    vol_lido_cols = ['VOLUME_LIDO'] + [f'VOLUME_LIDO_{i:02d}' for i in range(1, 13)]

    if 'MESES_CONSUMO_ZERO' not in zero_df.columns:
        zero_df['MESES_ZERO'] = zero_df[vol_lido_cols].fillna(0).eq(0).sum(axis=1)
    else:
        zero_df['MESES_ZERO'] = zero_df['MESES_CONSUMO_ZERO']

    col1, col2, col3 = st.columns(3)
    with col1:
        total_ativas = len(zero_df)
        st.metric("Ligacoes Ativas", f"{total_ativas:,}")
    with col2:
        com_zero = (zero_df['MESES_ZERO'] > 0).sum()
        st.metric("Com Consumo Zero (ao menos 1 mes)", f"{com_zero:,}")
    with col3:
        receita_perdida = zero_df['MESES_ZERO'].sum() * TARIFA_MINIMA
        st.metric("Receita Potencial Perdida", format_currency(receita_perdida))

    st.divider()

    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.markdown("**Distribuicao de Meses com Consumo Zero**")
        hist_data = zero_df['MESES_ZERO'].value_counts().sort_index().reset_index()
        hist_data.columns = ['Meses Zero', 'Qtd Ligacoes']
        fig_hist = px.bar(
            hist_data, x='Meses Zero', y='Qtd Ligacoes',
            template=get_plotly_template(),
            color='Qtd Ligacoes', color_continuous_scale='Reds'
        )
        fig_hist.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig_hist, width='stretch')

    with col_g2:
        st.markdown("**Consumo Zero por Categoria**")
        cat_zero = zero_df[zero_df['MESES_ZERO'] >= 1].groupby('CATEGORIA_PRINCIPAL').size().reset_index()
        cat_zero.columns = ['Categoria', 'Qtd com Zero']
        fig_cat = px.bar(
            cat_zero, x='Categoria', y='Qtd com Zero',
            template=get_plotly_template(),
            color='Categoria',
            color_discrete_sequence=[COR_CRITICO, COR_ALERTA, COR_OK, COR_INFO]
        )
        fig_cat.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig_cat, width='stretch')

    st.divider()
    st.markdown("**Tabela: Ligacoes com >= 3 Meses de Consumo Zero**")
    criticos = zero_df[zero_df['MESES_ZERO'] >= 3][
        ['MATRICULA', 'CATEGORIA_PRINCIPAL', 'MESES_ZERO', 'VOLUME_LIDO', 'VOLUME_FATURADO']
    ].sort_values('MESES_ZERO', ascending=False)

    criticos = criticos.copy()
    criticos['Receita_Perdida_Estimada'] = criticos['MESES_ZERO'] * TARIFA_MINIMA
    if len(criticos) > 50:
        page = st.number_input("Pagina", 1, max(1, (len(criticos) - 1) // 50 + 1), 1, key="zero_page")
        start = (page - 1) * 50
        criticos_page = criticos.iloc[start:start + 50]
    else:
        criticos_page = criticos
    st.dataframe(criticos_page, width='stretch', height=400)

    st.markdown(f"**Total de ligacoes criticas (>= 3 meses zero):** {len(criticos):,}")
    st.markdown(f"**Receita perdida estimada (casos criticos):** {format_currency(criticos['Receita_Perdida_Estimada'].sum())}")