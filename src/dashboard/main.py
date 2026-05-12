import streamlit as st
import os
import pandas as pd
from datetime import datetime
from dashboard.load_data import load_data, get_month_labels, get_quality_metrics
from dashboard.utils import apply_filters, render_methodology_expander
from dashboard.tabs import overview, anomalies, zero_consumption, meters, recovery, data_quality

DATA_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed', 'micromedicao_tratado.csv')
DATA_FILE = os.path.abspath(DATA_FILE)


def render_header():
    st.html("""
    <style>
        :root {
            --cor-agua: #2980B9;
            --cor-agua-escuro: #1a5276;
            --cor-sucesso: #27AE60;
            --cor-alerta: #F39C12;
            --cor-critico: #E74C3C;
            --cor-neutro: #95A5A6;
            --bg-card: #1E1E1E;
            --bg-card-hover: #2A2A2A;
            --bg-sidebar: #1A1A2E;
            --bg-sidebar-section: #252540;
            --texto-principal: #E0E0E0;
            --texto-secundario: #9BA0A6;
            --borda: #3A3A4A;
        }
        /* Page background */
        .stApp { background: #0E1117; }
        /* Sidebar */
        section[data-testid="stSidebar"] > div {
            background: var(--bg-sidebar);
        }
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] h4 {
            color: var(--texto-principal);
        }
        /* KPI metric cards */
        div[data-testid="stMetric"] {
            border-left: 4px solid var(--cor-agua);
            padding: 12px 16px;
            background: var(--bg-card);
            border-radius: 6px;
            color: var(--texto-principal);
        }
        div[data-testid="stMetric"] label,
        div[data-testid="stMetric"] [data-testid="stMetricLabel"],
        div[data-testid="stMetric"] [data-testid="stMetricValue"] {
            color: var(--texto-principal) !important;
        }
        div[data-testid="stMetric"].metric-critico {
            border-left-color: var(--cor-critico);
        }
        div[data-testid="stMetric"].metric-alerta {
            border-left-color: var(--cor-alerta);
        }
        div[data-testid="stMetric"].metric-sucesso {
            border-left-color: var(--cor-sucesso);
        }
        /* Headline */
        .page-headline {
            font-size: 2rem !important;
            font-weight: 800 !important;
            color: var(--cor-agua) !important;
            margin-bottom: 4px !important;
            padding: 0 !important;
            line-height: 1.2 !important;
            font-family: inherit !important;
        }
        .page-subtitle {
            font-size: 1rem !important;
            color: var(--texto-secundario) !important;
            margin-bottom: 16px !important;
            font-weight: 400 !important;
            font-family: inherit !important;
        }
        /* Sidebar sections */
        .sidebar-section {
            background: var(--bg-sidebar-section);
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 12px;
            border: 1px solid var(--borda);
            color: var(--texto-principal);
        }
        .sidebar-section-title {
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            color: var(--texto-secundario);
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }
        /* Info badges */
        .info-badge {
            display: inline-block;
            background: var(--cor-agua);
            color: white;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        .info-badge.alerta { background: var(--cor-alerta); }
        .info-badge.critico { background: var(--cor-critico); }
        .info-badge.sucesso { background: var(--cor-sucesso); }
        /* Dividers */
        .divider-custom {
            border: none;
            border-top: 1px solid var(--borda);
            margin: 16px 0;
        }
        /* Tabs */
        button[data-testid="stTab"] { color: var(--texto-secundario); }
        button[data-testid="stTab"]:active,
        button[data-testid="stTab"][aria-selected="true"] {
            color: var(--cor-agua);
        }
        /* Dataframes */
        .stDataFrame tbody { color: var(--texto-principal); }
        .stDataFrame thead th { color: var(--texto-secundario); }
        /* Streamlit expander */
        .streamlit-expander { background: var(--bg-card); border: 1px solid var(--borda); border-radius: 6px; }
        /* Subheaders and body text */
        h1, h2, h3, h4, p, span { color: var(--texto-principal); }
        /* Caption / secondary text */
        .stCaption, [data-testid="stCaption"] {
            color: var(--texto-secundario) !important;
        }
        /* Filter count text */
        .filter-count {
            color: var(--texto-secundario);
            font-size: 0.85rem;
        }
        /* Sidebar checkboxes — full-width pill rows */
        section[data-testid="stSidebar"] [data-testid="stCheckbox"] {
            margin: 3px 0;
        }
        section[data-testid="stSidebar"] [data-testid="stCheckbox"] label {
            display: flex;
            align-items: center;
            background: var(--bg-sidebar-section);
            border: 1px solid var(--borda);
            border-radius: 6px;
            padding: 8px 12px;
            margin: 0;
            font-size: 0.82rem;
            color: var(--texto-secundario);
            cursor: pointer;
            transition: all 0.15s ease;
            gap: 10px;
        }
        section[data-testid="stSidebar"] [data-testid="stCheckbox"] label:hover {
            border-color: var(--cor-agua);
            color: var(--texto-principal);
        }
        section[data-testid="stSidebar"] [data-testid="stCheckbox"] label > div:first-child {
            flex-shrink: 0;
            display: flex;
            align-items: center;
        }
        section[data-testid="stSidebar"] [data-testid="stCheckbox"] label > div:last-child {
            flex: 1;
            color: inherit;
            font-size: inherit;
            font-weight: inherit;
        }
        section[data-testid="stSidebar"] [data-testid="stCheckbox"] input:checked + div:last-child,
        section[data-testid="stSidebar"] [data-testid="stCheckbox"] label:has(input:checked) {
            background: var(--cor-agua);
            border-color: var(--cor-agua);
            color: white;
        }
    </style>
    """)

    st.markdown('<p class="page-headline">Analise Comercial de Micromedicao</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">SANOVA | saneamento inteligente</p>', unsafe_allow_html=True)


