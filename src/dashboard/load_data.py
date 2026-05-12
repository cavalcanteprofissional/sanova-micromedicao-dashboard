import pandas as pd
import numpy as np
import streamlit as st


@st.cache_data
def load_data(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath, encoding='utf-8')

    df['SIT._LIG_AGUA'] = df['SIT._LIG_AGUA'].replace('', 'NAO INFORMADA')
    df['SIT._LIG_AGUA'] = df['SIT._LIG_AGUA'].fillna('NAO INFORMADA')
    df['CATEGORIA_PRINCIPAL'] = df['CATEGORIA_PRINCIPAL'].fillna('Não Informada')

    if 'DATA_INSTALACAO_HIDROMETRO_DT' in df.columns:
        df['DATA_INSTALACAO_HIDROMETRO_DT'] = pd.to_datetime(
            df['DATA_INSTALACAO_HIDROMETRO_DT'], errors='coerce'
        )
        df['IDADE_HIDRO_ANOS'] = (
            pd.Timestamp.today() - df['DATA_INSTALACAO_HIDROMETRO_DT']
        ).dt.days / 365.25
    elif 'DATA_INSTALACAO_HIDROMETRO' in df.columns:
        df['DATA_INSTALACAO_HIDROMETRO'] = pd.to_datetime(
            df['DATA_INSTALACAO_HIDROMETRO'], dayfirst=True, errors='coerce'
        )
        df['IDADE_HIDRO_ANOS'] = (
            pd.Timestamp.today() - df['DATA_INSTALACAO_HIDROMETRO']
        ).dt.days / 365.25

    meses = [''] + [f'_{i:02d}' for i in range(1, 13)]

    df['RECEITA_TOTAL_12M'] = sum(
        df[f'VALOR_TOTAL{s}'].fillna(0) for s in meses
    )
    df['VOLUME_TOTAL_12M'] = sum(
        df[f'VOLUME_FATURADO{s}'].fillna(0) for s in meses
    )

    df['FLAG_SEM_HIDROMETRO'] = (
        df['NUMERO_HIDROMETRO'].isnull() & (df['SIT._LIG_AGUA'] == 'ATIVA')
    )

    df['FLAG_CONSUMO_ZERO'] = (
        (df['VOLUME_LIDO'].fillna(0) == 0) & (df['SIT._LIG_AGUA'] == 'ATIVA')
    )

    if 'DIVERGENCIA_VOL' not in df.columns:
        df['DIVERGENCIA_VOL'] = df['VOLUME_REAL'].fillna(0) - df['VOLUME_LIDO'].fillna(0)

    if 'FLAG_ANOMALIA_LEITURA' not in df.columns:
        df['FLAG_ANOMALIA_LEITURA'] = df['DIVERGENCIA_VOL'] < -1

    vol_lido_cols = ['VOLUME_LIDO'] + [f'VOLUME_LIDO_{i:02d}' for i in range(1, 13)]

    if 'MESES_CONSUMO_ZERO' not in df.columns:
        df['MESES_CONSUMO_ZERO'] = (df[vol_lido_cols].fillna(0) == 0).sum(axis=1)

    if 'MESES_DADOS_AUSENTES' not in df.columns:
        df['MESES_DADOS_AUSENTES'] = df[vol_lido_cols].isnull().sum(axis=1)

    if 'SCORE_PRIORIDADE' not in df.columns:
        df['SCORE_PRIORIDADE'] = (
            df['FLAG_ANOMALIA_LEITURA'].astype(int) * 50 +
            df['FLAG_CONSUMO_ZERO'].astype(int) * 30 +
            (df['MESES_CONSUMO_ZERO'] >= 3).astype(int) * 20 +
            (df['IDADE_HIDRO_ANOS'].fillna(0) > 5).astype(int) * 10 +
            df['FLAG_SEM_HIDROMETRO'].astype(int) * 40
        )

    vol_cols_12m = ['VOLUME_LIDO'] + [f'VOLUME_LIDO_{i:02d}' for i in range(1, 13)]
    if 'MEDIA_VOL_12M' not in df.columns:
        df['MEDIA_VOL_12M'] = df[vol_cols_12m].mean(axis=1)
    if 'STD_VOL_12M' not in df.columns:
        df['STD_VOL_12M'] = df[vol_cols_12m].std(axis=1)
    if 'FLAG_OUTLIER_EXTREMO' not in df.columns:
        q99 = df['VOLUME_LIDO'].quantile(0.99)
        df['FLAG_OUTLIER_EXTREMO'] = df['VOLUME_LIDO'] > q99

    if 'RECEITA_POTENCIAL_SUBMED' not in df.columns:
        df['RECEITA_POTENCIAL_SUBMED'] = (
            df['VALOR_TOTAL'].fillna(0) * 0.15 * 12
        )

    return df


def get_month_labels() -> list:
    import datetime
    mes_atual = datetime.datetime.now().month
    ano_atual = datetime.datetime.now().year
    labels = ['Mês Atual']
    for i in range(1, 13):
        mes = mes_atual - i
        ano = ano_atual
        if mes <= 0:
            mes += 12
            ano -= 1
        nome = datetime.date(ano, mes, 1).strftime('%b/%y')
        labels.append(f'M-{i} ({nome})')
    return labels


def get_quality_metrics(df: pd.DataFrame) -> dict:
    total = len(df)
    complete = (df.notna().sum(axis=1) == len(df.columns)).sum()
    cadastral_complete = df[['NUMERO_HIDROMETRO', 'TIPO_HIDROMETRO', 'MARCA_HIDROMETRO']].notna().all(axis=1).sum()
    monthly_complete = df[['VOLUME_LIDO', 'VOLUME_REAL', 'VALOR_TOTAL']].notna().all(axis=1).sum()

    return {
        'total_registros': total,
        'registros_completos': int(complete),
        'iqd': round(complete / total * 100, 1),
        'cadastral_complete': int(cadastral_complete),
        'monthly_complete': int(monthly_complete),
        'missing_hidrometro': int(df['NUMERO_HIDROMETRO'].isnull().sum()),
        'missing_volume_atual': int(df['VOLUME_LIDO'].isnull().sum()),
        'anomalias_leitura': int(df['FLAG_ANOMALIA_LEITURA'].sum()) if 'FLAG_ANOMALIA_LEITURA' in df.columns else 0,
        'outliers_extremos': int(df['FLAG_OUTLIER_EXTREMO'].sum()) if 'FLAG_OUTLIER_EXTREMO' in df.columns else 0,
        'dados_incompletos': int((df['MESES_DADOS_AUSENTES'] > 0).sum()) if 'MESES_DADOS_AUSENTES' in df.columns else 0
    }