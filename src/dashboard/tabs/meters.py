import streamlit as st
import plotly.express as px
import pandas as pd
from dashboard.config import COR_INFO, COR_OK, COR_ALERTA, IDADE_HIDRO_CRITICA, FATOR_SUBMEDICAO
from dashboard.utils import get_plotly_template, format_currency


def render(df):
    st.subheader("Analise de Hidrometros")

    col1, col2, col3 = st.columns(3)
    with col1:
        total = len(df[df['NUMERO_HIDROMETRO'].notna()])
        st.metric("Total de Hidrometros", f"{total:,}")
    with col2:
        velhos = (df['IDADE_HIDRO_ANOS'].fillna(0) > IDADE_HIDRO_CRITICA).sum()
        pct = velhos/total*100 if total > 0 else 0
        st.metric(f"Candidatos Substit. (> {IDADE_HIDRO_CRITICA} anos)", f"{velhos:,}", delta=f"{pct:.1f}%")
    with col3:
        media_idade = df['IDADE_HIDRO_ANOS'].mean()
        st.metric("Idade Media (anos)", f"{media_idade:.1f}")

    st.divider()

    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.markdown("**Distribuição por Tipo**")
        tipo_counts = df['TIPO_HIDROMETRO'].value_counts().reset_index()
        tipo_counts.columns = ['Tipo', 'Qtd']
        fig_pie = px.pie(
            tipo_counts, values='Qtd', names='Tipo',
            hole=0.4, template=get_plotly_template(),
            color_discrete_sequence=[COR_INFO, COR_OK, COR_ALERTA, '#9B59B6']
        )
        st.plotly_chart(fig_pie, width='stretch')

    with col_g2:
        st.markdown("**Distribuição por Marca**")
        marca_counts = df['MARCA_HIDROMETRO'].value_counts().reset_index()
        marca_counts.columns = ['Marca', 'Qtd']
        fig_bar = px.bar(
            marca_counts, x='Marca', y='Qtd',
            template=get_plotly_template(),
            color='Qtd', color_continuous_scale='Blues'
        )
        fig_bar.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig_bar, width='stretch')

    col_g3, col_g4 = st.columns(2)
    with col_g3:
        st.markdown("**Distribuição por Classe Metrológica**")
        classe_counts = df['CLASSE_METROLOGICA'].value_counts().reset_index()
        classe_counts.columns = ['Classe', 'Qtd']
        fig_classe = px.bar(
            classe_counts, x='Classe', y='Qtd',
            template=get_plotly_template(),
            color='Qtd', color_continuous_scale='Greens'
        )
        fig_classe.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig_classe, width='stretch')

    with col_g4:
        st.markdown("**Distribuição de Idade dos Hidrômetros**")
        hidro_com_data = df[df['DATA_INSTALACAO_HIDROMETRO'].notna()].copy()
        fig_hist = px.histogram(
            hidro_com_data, x='IDADE_HIDRO_ANOS',
            nbins=30, template=get_plotly_template(),
            color_discrete_sequence=[COR_INFO]
        )
        fig_hist.add_vline(
            x=IDADE_HIDRO_CRITICA, line_dash='dash',
            line_color=COR_ALERTA,
            annotation_text=f"{IDADE_HIDRO_CRITICA} anos (limiar)"
        )
        fig_hist.update_layout(showlegend=False, height=350, xaxis_title="Anos")
        st.plotly_chart(fig_hist, width='stretch')

    st.divider()
    st.markdown(f"**Tabela: Hidrometros Candidatos a Substituicao (> {IDADE_HIDRO_CRITICA} anos)**")

    substituicao = df[df['IDADE_HIDRO_ANOS'] > IDADE_HIDRO_CRITICA].copy()
    substituicao['Receita_Potencial_Submed'] = (
        substituicao['VALOR_TOTAL'].fillna(0) * FATOR_SUBMEDICAO * 12
    )
    sub_table = substituicao[
        ['MATRICULA', 'MARCA_HIDROMETRO', 'TIPO_HIDROMETRO', 'CLASSE_METROLOGICA',
         'IDADE_HIDRO_ANOS', 'VOLUME_FATURADO', 'VALOR_TOTAL', 'Receita_Potencial_Submed']
    ].sort_values('IDADE_HIDRO_ANOS', ascending=False)

    if len(sub_table) > 50:
        page = st.number_input("Pagina", 1, max(1, (len(sub_table) - 1) // 50 + 1), 1, key="meters_page")
        start = (page - 1) * 50
        sub_table_page = sub_table.iloc[start:start + 50]
    else:
        sub_table_page = sub_table
    st.dataframe(sub_table_page, width='stretch', height=400)

    total_receita_submed = sub_table['Receita_Potencial_Submed'].sum()
    st.markdown(f"**Total de hidrometros para substituicao:** {len(sub_table):,}")
    st.markdown(f"**Receita potencial por submedição (15% x 12m):** {format_currency(total_receita_submed)}")