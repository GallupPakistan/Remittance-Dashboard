"""
metrics.py
Central calculation module for derived figures (growth rates, shares, rankings, YTD).
Strictly adheres to data integrity:
- Never edits or overrides raw data.
- Level rules prevent double-counting parents and children.
- Corridor rankings use only un-aggregated primary sovereign sources.
"""

import os
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROCESSED_DIR = os.path.join(BASE_DIR, 'data', 'processed')

CORRIDOR_ENTITIES = [
    'usa', 'uk', 'saudi_arabia', 'uae',
    'bahrain', 'kuwait', 'qatar', 'oman',
    'germany', 'france', 'netherlands', 'spain', 'italy',
    'greece', 'sweden', 'denmark', 'ireland', 'belgium',
    'norway', 'switzerland', 'australia', 'canada', 'japan',
    'malaysia', 'south_africa', 'south_korea'
]

def load_clean_data():
    df_m = pd.read_parquet(os.path.join(PROCESSED_DIR, 'remittances_long.parquet'))
    df_fy = pd.read_parquet(os.path.join(PROCESSED_DIR, 'fy_reported.parquet'))
    df_ent = pd.read_parquet(os.path.join(PROCESSED_DIR, 'entities.parquet'))
    return df_m, df_fy, df_ent

def get_executive_kpis():
    """
    Computes Page 1 KPI cards:
    1. Latest completed fiscal year (FY26) total & YoY growth vs FY25.
    2. Latest available month (Sep 2026) total & YoY comparison.
    3. Top source country in the latest year and its share.
    4. YTD FY27 tracker vs same months of FY26.
    """
    df_m, df_fy, df_ent = load_clean_data()
    
    # 1. Latest completed FY total (FY26)
    fy26_cash = df_fy[(df_fy['fiscal_year'] == 2026) & (df_fy['entity_id'] == 'total_cash')]
    fy25_cash = df_fy[(df_fy['fiscal_year'] == 2025) & (df_fy['entity_id'] == 'total_cash')]
    
    fy26_val = fy26_cash['value_musd'].iloc[0] if not fy26_cash.empty else 0.0
    fy25_val = fy25_cash['value_musd'].iloc[0] if not fy25_cash.empty else 0.0
    fy_growth_pct = ((fy26_val - fy25_val) / fy25_val * 100.0) if fy25_val > 0 else 0.0
    
    # 2. Latest available month
    latest_month = df_m['month_start'].max()
    prev_year_month = latest_month - pd.DateOffset(years=1)
    
    m_latest_cash = df_m[(df_m['month_start'] == latest_month) & (df_m['entity_id'] == 'total_cash')]
    m_prev_cash = df_m[(df_m['month_start'] == prev_year_month) & (df_m['entity_id'] == 'total_cash')]
    
    m_latest_val = m_latest_cash['value_musd'].iloc[0] if not m_latest_cash.empty else 0.0
    m_prev_val = m_prev_cash['value_musd'].iloc[0] if not m_prev_cash.empty else 0.0
    m_growth_pct = ((m_latest_val - m_prev_val) / m_prev_val * 100.0) if m_prev_val > 0 else 0.0
    is_latest_revised = bool(m_latest_cash['is_revised'].iloc[0]) if not m_latest_cash.empty else False
    
    # 3. Top source corridor in FY26
    fy26_corridors = df_fy[(df_fy['fiscal_year'] == 2026) & (df_fy['entity_id'].isin(CORRIDOR_ENTITIES))].copy()
    fy26_corridors = fy26_corridors.merge(df_ent[['entity_id', 'display_name']], on='entity_id', how='left')
    top_corridor = fy26_corridors.sort_values('value_musd', ascending=False).iloc[0]
    top_share_pct = (top_corridor['value_musd'] / fy26_val * 100.0) if fy26_val > 0 else 0.0
    
    # 4. YTD FY27 vs same period FY26
    fy27_months = df_m[df_m['fiscal_year'] == 2027]['month_of_fy'].unique()
    ytd_fy27 = df_m[(df_m['fiscal_year'] == 2027) & (df_m['entity_id'] == 'total_cash')]['value_musd'].sum()
    ytd_fy26_same = df_m[(df_m['fiscal_year'] == 2026) & (df_m['entity_id'] == 'total_cash') & (df_m['month_of_fy'].isin(fy27_months))]['value_musd'].sum()
    ytd_growth_pct = ((ytd_fy27 - ytd_fy26_same) / ytd_fy26_same * 100.0) if ytd_fy26_same > 0 else 0.0
    
    return {
        'fy26_val_bn': fy26_val / 1000.0,
        'fy26_val_raw': fy26_val,
        'fy_growth_pct': fy_growth_pct,
        'latest_month_date': latest_month,
        'latest_month_str': latest_month.strftime('%b %Y'),
        'latest_month_val_m': m_latest_val,
        'latest_month_val_bn': m_latest_val / 1000.0,
        'm_growth_pct': m_growth_pct,
        'is_latest_revised': is_latest_revised,
        'top_corridor_name': top_corridor['display_name'],
        'top_corridor_val_bn': top_corridor['value_musd'] / 1000.0,
        'top_corridor_share': top_share_pct,
        'ytd_fy27_bn': ytd_fy27 / 1000.0,
        'ytd_fy26_same_bn': ytd_fy26_same / 1000.0,
        'ytd_growth_pct': ytd_growth_pct,
        'ytd_months_count': len(fy27_months)
    }

