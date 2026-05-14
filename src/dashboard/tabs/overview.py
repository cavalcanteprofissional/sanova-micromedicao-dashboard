import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from dashboard.utils import get_plotly_template
from dashboard.load_data import get_month_labels


def render(df, qm=None):
    ativas = (df['SIT._LIG_AGUA'] == 'ATIVA').sum()
    receita = df[df['SIT._LIG_AGUA'] == 'ATIVA']['VALOR_TOTAL'].sum()
    vol_total = df[df['SIT._LIG_AGUA'] == 'ATIVA']['VOLUME_FATURADO'].sum()
    anomalias = int(
        df.get('FLAG_ANOMALIA_LEITURA', pd.Series([False]*len(df))).sum() +
        df.get('FLAG_CONSUMO_ZERO', pd.Series([False]*len(df))).sum()
    )
    # Casos comerciais = anomalias + consumo zero ativo (diferente da sidebar que tem casos técnicos)

    iqd = qm['iqd'] if qm else 88.4

    st.markdown('<div class="kpi-container">', unsafe_allow_html=True)

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("💧 Ligações Ativas", f"{ativas:,}", delta_color="normal")
    with col2:
        st.metric("💰 Faturamento Mensal", f"R$ {receita:,.2f}", delta_color="normal")
    with col3:
        st.metric("📊 Volume Faturado", f"{vol_total:,.0f} m³", delta_color="off")
    with col4:
        cor_delta = "inverse" if anomalias > 0 else "normal"
        st.metric("🚨 Casos Comerciais", f"{anomalias}", delta="Anomalia + Consumo Zero" if anomalias > 0 else "OK", delta_color=cor_delta)
    with col5:
        cor_iqd = "normal" if iqd >= 90 else ("off" if iqd >= 70 else "inverse")
        label_iqd = "Excelente" if iqd >= 90 else ("Atenção" if iqd >= 70 else "Crítico")
        st.metric("📋 IQD", f"{iqd}%", delta=label_iqd, delta_color=cor_iqd)

    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.markdown("**📊 Distribuição por Categoria**")
        st.caption("_Quantidade de ligações por categoria de uso_")
        cat_counts = df['CATEGORIA_PRINCIPAL'].value_counts().reset_index()
        cat_counts.columns = ['Categoria', 'Quantidade']
        cat_counts = cat_counts.sort_values('Quantidade', ascending=False)
        cores_cat = ['#2980B9', '#1ABC9C', '#95A5A6', '#F39C12'][:len(cat_counts)]
        fig_pie = px.pie(
            cat_counts, values='Quantidade', names='Categoria',
            hole=0.45, template=get_plotly_template(),
            color_discrete_sequence=cores_cat
        )
        fig_pie.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Quantidade: %{value:,}<br>Percentual: %{percent}<extra></extra>'
        )
        fig_pie.update_layout(
            legend=dict(orientation='h', yanchor='bottom', y=-0.15, xanchor='center', x=0.5),
            margin=dict(t=20, b=30),
            font=dict(color='#E0E0E0')
        )
        st.plotly_chart(fig_pie, width='stretch')

    with col_g2:
        st.markdown("**🔌 Distribuição por Situação da Ligação**")
        st.caption("_Status operacional das ligações de água_")
        situacao_counts = df['SIT._LIG_AGUA'].value_counts().reset_index()
        situacao_counts.columns = ['Situacao', 'Quantidade']

        cor_situacao = {
            'ATIVA': '#1ABC9C',
            'CANCELADA': '#95A5A6',
            'CORTADA RAMAL': '#E74C3C',
            'CORTADA CAVALETE': '#E74C3C',
            'CORTADA NA FITA': '#E74C3C',
            'SUPRIMIDA': '#7F8C8D',
            'ELIMINADA': '#7F8C8D',
            'NAO INFORMADA': '#F39C12',
        }
        bar_colors = [cor_situacao.get(s, '#95A5A6') for s in situacao_counts['Situacao']]

        fig_bar = px.bar(
            situacao_counts, y='Situacao', x='Quantidade',
            orientation='h', template=get_plotly_template(),
        )
        fig_bar.update_traces(
            marker_color=bar_colors,
            hovertemplate='<b>%{y}</b><br>Quantidade: %{x:,}<extra></extra>'
        )
        fig_bar.update_layout(
            showlegend=False,
            yaxis={'autorange': 'reversed'},
            margin=dict(t=20),
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
            font=dict(color='#E0E0E0')
        )
        st.plotly_chart(fig_bar, width='stretch')

    st.markdown("**💰 Evolução do Faturamento (13 meses)**")
    st.caption("_Receita mensal faturada ao longo do período_")
    meses = [''] + [f'_{i:02d}' for i in range(1, 13)]
    meses_labels = get_month_labels()

    fat_mensal = []
    for s, label in zip(meses, meses_labels):
        col_name = f'VALOR_TOTAL{s}' if s else 'VALOR_TOTAL'
        val = df[col_name].sum()
        fat_mensal.append({'Mes': label, 'Faturamento': val, 'Indice': len(fat_mensal)})

    fat_df = pd.DataFrame(fat_mensal)
    fig_line = px.area(
        fat_df, x='Mes', y='Faturamento',
        template=get_plotly_template(),
        color_discrete_sequence=['#2980B9']
    )
    fig_line.add_traces(go.Scatter(
        x=fat_df['Mes'], y=fat_df['Faturamento'],
        mode='lines+markers',
        line=dict(color='#1ABC9C', width=2, dash='dot'),
        marker=dict(size=6, color='#1ABC9C'),
        name='Tendência'
    ))
    fig_line.update_layout(
        yaxis_tickprefix='R$ ',
        height=350,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
        legend=dict(orientation='h', yanchor='bottom', y=-0.25, xanchor='center', x=0.5)
    )
    st.plotly_chart(fig_line, width='stretch')

    st.markdown("**🌊 Consumo Médio por Categoria × Mês**")
    st.caption("_Volume faturado médio (m³) por categoria ao longo dos meses. Verde = baixo, Vermelho = alto_")
    cat_mes_data = []
    for cat in df['CATEGORIA_PRINCIPAL'].unique():
        subset = df[df['CATEGORIA_PRINCIPAL'] == cat]
        for s, label in zip(meses, meses_labels):
            col_name = f'VOLUME_FATURADO{s}' if s else 'VOLUME_FATURADO'
            media = subset[col_name].mean()
            cat_mes_data.append({'Categoria': cat, 'Mes': label, 'Media Volume (m3)': round(media, 1)})

    heat_df = pd.DataFrame(cat_mes_data)
    pivot_df = heat_df.pivot(index='Categoria', columns='Mes', values='Media Volume (m3)')
    col_order = get_month_labels()
    pivot_df = pivot_df.reindex(columns=col_order)
    
    z_min = pivot_df.values.min()
    z_max = pivot_df.values.max()
    
    fig_heat = go.Figure(data=go.Heatmap(
        z=pivot_df.values,
        x=pivot_df.columns,
        y=pivot_df.index,
        colorscale='RdYlGn_r',
        zmin=z_min,
        zmax=z_max,
        text=pivot_df.values,
        texttemplate='%{text:.0f}',
        textfont=dict(color='white', size=10),
        hovertemplate='<b>%{y}</b><br>%{x}<br>Média: %{text:.1f} m³<extra></extra>'
    ))
    fig_heat.update_layout(
        height=300,
        template=get_plotly_template(),
        margin=dict(t=20),
        font=dict(color='#E0E0E0')
    )
    st.plotly_chart(fig_heat, width='stretch')