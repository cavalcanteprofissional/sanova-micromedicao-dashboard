import pandas as pd
import os
import json
from datetime import datetime


def save_to_csv(df: pd.DataFrame, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False, encoding='utf-8')


def validate_output(df: pd.DataFrame, log_path: str = None) -> dict:
    log = {
        'timestamp': datetime.now().isoformat(),
        'total_rows': int(len(df)),
        'total_cols': int(len(df.columns)),
        'warnings': [],
        'errors': []
    }

    if df.duplicated(subset=['MATRICULA']).any():
        log['errors'].append('Q001: MATRICULA duplicada encontrada')

    date_col = 'DATA_INSTALACAO_HIDROMETRO_DT'
    if date_col in df.columns:
        future = (df[date_col] > pd.Timestamp.today()).sum()
        if future > 0:
            log['warnings'].append(f'Q002: {future} datas futuras detectadas')

    val_cols = ['VALOR_AGUA', 'VALOR_ESGOTO', 'VALOR_SERVICOS', 'VALOR_IMPOSTOS', 'VALOR_DESCONTOS', 'VALOR_TOTAL']
    if all(c in df.columns for c in val_cols):
        calc = (df['VALOR_AGUA'].fillna(0) + df['VALOR_ESGOTO'].fillna(0) +
                df['VALOR_SERVICOS'].fillna(0) + df['VALOR_IMPOSTOS'].fillna(0) -
                df['VALOR_DESCONTOS'].fillna(0))
        diff = abs(df['VALOR_TOTAL'].fillna(0) - calc)
        inconsist = (diff > 0.01).sum()
        if inconsist > 0:
            log['warnings'].append(f'Q003: {inconsist} inconsistências em VALOR_TOTAL')

    if 'FLAG_OUTLIER_EXTREMO' in df.columns:
        outliers = df['FLAG_OUTLIER_EXTREMO'].sum()
        if outliers > 0:
            log['warnings'].append(f'Q005: {outliers} outliers extremos detectados')

    if 'FLAG_SEM_HIDROMETRO' in df.columns:
        sem_hidro = df['FLAG_SEM_HIDROMETRO'].sum()
        log['metrics'] = {
            'outliers_extremos': int(outliers) if 'FLAG_OUTLIER_EXTREMO' in df.columns else 0,
            'sem_hidrometro': int(sem_hidro),
            'missing_por_coluna': {
                col: int(df[col].isnull().sum())
                for col in df.columns[:20] if df[col].isnull().sum() > 0
            }
        }

    if log_path:
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(log, f, indent=2, ensure_ascii=False)

    return log


def read_csv(path: str) -> pd.DataFrame:
    return pd.read_csv(path, encoding='utf-8')