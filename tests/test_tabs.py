import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestTabs:
    DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'micromedicao_tratado.csv')

    def test_overview_import(self):
        from dashboard.tabs import overview
        assert hasattr(overview, 'render')

    def test_anomalies_import(self):
        from dashboard.tabs import anomalies
        assert hasattr(anomalies, 'render')

    def test_zero_consumption_import(self):
        from dashboard.tabs import zero_consumption
        assert hasattr(zero_consumption, 'render')

    def test_meters_import(self):
        from dashboard.tabs import meters
        assert hasattr(meters, 'render')

    def test_recovery_import(self):
        from dashboard.tabs import recovery
        assert hasattr(recovery, 'render')

    def test_config_values(self):
        from dashboard.config import TARIFA_MINIMA, FATOR_SUBMEDICAO, IDADE_HIDRO_CRITICA
        assert TARIFA_MINIMA == 89.03
        assert FATOR_SUBMEDICAO == 0.15
        assert IDADE_HIDRO_CRITICA == 5

    def test_anomalies_detection(self):
        from dashboard.load_data import load_data
        from dashboard.utils import apply_filters
        df = load_data(self.DATA_FILE)
        filtered = apply_filters(df, df['CATEGORIA_PRINCIPAL'].unique().tolist(),
                                 ['ATIVA'], df['MARCA_HIDROMETRO'].dropna().unique().tolist())
        assert 'FLAG_ANOMALIA_LEITURA' in filtered.columns
        assert 'FLAG_SEM_HIDROMETRO' in filtered.columns

    def test_recovery_data(self):
        from dashboard.load_data import load_data
        df = load_data(self.DATA_FILE)
        assert 'RECEITA_TOTAL_12M' in df.columns
        assert df['RECEITA_TOTAL_12M'].sum() > 0

    def test_meters_data(self):
        from dashboard.load_data import load_data
        df = load_data(self.DATA_FILE)
        assert 'IDADE_HIDRO_ANOS' in df.columns
        assert 'TIPO_HIDROMETRO' in df.columns
        assert 'MARCA_HIDROMETRO' in df.columns
        velhos = df[df['IDADE_HIDRO_ANOS'] > 5]
        assert len(velhos) > 0