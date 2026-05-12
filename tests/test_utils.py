import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestUtilsFunctions:
    def test_format_currency(self):
        from dashboard.utils import format_currency
        assert format_currency(1234.56) == 'R$ 1,234.56'
        assert format_currency(0) == 'R$ 0.00'
        assert format_currency(1000000) == 'R$ 1,000,000.00'

    def test_format_number(self):
        from dashboard.utils import format_number
        assert format_number(999.9, 0) == '1,000'
        assert format_number(999.9, 2) == '999.90'

    def test_apply_filters_all_filters(self):
        from dashboard.load_data import load_data
        from dashboard.utils import apply_filters
        DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'micromedicao_tratado.csv')
        df = load_data(DATA_FILE)
        cats = ['RESIDENCIAL', 'COMERCIAL']
        situacoes = ['ATIVA']
        marcas = ['MARCA A']
        filtered = apply_filters(df, cats, situacoes, marcas)
        assert filtered['CATEGORIA_PRINCIPAL'].isin(cats).all()

    def test_apply_filters_empty_filters_returns_all(self):
        from dashboard.load_data import load_data
        from dashboard.utils import apply_filters
        DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'micromedicao_tratado.csv')
        df = load_data(DATA_FILE)
        filtered = apply_filters(df, df['CATEGORIA_PRINCIPAL'].unique().tolist(),
                                 df['SIT._LIG_AGUA'].unique().tolist(),
                                 df['MARCA_HIDROMETRO'].dropna().unique().tolist())
        assert len(filtered) == len(df)