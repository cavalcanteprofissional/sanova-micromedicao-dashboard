import pandas as pd
import numpy as np
import re
import unicodedata
from datetime import datetime


def normalize_text(text: str) -> str:
    if pd.isna(text):
        return text
    text = str(text).strip().upper()
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')
    return text


def normalize_text_columns(df: pd.DataFrame) -> pd.DataFrame:
    text_cols = [
        'SIT._LIG_AGUA', 'SIT._LIG_ESGOTO', 'CATEGORIA_PRINCIPAL',
        'TIPO_HIDROMETRO', 'MARCA_HIDROMETRO', 'CLASSE_METROLOGICA',
        'DIAMETRO_HIDROMETRO'
    ]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].apply(normalize_text)
    return df


def fix_capacidade_hidrometro(df: pd.DataFrame) -> pd.DataFrame:
    if 'CAPACIDADE_HIDROMETRO' in df.columns:
        df['CAPACIDADE_HIDROMETRO_NUM'] = (
            df['CAPACIDADE_HIDROMETRO']
            .astype(str)
            .str.replace(',', '.', regex=False)
            .replace('NAN', np.nan)
            .replace('N/A', np.nan)
            .replace('SEM_HIDROMETRO', np.nan)
        )
        df['CAPACIDADE_HIDROMETRO_NUM'] = pd.to_numeric(
            df['CAPACIDADE_HIDROMETRO_NUM'], errors='coerce'
        )
    return df


def fix_diametro_hidrometro(df: pd.DataFrame) -> pd.DataFrame:
    if 'DIAMETRO_HIDROMETRO' in df.columns:
        df['DIAMETRO_HIDROMETRO'] = (
            df['DIAMETRO_HIDROMETRO']
            .astype(str)
            .str.replace('"', '', regex=False)
            .str.strip()
        )
        diam_map = {
            '3/4': '3/4',
            '1': '1',
            '1 1/2': '1_1/2',
            '2': '2',
            'NAN': 'N/A'
        }
        df['DIAMETRO_HIDROMETRO'] = df['DIAMETRO_HIDROMETRO'].replace(diam_map)
    return df


def convert_dates(df: pd.DataFrame) -> pd.DataFrame:
    if 'DATA_INSTALACAO_HIDROMETRO' in df.columns:
        df['DATA_INSTALACAO_HIDROMETRO_DT'] = pd.to_datetime(
            df['DATA_INSTALACAO_HIDROMETRO'], dayfirst=True, errors='coerce'
        )
    return df


def handle_missing_cadastral(df: pd.DataFrame) -> pd.DataFrame:
    cadastral_cols = [
        'NUMERO_HIDROMETRO', 'TIPO_HIDROMETRO', 'MARCA_HIDROMETRO',
        'CAPACIDADE_HIDROMETRO', 'DIAMETRO_HIDROMETRO',
        'CLASSE_METROLOGICA', 'DATA_INSTALACAO_HIDROMETRO'
    ]
    all_missing_mask = df[cadastral_cols].isnull().all(axis=1)
    df.loc[all_missing_mask, 'TIPO_HIDROMETRO'] = df.loc[all_missing_mask, 'TIPO_HIDROMETRO'].fillna('SEM_HIDROMETRO')
    df.loc[all_missing_mask, 'MARCA_HIDROMETRO'] = df.loc[all_missing_mask, 'MARCA_HIDROMETRO'].fillna('SEM_HIDROMETRO')
    df.loc[all_missing_mask, 'CLASSE_METROLOGICA'] = df.loc[all_missing_mask, 'CLASSE_METROLOGICA'].fillna('N/A')
    df.loc[all_missing_mask, 'DIAMETRO_HIDROMETRO'] = df.loc[all_missing_mask, 'DIAMETRO_HIDROMETRO'].fillna('N/A')
    return df


def handle_missing_economias(df: pd.DataFrame) -> pd.DataFrame:
    econ_cols = [
        'NUMERO_ECONOMIAS_RES', 'NUMERO_ECONOMIAS_COM',
        'NUMERO_ECONOMIAS_IND', 'NUMERO_ECONOMIAS_PUB'
    ]
    for col in econ_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df


def convert_numeric_monthly(df: pd.DataFrame) -> pd.DataFrame:
    meses = [''] + [f'_{i:02d}' for i in range(1, 13)]
    numeric_prefixes = ['VOLUME_', 'VALOR_']
    for prefix in numeric_prefixes:
        for s in meses:
            col = f'{prefix}LIDO{s}' if 'VOLUME' in prefix else f'{prefix}AGUA{s}' if 'AGUA' in prefix else None
            if col and col in df.columns:
                pass
        if prefix == 'VOLUME_':
            for s in meses:
                for suf in ['LIDO', 'REAL', 'FATURADO']:
                    col = f'VOLUME_{suf}{s}' if s else f'VOLUME_{suf}'
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
        elif prefix == 'VALOR_':
            for s in meses:
                for suf in ['AGUA', 'ESGOTO', 'SERVICOS', 'IMPOSTOS', 'DESCONTOS', 'TOTAL']:
                    col = f'VALOR_{suf}{s}' if s else f'VALOR_{suf}'
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
    return df


