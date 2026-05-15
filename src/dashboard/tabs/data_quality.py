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

    st.markdown("### KPIs de Qualidade")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        iqd = qm['iqd']
        cor_iqd = "normal" if iqd >= 90 else ("off" if iqd >= 70 else "inverse")
        label_iqd = "Excelente" if iqd >= 90 else ("Atenção" if iqd >= 70 else "Crítico")
        st.metric("📋 IQD", f"{iqd}%", delta=label_iqd, delta_color=cor_iqd)
    with col2:
        st.metric("✅ Completos", f"{qm['registros_completos']:,}", delta_color="off")
    with col3:
        incompletos = qm['dados_incompletos']
        pct_incomp = incompletos / qm['total_registros'] * 100
        cor_incomp = "inverse" if pct_incomp > 10 else "normal"
        st.metric("⚠️ Incompletos", f"{incompletos:,}", delta=f"{pct_incomp:.1f}%", delta_color=cor_incomp)
    with col4:
        receita_perdida_missing = qm['dados_incompletos'] * TARIFA_MINIMA
        st.metric("💸 Perda (Missing)", format_currency(receita_perdida_missing), delta_color="inverse")

    st.markdown("### KPIs de Inconsistências")
    col5, col6, col7, col8 = st.columns(4)
    with col5:
        inconsist_fat = df.get('FLAG_INCONSIST_FATURAMENTO', pd.Series([False]*len(df))).sum()
        st.metric("Q003 Faturamento", f"{int(inconsist_fat)}", delta="Inconsistente" if inconsist_fat > 0 else "OK", delta_color="inverse")
    with col6:
        q004 = df.get('FLAG_FATURADO_MENOR_REAL', pd.Series([False]*len(df))).sum()
        st.metric("Q004 Fat < Real", f"{int(q004)}", delta="Erro" if q004 > 0 else "OK", delta_color="inverse")
    with col7:
        vol_neg = df.get('FLAG_VOLUME_NEGATIVO', pd.Series([False]*len(df))).sum()
        val_neg = df.get('FLAG_VALOR_NEGATIVO', pd.Series([False]*len(df))).sum()
        q006 = vol_neg + val_neg
        st.metric("Q006 Negativos", f"{int(q006)}", delta="Erro" if q006 > 0 else "OK", delta_color="inverse")
    with col8:
        q007 = df.get('FLAG_ATIVA_SEM_RECEITA', pd.Series([False]*len(df))).sum()
        st.metric("Q007 Sem Receita", f"{int(q007)}", delta="Erro" if q007 > 0 else "OK", delta_color="inverse")

    col9, col10, col11, col12 = st.columns(4)
    with col9:
        q008 = df.get('FLAG_SEM_CATEGORIA', pd.Series([False]*len(df))).sum()
        st.metric("Q008 Sem Categoria", f"{int(q008)}", delta="Erro" if q008 > 0 else "OK", delta_color="inverse")
    with col10:
        q009 = df.get('FLAG_DATA_INVALIDA', pd.Series([False]*len(df))).sum()
        st.metric("Q009 Data Inválida", f"{int(q009)}", delta="Erro" if q009 > 0 else "OK", delta_color="inverse")
    with col11:
        q010 = df.get('FLAG_ZERO_ECONOMIAS', pd.Series([False]*len(df))).sum()
        st.metric("Q010 Zero Economias", f"{int(q010)}", delta="Erro" if q010 > 0 else "OK", delta_color="inverse")
    with col12:
        q012 = df.get('FLAG_REAL_MAIOR_LIDO', pd.Series([False]*len(df))).sum()
        st.metric("Q012 Real > Lido", f"{int(q012)}", delta="Erro" if q012 > 0 else "OK", delta_color="inverse")

    st.divider()

    inconsist_fat = df.get('FLAG_INCONSIST_FATURAMENTO', pd.Series([False]*len(df))).sum()
    if inconsist_fat > 0:
        st.markdown("**💰 Inconsistências de Faturamento (VALOR_TOTAL)**")
        st.caption("Registros onde VALOR_TOTAL ≠ soma dos componentes (Água + Esgoto + Serviços + Impostos - Descontos)")

        cols_to_show = ['MATRICULA', 'VALOR_AGUA', 'VALOR_ESGOTO', 'VALOR_SERVICOS',
                        'VALOR_IMPOSTOS', 'VALOR_DESCONTOS', 'VALOR_TOTAL',
                        'VALOR_TOTAL_CALCULADO', 'DIFERENCA_FATURAMENTO']
        existing_cols = [c for c in cols_to_show if c in df.columns]

        fat_inc_df = df[df['FLAG_INCONSIST_FATURAMENTO'] == True][existing_cols].copy()

        col_config = {}
        for col in existing_cols:
            if 'VALOR' in col:
                col_config[col] = st.column_config.NumberColumn(
                    col.replace('VALOR_', '').replace('_', ' '), format="R$ %.2f"
                )

        st.dataframe(fat_inc_df, width='stretch', column_config=col_config, hide_index=True)
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
        st.markdown("**Inconsistências Detectadas (Q001-Q012)**")
        inc_data = []

        if 'DIVERGENCIA_VOL' in df.columns:
            inc_data.append({'Código': 'Q001', 'Tipo': 'MATRÍCULA Duplicada', 'Qtd': int(df.duplicated(subset=['MATRICULA']).sum()), 'Descrição': 'Duplicatas no identificador'})

        date_col = 'DATA_INSTALACAO_HIDROMETRO_DT'
        if date_col in df.columns:
            future = (df[date_col] > pd.Timestamp.today()).sum()
            inc_data.append({'Código': 'Q002', 'Tipo': 'Data Futura', 'Qtd': int(future), 'Descrição': 'Datas de instalação no futuro'})

        q003 = df.get('FLAG_INCONSIST_FATURAMENTO', pd.Series([False]*len(df))).sum()
        inc_data.append({'Código': 'Q003', 'Tipo': 'Inconsist. Faturamento', 'Qtd': int(q003), 'Descrição': 'VALOR_TOTAL ≠ soma componentes'})

        q004 = df.get('FLAG_FATURADO_MENOR_REAL', pd.Series([False]*len(df))).sum()
        inc_data.append({'Código': 'Q004', 'Tipo': 'Fat < Real', 'Qtd': int(q004), 'Descrição': 'VOLUME_FATURADO < VOLUME_REAL'})

        q006 = df.get('FLAG_VOLUME_NEGATIVO', pd.Series([False]*len(df))).sum() + df.get('FLAG_VALOR_NEGATIVO', pd.Series([False]*len(df))).sum()
        inc_data.append({'Código': 'Q006', 'Tipo': 'Valores Negativos', 'Qtd': int(q006), 'Descrição': 'Volumes ou valores negativos'})

        q007 = df.get('FLAG_ATIVA_SEM_RECEITA', pd.Series([False]*len(df))).sum()
        inc_data.append({'Código': 'Q007', 'Tipo': 'Ativa sem Receita', 'Qtd': int(q007), 'Descrição': 'Ligação ativa com valor = 0'})

        q008 = df.get('FLAG_SEM_CATEGORIA', pd.Series([False]*len(df))).sum()
        inc_data.append({'Código': 'Q008', 'Tipo': 'Sem Categoria', 'Qtd': int(q008), 'Descrição': 'Categoria não informada'})

        q009 = df.get('FLAG_DATA_INVALIDA', pd.Series([False]*len(df))).sum()
        inc_data.append({'Código': 'Q009', 'Tipo': 'Data Inválida', 'Qtd': int(q009), 'Descrição': 'Dataausente ou futura'})

        q010 = df.get('FLAG_ZERO_ECONOMIAS', pd.Series([False]*len(df))).sum()
        inc_data.append({'Código': 'Q010', 'Tipo': 'Zero Economias', 'Qtd': int(q010), 'Descrição': 'Ativa com 0 economias'})

        q012 = df.get('FLAG_REAL_MAIOR_LIDO', pd.Series([False]*len(df))).sum()
        inc_data.append({'Código': 'Q012', 'Tipo': 'Real > Lido', 'Qtd': int(q012), 'Descrição': 'VOLUME_REAL > VOLUME_LIDO'})

        inc_data.append({'Código': 'Q005', 'Tipo': 'Outlier Extremo', 'Qtd': int(df.get('FLAG_OUTLIER_EXTREMO', pd.Series([False]*len(df))).sum()), 'Descrição': 'Volume > P99'})

        inc_df = pd.DataFrame(inc_data)
        inc_df = inc_df.sort_values('Qtd', ascending=False)

        def colorize_q(qtd):
            if qtd > 0:
                return 'background-color: #2D1F1F; color: #E74C3C'
            return ''

        styled_inc = inc_df.style.map(colorize_q, subset=['Qtd'])
        st.dataframe(styled_inc, width='stretch', hide_index=True)

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

    q004_df = df[df.get('FLAG_FATURADO_MENOR_REAL', pd.Series([False]*len(df))) == True]
    if len(q004_df) > 0:
        st.divider()
        st.markdown("**Q004: VOLUME_FATURADO < VOLUME_REAL**")
        st.caption("Casos onde o volume faturado é menor que o volume real — erro sistêmico")
        cols_q004 = ['MATRICULA', 'VOLUME_LIDO', 'VOLUME_REAL', 'VOLUME_FATURADO']
        existing_q004 = [c for c in cols_q004 if c in q004_df.columns]
        st.dataframe(q004_df[existing_q004].head(50), width='stretch', hide_index=True)

    q012_df = df[df.get('FLAG_REAL_MAIOR_LIDO', pd.Series([False]*len(df))) == True]
    if len(q012_df) > 0:
        st.divider()
        st.markdown("**Q012: VOLUME_REAL > VOLUME_LIDO**")
        st.caption("Casos onde volume real é maior que volume lido — matematicamente impossível")
        cols_q012 = ['MATRICULA', 'VOLUME_LIDO', 'VOLUME_REAL', 'DIVERGENCIA_VOL']
        existing_q012 = [c for c in cols_q012 if c in q012_df.columns]
        st.dataframe(q012_df[existing_q012].head(50), width='stretch', hide_index=True)

    q007_df = df[df.get('FLAG_ATIVA_SEM_RECEITA', pd.Series([False]*len(df))) == True]
    if len(q007_df) > 0:
        st.divider()
        st.markdown("**Q007: Ligações Ativas sem Receita**")
        st.caption("Ligação ativa com VALOR_TOTAL = 0 — receita perdida garantida")
        cols_q007 = ['MATRICULA', 'CATEGORIA_PRINCIPAL', 'VALOR_TOTAL', 'VOLUME_FATURADO']
        existing_q007 = [c for c in cols_q007 if c in q007_df.columns]
        st.dataframe(q007_df[existing_q007].head(50), width='stretch', hide_index=True)

    q008_df = df[df.get('FLAG_SEM_CATEGORIA', pd.Series([False]*len(df))) == True]
    if len(q008_df) > 0:
        st.divider()
        st.markdown("**Q008: Registros sem Categoria**")
        st.caption("Ligação sem CATEGORIA_PRINCIPAL definida")
        cols_q008 = ['MATRICULA', 'SIT._LIG_AGUA']
        existing_q008 = [c for c in cols_q008 if c in q008_df.columns]
        st.dataframe(q008_df[existing_q008].head(50), width='stretch', hide_index=True)

    st.divider()
    st.markdown("**Top 10 Colunas com Maior Missing**")
    miss_by_col = []
    for col in df.columns:
        miss = df[col].isnull().sum()
        if miss > 0:
            miss_by_col.append({'Coluna': col, 'Missing': int(miss), 'Missing (%)': round(miss / len(df) * 100, 1)})
    miss_by_col = sorted(miss_by_col, key=lambda x: x['Missing'], reverse=True)[:10]
    miss_col_df = pd.DataFrame(miss_by_col)
    
    def colorize_missing(pct):
        if pct > 20:
            return 'background-color: #2D1F1F; color: #E74C3C'
        elif pct > 5:
            return 'background-color: #2D2A1A; color: #F39C12'
        else:
            return ''
    
    styled_missing = miss_col_df.style.map(colorize_missing, subset=['Missing (%)'])
    st.dataframe(styled_missing, width='stretch', hide_index=True)