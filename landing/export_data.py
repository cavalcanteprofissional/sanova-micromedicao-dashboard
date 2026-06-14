#!/usr/bin/env python3
"""Export CSV data to landing/data.json for the landing page."""
import json
import re
import pandas as pd
import numpy as np

DATA_CSV = 'data/processed/micromedicao_tratado.csv'
OUTPUT = 'landing/data.json'

df = pd.read_csv(DATA_CSV, low_memory=False)

df['CATEGORIA_PRINCIPAL'] = df['CATEGORIA_PRINCIPAL'].fillna('NÃO INFORMADA')

cat_counts = df['CATEGORIA_PRINCIPAL'].value_counts().to_dict()
sit_counts = df['SIT._LIG_AGUA'].value_counts().to_dict()

def safe_sum(col):
    return round(float(pd.to_numeric(col, errors='coerce').sum()), 2)

def safe_mean(col):
    return round(float(pd.to_numeric(col, errors='coerce').mean()), 2)

def safe_median(col):
    return round(float(pd.to_numeric(col, errors='coerce').median()), 2)

monthly_vol_cols = sorted([c for c in df.columns if re.match(r'VOLUME_LIDO_\d+$', c)])
monthly_volume = [safe_sum(df[c]) for c in monthly_vol_cols]
monthly_volume.append(safe_sum(df['VOLUME_LIDO']))

monthly_val_cols = sorted([c for c in df.columns if re.match(r'VALOR_TOTAL_\d+$', c)])
monthly_billing = [safe_sum(df[c]) for c in monthly_val_cols]
monthly_billing.append(safe_sum(df['VALOR_TOTAL']))

from datetime import date
_MESES_PT = {1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
             7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'}
_REF = date(2026, 5, 1)  # mês atual (ATUAL)
monthly_labels = []
for i in range(12):
    y, m = _REF.year, _REF.month - 12 + i
    while m < 1:
        m += 12
        y -= 1
    monthly_labels.append(f'{_MESES_PT[m]}/{y}')
monthly_labels.append(f'{_MESES_PT[_REF.month]}/{_REF.year}')

flag_data = {}
for c in sorted(df.columns):
    m = re.match(r'FLAG_(.+)$', c)
    if m:
        true_count = int(df[c].sum()) if df[c].dtype in ['int64', 'float64', 'bool'] else int((df[c] == True).sum())
        if true_count > 0:
            flag_data[m.group(1).lower()] = true_count

idade = pd.to_numeric(df['IDADE_HIDRO_ANOS'], errors='coerce')
bins = list(range(0, 11))
labels = [f'{i}-{i+1}' for i in range(10)]
age_groups = pd.cut(idade, bins=bins, labels=labels, right=False)
age_dist = age_groups.value_counts().sort_index().to_dict()

zero_by_cat = {}
for cat in df['CATEGORIA_PRINCIPAL'].unique():
    subset = df[df['CATEGORIA_PRINCIPAL'] == cat]
    vol = pd.to_numeric(subset['VOLUME_LIDO'], errors='coerce')
    zero_by_cat[cat] = {
        'total': len(subset),
        'zero': int((vol == 0).sum()),
        'near_zero': int(((vol > 0) & (vol < 10)).sum()),
    }

if 'NÃO INFORMADA' in zero_by_cat and zero_by_cat['NÃO INFORMADA']['total'] == 0:
    del zero_by_cat['NÃO INFORMADA']

val_total = pd.to_numeric(df['VALOR_TOTAL'], errors='coerce')
vol_lido = pd.to_numeric(df['VOLUME_LIDO'], errors='coerce')

revenue_stats = {
    'total': round(float(val_total.sum()), 2),
    'mean': round(float(val_total.mean()), 2),
    'median': round(float(val_total.median()), 2),
    'std': round(float(val_total.std()), 2),
}

volume_stats = {
    'total': round(float(vol_lido.sum()), 2),
    'mean': round(float(vol_lido.mean()), 2),
    'median': round(float(vol_lido.median()), 2),
    'std': round(float(vol_lido.std()), 2),
}

kpis = {
    'total_connections': len(df),
    'active_connections': int((df['SIT._LIG_AGUA'].str.upper() == 'ATIVA').sum()),
    'total_columns': len(df.columns),
    'months_history': 13,
}

avg = revenue_stats['mean']
recovery = {
    'consumo_zero': round(77 * avg * 0.8, 2),
    'ativas_sem_receita': round(26 * avg, 2),
    'dados_incompletos': round(176 * avg * 0.3, 2),
    'outliers': round(19 * avg * 0.5, 2),
}

hidro_types = {}
if 'TIPO_HIDROMETRO' in df.columns:
    hidro_types = {k.lower(): v for k, v in df['TIPO_HIDROMETRO'].value_counts().to_dict().items()}

output = {
    'kpis': kpis,
    'categories': {k.lower(): v for k, v in cat_counts.items()},
    'situations': {k.lower().replace(' ', '_'): v for k, v in sit_counts.items()},
    'monthly_volume': [int(v) for v in monthly_volume],
    'monthly_billing': monthly_billing,
    'monthly_labels': monthly_labels,
    'flags': flag_data,
    'age_distribution': {str(k): v for k, v in age_dist.items()},
    'zero_consumption_by_category': zero_by_cat,
    'revenue': revenue_stats,
    'volume': volume_stats,
    'recovery_potential': recovery,
    'hydrometer_types': hidro_types,
}

with open(OUTPUT, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f'Exported {OUTPUT} ({len(json.dumps(output))} bytes)')
print(f'  Categories: {len(output["categories"])}')
print(f'  Flags: {len(output["flags"])} active')
print(f'  Monthly points: {len(output["monthly_volume"])} vol, {len(output["monthly_billing"])} billing')
print(f'  Age groups: {len(output["age_distribution"])}')
print(f'  Recovery potential: {len(output["recovery_potential"])} items')
