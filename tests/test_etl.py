import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'micromedicao_tratado.csv')


class TestExtractor:
    def test_read_excel(self):
        from etl.extractor import read_excel
        raw_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'micromedicao.xlsx')
        if os.path.exists(raw_path):
            df = read_excel(raw_path)
            assert df is not None
            assert len(df) > 0

    def test_get_column_info(self):
        from etl.extractor import get_column_info
        raw_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'micromedicao.xlsx')
        if os.path.exists(raw_path):
            from etl.extractor import read_excel
            df = read_excel(raw_path)
            info = get_column_info(df)
            assert 'total_rows' in info
            assert 'total_cols' in info


class TestTransformer:
    def test_normalize_text_columns(self):
        from etl.transformer import normalize_text_columns
        import pandas as pd
        df = pd.DataFrame({'SIT._LIG_AGUA': ['Ativa ', 'Cancelada', 'ATIVA']})
        df = normalize_text_columns(df)
        assert df['SIT._LIG_AGUA'].iloc[0] == 'ATIVA'

    def test_fix_capacidade_hidrometro(self):
        from etl.transformer import fix_capacidade_hidrometro
        import pandas as pd
        df = pd.DataFrame({'CAPACIDADE_HIDROMETRO': ['1,6', '1,5', '4,0', None]})
        df = fix_capacidade_hidrometro(df)
        assert df['CAPACIDADE_HIDROMETRO_NUM'].dtype in [float, 'float64']

    def test_handle_missing_cadastral(self):
        from etl.transformer import handle_missing_cadastral
        import pandas as pd
        df = pd.DataFrame({
            'NUMERO_HIDROMETRO': [None, 'ABC123'],
            'TIPO_HIDROMETRO': [None, 'Unijato'],
            'MARCA_HIDROMETRO': [None, 'MARCA A'],
            'CAPACIDADE_HIDROMETRO': [None, '1,6'],
            'DIAMETRO_HIDROMETRO': [None, '3/4"'],
            'CLASSE_METROLOGICA': [None, 'Classe A'],
            'DATA_INSTALACAO_HIDROMETRO': [None, '20/02/2024']
        })
        df = handle_missing_cadastral(df)
        assert df.loc[0, 'TIPO_HIDROMETRO'] == 'SEM_HIDROMETRO'

    def test_transform_runs_without_error(self):
        from etl.transformer import transform
        from etl.extractor import read_excel
        raw_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'micromedicao.xlsx')
        if os.path.exists(raw_path):
            df = read_excel(raw_path)
            df_t = transform(df)
            assert df_t is not None
            assert len(df_t) == len(df)
            assert len(df_t.columns) >= len(df.columns)


class TestLoader:
    def test_validate_output(self):
        from etl.loader import validate_output
        import pandas as pd
        df = pd.DataFrame({'MATRICULA': ['A', 'B', 'C'], 'VALOR_TOTAL': [100, 200, 300]})
        log = validate_output(df)
        assert 'timestamp' in log
        assert 'total_rows' in log
        assert 'errors' in log
        assert 'warnings' in log


class TestPipeline:
    def test_csv_exists(self):
        assert os.path.exists(DATA_FILE), f"CSV nao encontrado: {DATA_FILE}"

    def test_csv_shape(self):
        if os.path.exists(DATA_FILE):
            import pandas as pd
            df = pd.read_csv(DATA_FILE)
            assert df.shape[0] == 1912
            assert df.shape[1] >= 132

    def test_csv_has_new_columns(self):
        if os.path.exists(DATA_FILE):
            import pandas as pd
            df = pd.read_csv(DATA_FILE)
            expected = ['FLAG_SEM_HIDROMETRO', 'FLAG_ANOMALIA_LEITURA', 'FLAG_OUTLIER_EXTREMO',
                       'SCORE_PRIORIDADE', 'RECEITA_TOTAL_12M', 'MESES_DADOS_AUSENTES']
            for col in expected:
                assert col in df.columns, f"Coluna faltante: {col}"

    def test_csv_no_duplicate_matricula(self):
        if os.path.exists(DATA_FILE):
            import pandas as pd
            df = pd.read_csv(DATA_FILE)
            assert not df.duplicated(subset=['MATRICULA']).any()