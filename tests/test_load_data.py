import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'micromedicao_tratado.csv')


class TestLoadData:
    def test_load_data_returns_dataframe(self):
        from dashboard.load_data import load_data
        df = load_data(DATA_FILE)
        assert df is not None
        assert len(df) > 0

    def test_load_data_shape(self):
        from dashboard.load_data import load_data
        df = load_data(DATA_FILE)
        assert df.shape[0] == 1912
        assert df.shape[1] >= 132

    def test_calculated_columns_exist(self):
        from dashboard.load_data import load_data
        df = load_data(DATA_FILE)
        assert 'RECEITA_TOTAL_12M' in df.columns
        assert 'VOLUME_TOTAL_12M' in df.columns
        assert 'FLAG_SEM_HIDROMETRO' in df.columns
        assert 'FLAG_CONSUMO_ZERO' in df.columns
        assert 'FLAG_ANOMALIA_LEITURA' in df.columns
        assert 'MESES_CONSUMO_ZERO' in df.columns
        assert 'SCORE_PRIORIDADE' in df.columns
        assert 'FLAG_CONSUMO_CONSTANTE' in df.columns
        assert 'FLAG_CONSUMO_IMPLAUSIVEL' in df.columns
        assert 'IDADE_HIDRO_ANOS' in df.columns
        assert 'DIVERGENCIA_VOL' in df.columns

    def test_cache_consistency(self):
        from dashboard.load_data import load_data
        df1 = load_data(DATA_FILE)
        df2 = load_data(DATA_FILE)
        assert df1.equals(df2)

    def test_month_labels(self):
        from dashboard.load_data import get_month_labels
        labels = get_month_labels()
        assert len(labels) == 13
        assert labels[0] == 'Mês Atual'
        assert any('M-1' in l for l in labels)


class TestUtils:
    def test_apply_filters_categoria(self):
        from dashboard.load_data import load_data
        from dashboard.utils import apply_filters
        df = load_data(DATA_FILE)
        filtered = apply_filters(df, ['RESIDENCIAL'], ['ATIVA'], ['MARCA A'])
        assert all(filtered['CATEGORIA_PRINCIPAL'] == 'RESIDENCIAL')

    def test_apply_filters_situacao(self):
        from dashboard.load_data import load_data
        from dashboard.utils import apply_filters
        df = load_data(DATA_FILE)
        filtered = apply_filters(df, df['CATEGORIA_PRINCIPAL'].unique(), ['ATIVA'], df['MARCA_HIDROMETRO'].dropna().unique())
        assert all(filtered['SIT._LIG_AGUA'] == 'ATIVA')

    def test_format_currency(self):
        from dashboard.utils import format_currency
        assert format_currency(1000) == 'R$ 1,000.00'
        assert format_currency(0) == 'R$ 0.00'
        assert format_currency(89.03) == 'R$ 89.03'

    def test_format_number(self):
        from dashboard.utils import format_number
        assert format_number(1000, 0) == '1,000'
        assert format_number(1000.5, 1) == '1,000.5'

    def test_get_plotly_template(self):
        from dashboard.utils import get_plotly_template
        assert get_plotly_template() == 'plotly_dark'