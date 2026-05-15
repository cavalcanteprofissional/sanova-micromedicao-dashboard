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
        if 'FLAG_INCONSIST_FATURAMENTO' in df.columns:
            inconsist = df['FLAG_INCONSIST_FATURAMENTO'].sum()
            if inconsist > 0:
                matriculas = df[df['FLAG_INCONSIST_FATURAMENTO'] == True]['MATRICULA'].tolist()
                log['warnings'].append(f'Q003: {inconsist} inconsistências em VALOR_TOTAL - MATRÍCULAS: {matriculas}')
                log['inconsistencias_faturamento'] = {
                    'quantidade': int(inconsist),
                    'matriculas': matriculas
                }
        else:
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

    if 'FLAG_FATURADO_MENOR_REAL' in df.columns:
        q004 = df['FLAG_FATURADO_MENOR_REAL'].sum()
        if q004 > 0:
            matriculas = df[df['FLAG_FATURADO_MENOR_REAL'] == True]['MATRICULA'].tolist()
            log['warnings'].append(f'Q004: {q004} casos de VOLUME_FATURADO < VOLUME_REAL - MATRÍCULAS: {matriculas}')
            log['q004_faturado_menor_real'] = {'quantidade': int(q004), 'matriculas': matriculas}

    if 'FLAG_VOLUME_NEGATIVO' in df.columns or 'FLAG_VALOR_NEGATIVO' in df.columns:
        vol_neg = int(df.get('FLAG_VOLUME_NEGATIVO', pd.Series([False]*len(df))).sum())
        val_neg = int(df.get('FLAG_VALOR_NEGATIVO', pd.Series([False]*len(df))).sum())
        q006_total = vol_neg + val_neg
        if q006_total > 0:
            cols_neg = []
            for col in df.columns:
                if col.startswith('FLAG_') and col.endswith('_NEGATIVO') and df[col].any():
                    cols_neg.append(col.replace('FLAG_', '').replace('_NEGATIVO', ''))
            log['warnings'].append(f'Q006: {q006_total} valores negativos detectados - Campos: {cols_neg}')
            log['q006_valores_negativos'] = {'quantidade': q006_total, 'campos': cols_neg}

    if 'FLAG_ATIVA_SEM_RECEITA' in df.columns:
        q007 = df['FLAG_ATIVA_SEM_RECEITA'].sum()
        if q007 > 0:
            log['warnings'].append(f'Q007: {q007} ligações ativas sem receita')
            log['q007_ativa_sem_receita'] = {'quantidade': int(q007)}

    if 'FLAG_SEM_CATEGORIA' in df.columns:
        q008 = df['FLAG_SEM_CATEGORIA'].sum()
        if q008 > 0:
            matriculas = df[df['FLAG_SEM_CATEGORIA'] == True]['MATRICULA'].tolist()
            log['warnings'].append(f'Q008: {q008} registros sem categoria - MATRÍCULAS: {matriculas}')
            log['q008_sem_categoria'] = {'quantidade': int(q008), 'matriculas': matriculas}

    if 'FLAG_DATA_INVALIDA' in df.columns:
        q009 = df['FLAG_DATA_INVALIDA'].sum()
        if q009 > 0:
            log['warnings'].append(f'Q009: {q009} datas de instalação inválidas')
            log['q009_data_invalida'] = {'quantidade': int(q009)}

    if 'FLAG_ZERO_ECONOMIAS' in df.columns:
        q010 = df['FLAG_ZERO_ECONOMIAS'].sum()
        if q010 > 0:
            log['warnings'].append(f'Q010: {q010} ligações ativas com zero economias')
            log['q010_zero_economias'] = {'quantidade': int(q010)}

    if 'FLAG_REAL_MAIOR_LIDO' in df.columns:
        q012 = df['FLAG_REAL_MAIOR_LIDO'].sum()
        if q012 > 0:
            matriculas = df[df['FLAG_REAL_MAIOR_LIDO'] == True]['MATRICULA'].tolist()
            log['warnings'].append(f'Q012: {q012} casos de VOLUME_REAL > VOLUME_LIDO - MATRÍCULAS: {matriculas}')
            log['q012_real_maior_lido'] = {'quantidade': int(q012), 'matriculas': matriculas}

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