import pandas as pd
import os


def read_excel(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")
    df = pd.read_excel(path, sheet_name=0, dtype=str)
    return df


def get_column_info(df: pd.DataFrame) -> dict:
    info = {
        'total_rows': len(df),
        'total_cols': len(df.columns),
        'cols_with_missing': {},
        'dtypes_summary': df.dtypes.value_counts().to_dict()
    }
    for col in df.columns:
        missing = df[col].isnull().sum()
        if missing > 0:
            info['cols_with_missing'][col] = {
                'missing': int(missing),
                'pct': round(missing / len(df) * 100, 2)
            }
    return info