def get_annual_trend_data():
    """
    Returns annual fiscal-year cash remittances with YoY growth rate.
    """
    _, df_fy, _ = load_clean_data()
    cash_fy = df_fy[df_fy['entity_id'] == 'total_cash'].sort_values('fiscal_year').copy()
    cash_fy['value_bn'] = cash_fy['value_musd'] / 1000.0
    cash_fy['growth_pct'] = cash_fy['value_musd'].pct_change() * 100.0
    return cash_fy

def get_corridor_rankings(fiscal_year=2026):
    """
    Returns corridor rankings for a given fiscal year without double counting.
    """
    df_m, df_fy, df_ent = load_clean_data()
    sub = df_fy[(df_fy['fiscal_year'] == fiscal_year) & (df_fy['entity_id'].isin(CORRIDOR_ENTITIES))].copy()
    sub = sub.merge(df_ent[['entity_id', 'display_name', 'region_group']], on='entity_id', how='left')
    
    total_cash_row = df_fy[(df_fy['fiscal_year'] == fiscal_year) & (df_fy['entity_id'] == 'total_cash')]
    total_cash = total_cash_row['value_musd'].iloc[0] if not total_cash_row.empty else sub['value_musd'].sum()
    
    sub['share_pct'] = (sub['value_musd'] / total_cash) * 100.0
    sub['value_bn'] = sub['value_musd'] / 1000.0
    sub = sub.sort_values('value_musd', ascending=False).reset_index(drop=True)
    sub['rank'] = range(1, len(sub) + 1)
    return sub

def get_regional_summary(fiscal_year=2026):
    """
    Aggregates remittances into key geographic regions (Gulf, Europe, North America, Asia-Pacific, Africa, Other).
    """
    df_m, df_fy, df_ent = load_clean_data()
    # Merge corridor rows with region groups
    sub = df_fy[(df_fy['fiscal_year'] == fiscal_year) & (df_fy['entity_id'].isin(CORRIDOR_ENTITIES + ['other_countries']))].copy()
    sub = sub.merge(df_ent[['entity_id', 'region_group']], on='entity_id', how='left')
    reg = sub.groupby('region_group')['value_musd'].sum().reset_index()
    
    total_cash_row = df_fy[(df_fy['fiscal_year'] == fiscal_year) & (df_fy['entity_id'] == 'total_cash')]
    total_cash = total_cash_row['value_musd'].iloc[0] if not total_cash_row.empty else reg['value_musd'].sum()
    
    reg['share_pct'] = (reg['value_musd'] / total_cash) * 100.0
    reg['value_bn'] = reg['value_musd'] / 1000.0
    reg = reg.sort_values('value_musd', ascending=False).reset_index(drop=True)
    return reg

def get_uae_detail(fiscal_year=2026):
    """
    Returns UAE subcountry breakdown (Dubai, Abu Dhabi, Sharjah, Others).
    """
    df_m, df_fy, df_ent = load_clean_data()
    uae_subs = ['uae_dubai', 'uae_abudhabi', 'uae_sharjah', 'uae_others']
    sub = df_fy[(df_fy['fiscal_year'] == fiscal_year) & (df_fy['entity_id'].isin(uae_subs))].copy()
    sub = sub.merge(df_ent[['entity_id', 'display_name']], on='entity_id', how='left')
    uae_total = sub['value_musd'].sum()
    sub['share_pct'] = (sub['value_musd'] / uae_total * 100.0) if uae_total > 0 else 0.0
    sub['value_bn'] = sub['value_musd'] / 1000.0
    return sub.sort_values('value_musd', ascending=False)
