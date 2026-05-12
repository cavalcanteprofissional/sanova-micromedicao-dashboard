import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from etl.extractor import read_excel, get_column_info
from etl.transformer import transform
from etl.loader import save_to_csv, validate_output


def run_pipeline():
    # src/etl/run_pipeline.py -> project root (3 levels up)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    raw_path = os.path.join(project_root, 'data', 'raw', 'micromedicao.xlsx')
    out_path = os.path.join(project_root, 'data', 'processed', 'micromedicao_tratado.csv')
    log_path = os.path.join(project_root, 'data', 'stage', 'validation_log.json')

    print("=== Pipeline ETL: Excel -> CSV ===")
    print(f"Lendo: {raw_path}")
    df_raw = read_excel(raw_path)
    print(f"  Rows: {len(df_raw)}, Cols: {len(df_raw.columns)}")

    print("\nTransformando dados...")
    df_clean = transform(df_raw)
    print(f"  Shape apos transformacao: {df_clean.shape}")

    print("\nSalvando CSV tratado...")
    save_to_csv(df_clean, out_path)
    print(f"  Salvo em: {out_path}")

    print("\nValidando output...")
    log = validate_output(df_clean, log_path)
    if log['errors']:
        print(f"  ERROS: {log['errors']}")
    if log['warnings']:
        print(f"  AVISOS: {log['warnings']}")
    print(f"  Log salvo em: {log_path}")
    print("Pipeline concluido com sucesso!")

    return df_clean, log


if __name__ == "__main__":
    run_pipeline()