def render_sidebar_filters(df, qm):
    with st.sidebar:
        st.markdown("### Filtros Globais")

        with st.expander("📂 Categorias", expanded=False):
            cats_all = df['CATEGORIA_PRINCIPAL'].unique().tolist()
            categorias = []
            for i, cat in enumerate(cats_all):
                if st.checkbox(cat, value=True, key=f'cat_{i}'):
                    categorias.append(cat)

        with st.expander("🔌 Situacao da Ligacao", expanded=False):
            sits_all = df['SIT._LIG_AGUA'].unique().tolist()
            situacoes = []
            for i, sit in enumerate(sits_all):
                if st.checkbox(sit, value=True, key=f'sit_{i}'):
                    situacoes.append(sit)

        with st.expander("🏷️ Marca do Hidrometro", expanded=False):
            marcas_all = df['MARCA_HIDROMETRO'].dropna().unique().tolist()
            marcas = []
            for i, mar in enumerate(marcas_all):
                if st.checkbox(mar, value=True, key=f'mar_{i}'):
                    marcas.append(mar)

        st.markdown("<hr class='divider-custom'>", unsafe_allow_html=True)

        st.markdown("#### Resumo dos Dados")

        iqd_pct = qm['iqd']
        iqd_badge = "sucesso" if iqd_pct >= 90 else ("alerta" if iqd_pct >= 70 else "critico")
        st.markdown(f"""
        <div class="sidebar-section">
            <div class="sidebar-section-title">Qualidade dos Dados</div>
            <div>
                IQD: <span class="info-badge {iqd_badge}">{iqd_pct}%</span>
            </div>
            <div style="margin-top:4px; font-size:0.85rem; color:#7F8C8D;">
                {qm['registros_completos']:,} registros completos de {qm['total_registros']:,}
            </div>
        </div>
        """, unsafe_allow_html=True)

        anom_count = qm['anomalias_leitura'] + qm['outliers_extremos']
        anom_badge = "critico" if anom_count > 50 else ("alerta" if anom_count > 0 else "sucesso")
        st.markdown(f"""
        <div class="sidebar-section">
            <div class="sidebar-section-title">Oportunidades</div>
            <div style="font-size:0.85rem;">
                Casos criticos: <span class="info-badge {anom_badge}">{anom_count}</span>
            </div>
            <div style="font-size:0.85rem; margin-top:4px; color:#7F8C8D;">
                Receita potencial: R$ 2.49M
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<hr class='divider-custom'>", unsafe_allow_html=True)
        st.markdown("#### Opcoes de Visualizacao")

        include_outliers = st.checkbox("Incluir outliers extremos", value=True)
        dados_completos_only = st.checkbox("Apenas dados completos", value=False)

        st.markdown("<hr class='divider-custom'>", unsafe_allow_html=True)
        st.caption(f"Atualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        st.caption(f"Periodo: 13 meses")

        return categorias, situacoes, marcas, include_outliers, dados_completos_only


def main():
    st.set_page_config(
        page_title="Micromedicao | Analise Comercial | SANOVA",
        layout="wide",
        page_icon="💧"
    )

    render_header()

    df = load_data(DATA_FILE)
    qm = get_quality_metrics(df)

    categorias, situacoes, marcas, include_outliers, dados_completos_only = render_sidebar_filters(df, qm)

    if not include_outliers:
        df = df[~df.get('FLAG_OUTLIER_EXTREMO', pd.Series([False]*len(df)))]

    if dados_completos_only:
        df = df[df['MESES_DADOS_AUSENTES'] == 0]

    df_filtered = apply_filters(df, categorias, situacoes, marcas)

    st.markdown(f"""
    <div style="margin-bottom:8px; font-size:0.85rem; color:#7F8C8D;">
        Registros filtrados: <strong>{len(df_filtered):,}</strong> de {len(df):,} total
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Visao Geral",
        "🚨 Anomalias & Fraudes",
        "📉 Consumo Zero",
        "🔧 Hidrometros",
        "💰 Recuperacao de Receita",
        "🔍 Qualidade de Dados"
    ])

    with tab1:
        overview.render(df_filtered, qm)
        render_methodology_expander()

    with tab2:
        anomalies.render(df_filtered)
        render_methodology_expander()

    with tab3:
        zero_consumption.render(df_filtered)
        render_methodology_expander()

    with tab4:
        meters.render(df_filtered)
        render_methodology_expander()

    with tab5:
        recovery.render(df_filtered)
        render_methodology_expander()

    with tab6:
        data_quality.render(df_filtered, qm)
        render_methodology_expander()


if __name__ == "__main__":
    main()