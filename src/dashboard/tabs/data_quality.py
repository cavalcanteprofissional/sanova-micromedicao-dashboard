import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from dashboard.config import TARIFA_MINIMA, COR_CRITICO, COR_ALERTA, COR_OK, COR_INFO
from dashboard.utils import get_plotly_template, format_currency
from dashboard.load_data import get_month_labels


def render(df, qm=None):
    st.subheader("Qualidade de Dados — Análise de Integridade")

    if qm is None:
        total = len(df)
        complete = (df.notna().all(axis=1)).sum()
        qm = {
            'total_registros': total,
            'registros_completos': int(complete),
            'iqd': round(complete / total * 100, 1),
            'missing_hidrometro': int(df['NUMERO_HIDROMETRO'].isnull().sum()),
            'missing_volume_atual': int(df['VOLUME_LIDO'].isnull().sum()),
            'anomalias_leitura': int(df.get('FLAG_ANOMALIA_LEITURA', pd.Series([False]*len(df))).sum()),
            'outliers_extremos': int(df.get('FLAG_OUTLIER_EXTREMO', pd.Series([False]*len(df))).sum()),
            'dados_incompletos': int(df.get('MESES_DADOS_AUSENTES', pd.Series([0]*len(df)) > 0).sum())
        }

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("IQD - Indice de Qualidade", f"{qm['iqd']}%")
    with col2:
        st.metric("Registros Completos", f"{qm['registros_completos']:,} / {qm['total_registros']:,}")
    with col3:
        st.metric("Registros Incompletos", f"{qm['dados_incompletos']:,}")
    with col4:
        receita_perdida_missing = qm['dados_incompletos'] * TARIFA_MINIMA
        st.metric("Receita Perdida Est. (Missing)", format_currency(receita_perdida_missing))

    st.divider()

    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.markdown("**Evolução do Missing ao Longo do Tempo (VOLUME_LIDO)**")
        meses = [''] + [f'_{i:02d}' for i in range(1, 13)]
        meses_labels = get_month_labels()

        missing_evol = []
        for s, label in zip(meses, meses_labels):
            col = f'VOLUME_LIDO{s}' if s else 'VOLUME_LIDO'
            if col in df.columns:
                miss = df[col].isnull().sum()
                pct = miss / len(df) * 100
                missing_evol.append({'Mes': label, 'Missing (Qtd)': miss, 'Missing (%)': round(pct, 1)})

        miss_df = pd.DataFrame(missing_evol)
        fig_line = px.line(
            miss_df, x='Mes', y='Missing (%)',
            markers=True, template=get_plotly_template(),
            color_discrete_sequence=[COR_CRITICO]
        )
        fig_line.update_layout(height=300, yaxis_title="Missing (%)")
        st.plotly_chart(fig_line, width='stretch')

    with col_g2:
        st.markdown("**Heatmap de Missing por Coluna × Mês**")
        cols_to_check = [
            'VOLUME_LIDO', 'VOLUME_REAL', 'VOLUME_FATURADO',
            'VALOR_AGUA', 'VALOR_ESGOTO', 'VALOR_TOTAL'
        ]
        heat_data = []
        for col in cols_to_check:
            for s, label in zip(meses, meses_labels):
                c = f'{col}{s}' if s else col
                if c in df.columns:
                    miss_pct = df[c].isnull().sum() / len(df) * 100
                    heat_data.append({'Coluna': col, 'Mes': label, 'Missing (%)': round(miss_pct, 1)})

        heat_df = pd.DataFrame(heat_data)
        pivot_heat = heat_df.pivot(index='Coluna', columns='Mes', values='Missing (%)')
        col_order = get_month_labels()
        pivot_heat = pivot_heat.reindex(columns=col_order)

        fig_heat = go.Figure(data=go.Heatmap(
            z=pivot_heat.values,
            x=pivot_heat.columns,
            y=pivot_heat.index,
            colorscale='Reds',
            text=pivot_heat.values,
            texttemplate="%{text:.1f}%",
            hovertemplate='Coluna: %{y}<br>Mês: %{x}<br>Missing: %{z:.1f}%<extra></extra>'
        ))
        fig_heat.update_layout(height=300, template=get_plotly_template())
        st.plotly_chart(fig_heat, width='stretch')

    st.divider()

    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.markdown("**Inconsistencias Detectadas**")
        inc_df = pd.DataFrame([
            {'Tipo': 'LIDO > REAL (>1m³)', 'Qtd': int((df['DIVERGENCIA_VOL'] < -1).sum()) if 'DIVERGENCIA_VOL' in df.columns else 0, 'Descricao': 'Possível fraude/adulteração'},
            {'Tipo': 'Outlier Extremo (>P99)', 'Qtd': int(df['FLAG_OUTLIER_EXTREMO'].sum()) if 'FLAG_OUTLIER_EXTREMO' in df.columns else 0, 'Descricao': 'Volume > 500 m³ ou anômalo'},
            {'Tipo': 'Ligação Ativa sem Hidrômetro', 'Qtd': int(df['FLAG_SEM_HIDROMETRO'].sum()) if 'FLAG_SEM_HIDROMETRO' in df.columns else 0, 'Descricao': 'Medição sem equipamento'},
            {'Tipo': 'Dados Mensais Incompletos', 'Qtd': int((df['MESES_DADOS_AUSENTES'] > 0).sum()) if 'MESES_DADOS_AUSENTES' in df.columns else 0, 'Descricao': 'Meses sem leitura'},
        ])
        st.dataframe(inc_df, width='stretch', hide_index=True)

    with col_t2:
        st.markdown("**Registros por Tipo de Inconsistência**")
        inc_counts = df[
            (df.get('FLAG_ANOMALIA_LEITURA', pd.Series([False]*len(df)))) |
            (df.get('FLAG_OUTLIER_EXTREMO', pd.Series([False]*len(df)))) |
            (df.get('FLAG_SEM_HIDROMETRO', pd.Series([False]*len(df))))
        ].groupby('SIT._LIG_AGUA').size().reset_index(name='Qtd Inconsistencias')
        fig_inc = px.bar(
            inc_counts, x='SIT._LIG_AGUA', y='Qtd Inconsistencias',
            template=get_plotly_template(),
            color='Qtd Inconsistencias', color_continuous_scale='Reds'
        )
        fig_inc.update_layout(showlegend=False, height=300)
        st.plotly_chart(fig_inc, width='stretch')

    st.divider()
    st.markdown("**Top 10 Colunas com Maior Missing**")
    miss_by_col = []
    for col in df.columns:
        miss = df[col].isnull().sum()
        if miss > 0:
            miss_by_col.append({'Coluna': col, 'Missing': int(miss), 'Missing (%)': round(miss / len(df) * 100, 1)})
    miss_by_col = sorted(miss_by_col, key=lambda x: x['Missing'], reverse=True)[:10]
    miss_col_df = pd.DataFrame(miss_by_col)
    st.dataframe(miss_col_df, width='stretch', hide_index=True)