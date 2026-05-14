import streamlit as st
import plotly.express as px
import pandas as pd
from dashboard.config import COR_CRITICO, COR_ALERTA, COR_OK, COR_INFO, COR_NEUTRO
from dashboard.utils import get_plotly_template, format_currency


def render(df):
    st.subheader("Detecção de Anomalias & Fraudes")

    anom_mask = (
        df.get('FLAG_ANOMALIA_LEITURA', pd.Series([False]*len(df))) |
        df.get('FLAG_SEM_HIDROMETRO', pd.Series([False]*len(df))) |
        df.get('FLAG_OUTLIER_EXTREMO', pd.Series([False]*len(df))) |
        df.get('FLAG_CONSUMO_CONSTANTE', pd.Series([False]*len(df))) |
        df.get('FLAG_CONSUMO_IMPLAUSIVEL', pd.Series([False]*len(df)))
    )
    anom_df = df[anom_mask].copy()

    cols_show = [
        'MATRICULA', 'CATEGORIA_PRINCIPAL', 'SIT._LIG_AGUA',
        'VOLUME_LIDO', 'VOLUME_REAL', 'DIVERGENCIA_VOL',
        'MESES_CONSUMO_ZERO', 'SCORE_PRIORIDADE'
    ]
    existing_cols = [c for c in cols_show if c in anom_df.columns]
    anom_df = anom_df.sort_values('SCORE_PRIORIDADE', ascending=False)

    st.markdown(f"**Total de casos detectados: {len(anom_df)}**")

    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.markdown("**Dispersão: Volume Lido × Volume Real**")
        zoom = st.checkbox("Sem outliers (>P95)", value=True, key="scatter_zoom")
        scatter_df = df[df['VOLUME_LIDO'].notna() & df['VOLUME_REAL'].notna()].copy()
        
        scatter_df['DIVERGENCIA'] = scatter_df['VOLUME_LIDO'] - scatter_df['VOLUME_REAL']
        
        if zoom:
            p95 = scatter_df['VOLUME_LIDO'].quantile(0.95)
            scatter_df = scatter_df[scatter_df['VOLUME_LIDO'] <= p95]
        
        fig_scatter = px.scatter(
            scatter_df,
            x='VOLUME_LIDO', y='VOLUME_REAL',
            color='DIVERGENCIA',
            color_continuous_scale='RdYlGn_r',
            template=get_plotly_template(),
            hover_data=['CATEGORIA_PRINCIPAL', 'DIVERGENCIA']
        )
        
        max_val = scatter_df['VOLUME_LIDO'].max() * 1.1 if scatter_df['VOLUME_LIDO'].max() > 0 else 100
        fig_scatter.add_shape(
            type='line', x0=0, y0=0, x1=max_val, y1=max_val,
            line=dict(color='#E74C3C', dash='dash', width=2),
            name='LIDO = REAL'
        )
        
        fig_scatter.update_layout(
            height=350,
            coloraxis_colorbar=dict(title="Divergência"),
            font=dict(color='#E0E0E0')
        )
        st.plotly_chart(fig_scatter, width='stretch')
        if zoom:
            st.caption(f"📌 Linha vermelha: LIDO = REAL. Pontos à esquerda = economia pode estar sendo beneficiada. Mostrando até P95 ({p95:.0f} m³).")

    with col_t2:
        st.markdown("**Contagem por Tipo de Anomalia**")
        tipo_data = {
            'Tipo': [
                'Anomalia de Leitura (LIDO > REAL)',
                'Sem Hidrômetro (Ativa)',
                'Outlier Extremo',
                'Consumo Implausível'
            ],
            'Qtd': [
                int(df.get('FLAG_ANOMALIA_LEITURA', pd.Series([False]*len(df))).sum()),
                int(df.get('FLAG_SEM_HIDROMETRO', pd.Series([False]*len(df))).sum()),
                int(df.get('FLAG_OUTLIER_EXTREMO', pd.Series([False]*len(df))).sum()),
                int(df.get('FLAG_CONSUMO_IMPLAUSIVEL', pd.Series([False]*len(df))).sum())
            ]
        }
        tipo_df = pd.DataFrame(tipo_data)
        tipo_df = tipo_df[tipo_df['Qtd'] > 0]
        tipo_df = tipo_df.sort_values('Qtd', ascending=False)
        
        cores_barra = {
            'Anomalia de Leitura (LIDO > REAL)': '#E74C3C',
            'Sem Hidrômetro (Ativa)': '#E74C3C',
            'Outlier Extremo': '#F39C12',
            'Consumo Implausível': '#E74C3C'
        }
        cores = [cores_barra.get(t, '#95A5A6') for t in tipo_df['Tipo']]

        fig_bar = px.bar(
            tipo_df, x='Tipo', y='Qtd',
            template=get_plotly_template(),
            color='Tipo',
            color_discrete_sequence=cores
        )
        fig_bar.update_traces(hovertemplate='<b>%{x}</b><br>Qtd: %{y:,}<extra></extra>')
        fig_bar.update_layout(
            showlegend=False,
            height=350,
            xaxis=dict(title=""),
            font=dict(color='#E0E0E0')
        )
        st.plotly_chart(fig_bar, width='stretch')

    st.divider()
    st.markdown("**Tabela de Casos Prioritários**")
    display_cols = [c for c in ['MATRICULA', 'CATEGORIA_PRINCIPAL', 'SIT._LIG_AGUA',
                                 'VOLUME_LIDO', 'VOLUME_REAL', 'DIVERGENCIA_VOL',
                                 'FLAG_ANOMALIA_LEITURA', 'FLAG_OUTLIER_EXTREMO', 'SCORE_PRIORIDADE']
                   if c in anom_df.columns]
    table_df = anom_df[display_cols].head(100).copy()
    col_config = {
        "FLAG_ANOMALIA_LEITURA": st.column_config.CheckboxColumn("Anomalia"),
        "FLAG_OUTLIER_EXTREMO": st.column_config.CheckboxColumn("Outlier"),
        "SCORE_PRIORIDADE": st.column_config.NumberColumn("Score", format="%d")
    }
    
    def colorize_score(row):
        score = row.get('SCORE_PRIORIDADE', 0)
        if pd.isna(score):
            return [''] * len(row)
        if score >= 100:
            return ['background-color: #2D1F1F; color: #E74C3C'] * len(row)
        elif score >= 50:
            return ['background-color: #2D2A1A; color: #F39C12'] * len(row)
        else:
            return [''] * len(row)
    
    if len(table_df) > 50:
        page = st.number_input("Página", 1, max(1, (len(table_df) - 1) // 50 + 1), 1, key="anom_page")
        start = (page - 1) * 50
        table_df = table_df.iloc[start:start + 50]
    
    styled_df = table_df.style.map(colorize_score, subset=['SCORE_PRIORIDADE'])
    st.dataframe(styled_df, width='stretch', height=400, column_config=col_config)