def enrich_with_calculated_fields(df: pd.DataFrame) -> pd.DataFrame:
    meses = [''] + [f'_{i:02d}' for i in range(1, 13)]

    if 'DATA_INSTALACAO_HIDROMETRO_DT' in df.columns:
        df['IDADE_HIDRO_ANOS'] = (
            pd.Timestamp.today() - df['DATA_INSTALACAO_HIDROMETRO_DT']
        ).dt.days / 365.25

    df['RECEITA_TOTAL_12M'] = sum(
        df[f'VALOR_TOTAL{s}'].fillna(0) for s in meses
    )
    df['VOLUME_TOTAL_12M'] = sum(
        df[f'VOLUME_FATURADO{s}'].fillna(0) for s in meses
    )

    vol_lido_cols = ['VOLUME_LIDO'] + [f'VOLUME_LIDO_{i:02d}' for i in range(1, 13)]
    df['MESES_DADOS_AUSENTES'] = df[vol_lido_cols].isnull().sum(axis=1)
    df['MESES_CONSUMO_ZERO'] = (df[vol_lido_cols].fillna(0) == 0).sum(axis=1)

    if 'VOLUME_LIDO' in df.columns and 'VOLUME_REAL' in df.columns:
        df['DIVERGENCIA_VOL'] = df['VOLUME_REAL'].fillna(0) - df['VOLUME_LIDO'].fillna(0)
        df['FLAG_ANOMALIA_LEITURA'] = df['DIVERGENCIA_VOL'] < -1
    else:
        df['DIVERGENCIA_VOL'] = 0
        df['FLAG_ANOMALIA_LEITURA'] = False

    df['FLAG_SEM_HIDROMETRO'] = (
        df['SIT._LIG_AGUA'] == 'ATIVA'
    ) & (df['NUMERO_HIDROMETRO'].isnull())

    df['FLAG_CONSUMO_ZERO'] = (
        (df['VOLUME_LIDO'].fillna(0) == 0) & (df['SIT._LIG_AGUA'] == 'ATIVA')
    )

    vol_cols_12m = ['VOLUME_LIDO'] + [f'VOLUME_LIDO_{i:02d}' for i in range(1, 13)]
    df['MEDIA_VOL_12M'] = df[vol_cols_12m].mean(axis=1)
    df['STD_VOL_12M'] = df[vol_cols_12m].std(axis=1)
    q99 = df['VOLUME_LIDO'].quantile(0.99)
    df['FLAG_OUTLIER_EXTREMO'] = df['VOLUME_LIDO'] > q99

    df['FLAG_DADOS_INCOMPLETOS'] = df['MESES_DADOS_AUSENTES'] > 0

    df['SCORE_PRIORIDADE'] = (
        df['FLAG_ANOMALIA_LEITURA'].astype(int) * 50 +
        df['FLAG_CONSUMO_ZERO'].astype(int) * 30 +
        (df['MESES_CONSUMO_ZERO'] >= 3).astype(int) * 20 +
        (df['IDADE_HIDRO_ANOS'].fillna(0) > 5).astype(int) * 10 +
        df['FLAG_SEM_HIDROMETRO'].astype(int) * 40
    )

    df['RECEITA_POTENCIAL_SUBMED'] = (
        df['VALOR_TOTAL'].fillna(0) * 0.15 * 12
    )

    vol_cols_6m = [f'VOLUME_LIDO_{i:02d}' for i in range(1, 7)]
    df['FLAG_CONSUMO_CONSTANTE'] = (
        df[vol_cols_6m].nunique(axis=1) == 1
    ) & (df['VOLUME_LIDO_01'].notna())

    df['FLAG_CONSUMO_IMPLAUSIVEL'] = (
        df['VOLUME_LIDO'] > df['MEDIA_VOL_12M'] + 3 * df['STD_VOL_12M']
    ) & (df['STD_VOL_12M'] > 0)

    return df


def transform(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_text_columns(df)
    df = fix_capacidade_hidrometro(df)
    df = fix_diametro_hidrometro(df)
    df = convert_dates(df)
    df = handle_missing_cadastral(df)
    df = handle_missing_economias(df)
    df = convert_numeric_monthly(df)
    df = enrich_with_calculated_fields(df)
    return df