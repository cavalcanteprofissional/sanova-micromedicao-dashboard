import streamlit as st
import pandas as pd
from dashboard.config import PLOTLY_TEMPLATE, PREMISSAS


def apply_filters(df, categorias, situacoes, marcas):
    mask = (
        (len(categorias) == 0 or df['CATEGORIA_PRINCIPAL'].isin(categorias)) &
        (len(situacoes) == 0 or df['SIT._LIG_AGUA'].isin(situacoes)) &
        (len(marcas) == 0 or df['MARCA_HIDROMETRO'].isin(marcas) | df['MARCA_HIDROMETRO'].isnull())
    )
    return df[mask].copy()


def format_currency(valor: float) -> str:
    return f"R$ {valor:,.2f}"


def format_number(valor: float, decimais: int = 0) -> str:
    if decimais == 0:
        return f"{valor:,.0f}"
    return f"{valor:,.{decimais}f}"


def get_plotly_template():
    return PLOTLY_TEMPLATE


def render_methodology_expander():
    with st.expander("📋 Premissas e Metodologia", expanded=False):
        st.markdown(PREMISSAS)