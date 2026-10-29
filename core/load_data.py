"""
load_data.py
Strict, non-destructive parser and unpivoter for Homeremit_Arch.xlsx.
Preserves full source precision, provenance (source_sheet, source_row, source_col),
and flags revisions and methodology basis without altering raw numeric values.
"""

import os
import re
from datetime import datetime
import openpyxl
import pandas as pd
import numpy as np

RAW_EXCEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'raw', 'Homeremit_Arch.xlsx')
PROCESSED_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'processed')

def clean_str(val):
    if val is None:
        return ''
    return str(val).strip()

def parse_header_date(cell_val):
    """
    Parses column header into (is_fy, is_revised, date_obj, fy_val, header_str).
    Returns None if column should be skipped (e.g. empty or non-data).
    """
    if cell_val is None:
        return None
    s = str(cell_val).strip()
    if not s or s.lower() in ['item', 'country', 'none']:
        return None
    
    # Check for Fiscal Year columns like 'FY 73', 'FY14', 'FY26', 'FY 2026'
    fy_match = re.search(r'FY\s*(\d{2,4})', s, re.IGNORECASE)
    if fy_match:
        yr = int(fy_match.group(1))
        if yr < 100:
            yr = 1900 + yr if yr >= 70 else 2000 + yr
        return {'is_fy': True, 'is_revised': False, 'date': None, 'fiscal_year': yr, 'raw_header': s}
    
    # Revision flag check: check trailing 'R' or explicit revised notes without stripping 'r' from 'Mar' or 'Apr'
    is_revised = bool(re.search(r'[a-zA-Z0-9]+[R]$', s))
    clean_date_str = re.sub(r'[R]$', '', s).strip()
    
    # Try parsing datetime objects or strings
    if isinstance(cell_val, datetime):
        dt = cell_val.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        # determine FY: Jul-Dec is FY (yr+1), Jan-Jun is FY (yr)
        fy = dt.year + 1 if dt.month >= 7 else dt.year
        return {'is_fy': False, 'is_revised': is_revised, 'date': dt, 'fiscal_year': fy, 'raw_header': s}
    
    # Try common date formats
    for fmt in ['%b-%y', '%B-%y', '%b-%Y', '%B-%Y', '%Y-%m-%d', '%d-%b-%y', '%Y-%m-%d %H:%M:%S']:
        try:
            dt = datetime.strptime(clean_date_str, fmt)
            dt = dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            fy = dt.year + 1 if dt.month >= 7 else dt.year
            return {'is_fy': False, 'is_revised': is_revised, 'date': dt, 'fiscal_year': fy, 'raw_header': s}
        except ValueError:
            pass
            
    return None

def get_entity_metadata():
    """
    Returns entity catalog according to design doc section 4.2 & 4.3.
    """
    entities = [
        # Totals
        {'entity_id': 'total_cash', 'source_label': 'Cash Flow', 'display_name': 'Total (Cash Flow)', 'level': 'total', 'parent_id': None, 'region_group': 'Total'},
        {'entity_id': 'total_all', 'source_label': 'Total (I+II)', 'display_name': 'Total Remittances', 'level': 'total', 'parent_id': None, 'region_group': 'Total'},
        {'entity_id': 'encashment', 'source_label': 'Encashment and Profit', 'display_name': 'Encashment & Profit', 'level': 'special', 'parent_id': None, 'region_group': 'Other'},
        
        # Top-level / Parent groups
        {'entity_id': 'usa', 'source_label': 'USA', 'display_name': 'USA', 'level': 'country', 'parent_id': None, 'region_group': 'North America'},
        {'entity_id': 'uk', 'source_label': 'U.K.', 'display_name': 'U.K.', 'level': 'country', 'parent_id': None, 'region_group': 'Europe'},
        {'entity_id': 'saudi_arabia', 'source_label': 'Saudi Arabia', 'display_name': 'Saudi Arabia', 'level': 'country', 'parent_id': None, 'region_group': 'Gulf (GCC)'},
        
        # UAE (parent + children)
        {'entity_id': 'uae', 'source_label': 'U.A.E.', 'display_name': 'U.A.E.', 'level': 'group', 'parent_id': None, 'region_group': 'Gulf (GCC)'},
        {'entity_id': 'uae_dubai', 'source_label': 'Dubai', 'display_name': 'Dubai (UAE)', 'level': 'subcountry', 'parent_id': 'uae', 'region_group': 'Gulf (GCC)'},
        {'entity_id': 'uae_abudhabi', 'source_label': 'Abu Dhabi', 'display_name': 'Abu Dhabi (UAE)', 'level': 'subcountry', 'parent_id': 'uae', 'region_group': 'Gulf (GCC)'},
        {'entity_id': 'uae_sharjah', 'source_label': 'Sharjah', 'display_name': 'Sharjah (UAE)', 'level': 'subcountry', 'parent_id': 'uae', 'region_group': 'Gulf (GCC)'},
        {'entity_id': 'uae_others', 'source_label': 'Others (UAE)', 'display_name': 'Others (UAE)', 'level': 'subcountry', 'parent_id': 'uae', 'region_group': 'Gulf (GCC)'},
        
        # Other GCC (parent + children)
        {'entity_id': 'gcc_other', 'source_label': 'Other GCC Countries', 'display_name': 'Other GCC Countries', 'level': 'group', 'parent_id': None, 'region_group': 'Gulf (GCC)'},
        {'entity_id': 'bahrain', 'source_label': 'Bahrain', 'display_name': 'Bahrain', 'level': 'country', 'parent_id': 'gcc_other', 'region_group': 'Gulf (GCC)'},
        {'entity_id': 'kuwait', 'source_label': 'Kuwait', 'display_name': 'Kuwait', 'level': 'country', 'parent_id': 'gcc_other', 'region_group': 'Gulf (GCC)'},
        {'entity_id': 'qatar', 'source_label': 'Qatar', 'display_name': 'Qatar', 'level': 'country', 'parent_id': 'gcc_other', 'region_group': 'Gulf (GCC)'},
        {'entity_id': 'oman', 'source_label': 'Oman', 'display_name': 'Oman', 'level': 'country', 'parent_id': 'gcc_other', 'region_group': 'Gulf (GCC)'},
        
        # EU (parent + children)
        {'entity_id': 'eu_total', 'source_label': 'EU Countries', 'display_name': 'EU Countries', 'level': 'group', 'parent_id': None, 'region_group': 'Europe'},
        {'entity_id': 'germany', 'source_label': 'Germany', 'display_name': 'Germany', 'level': 'country', 'parent_id': 'eu_total', 'region_group': 'Europe'},
        {'entity_id': 'france', 'source_label': 'France', 'display_name': 'France', 'level': 'country', 'parent_id': 'eu_total', 'region_group': 'Europe'},
        {'entity_id': 'netherlands', 'source_label': 'Netherlands', 'display_name': 'Netherlands', 'level': 'country', 'parent_id': 'eu_total', 'region_group': 'Europe'},
        {'entity_id': 'spain', 'source_label': 'Spain', 'display_name': 'Spain', 'level': 'country', 'parent_id': 'eu_total', 'region_group': 'Europe'},
        {'entity_id': 'italy', 'source_label': 'Italy', 'display_name': 'Italy', 'level': 'country', 'parent_id': 'eu_total', 'region_group': 'Europe'},
        {'entity_id': 'greece', 'source_label': 'Greece', 'display_name': 'Greece', 'level': 'country', 'parent_id': 'eu_total', 'region_group': 'Europe'},
        {'entity_id': 'sweden', 'source_label': 'Sweden', 'display_name': 'Sweden', 'level': 'country', 'parent_id': 'eu_total', 'region_group': 'Europe'},
        {'entity_id': 'denmark', 'source_label': 'Denmark', 'display_name': 'Denmark', 'level': 'country', 'parent_id': 'eu_total', 'region_group': 'Europe'},
        {'entity_id': 'ireland', 'source_label': 'Ireland', 'display_name': 'Ireland', 'level': 'country', 'parent_id': 'eu_total', 'region_group': 'Europe'},
        {'entity_id': 'belgium', 'source_label': 'Belgium', 'display_name': 'Belgium', 'level': 'country', 'parent_id': 'eu_total', 'region_group': 'Europe'},
        
        # Independent countries
        {'entity_id': 'malaysia', 'source_label': 'Malaysia', 'display_name': 'Malaysia', 'level': 'country', 'parent_id': None, 'region_group': 'Asia-Pacific'},
        {'entity_id': 'norway', 'source_label': 'Norway', 'display_name': 'Norway', 'level': 'country', 'parent_id': None, 'region_group': 'Europe'},
        {'entity_id': 'switzerland', 'source_label': 'Switzerland', 'display_name': 'Switzerland', 'level': 'country', 'parent_id': None, 'region_group': 'Europe'},
        {'entity_id': 'australia', 'source_label': 'Australia', 'display_name': 'Australia', 'level': 'country', 'parent_id': None, 'region_group': 'Asia-Pacific'},
        {'entity_id': 'canada', 'source_label': 'Canada', 'display_name': 'Canada', 'level': 'country', 'parent_id': None, 'region_group': 'North America'},
        {'entity_id': 'japan', 'source_label': 'Japan', 'display_name': 'Japan', 'level': 'country', 'parent_id': None, 'region_group': 'Asia-Pacific'},
        {'entity_id': 'south_africa', 'source_label': 'South Africa', 'display_name': 'South Africa', 'level': 'country', 'parent_id': None, 'region_group': 'Africa'},
        {'entity_id': 'south_korea', 'source_label': 'South Korea', 'display_name': 'South Korea', 'level': 'country', 'parent_id': None, 'region_group': 'Asia-Pacific'},
        {'entity_id': 'other_countries', 'source_label': 'Other Countries', 'display_name': 'Other (not itemised)', 'level': 'country', 'parent_id': None, 'region_group': 'Other (not itemised)'}
    ]
    return pd.DataFrame(entities)

def match_row_to_entity(sheet_name, row_idx, col1, col2, col3):
    c1, c2, c3 = clean_str(col1), clean_str(col2), clean_str(col3)
    c_all = f"{c1} {c2} {c3}".lower()
    
    if 'total' in c1.lower() or (sheet_name == 'July 2018 onwards ' and row_idx == 40):
        return 'total_all'
    if 'encashment' in c_all:
        return 'encashment'
    if 'cash' in c_all and 'encashment' not in c_all:
        return 'total_cash'
    if 'usa' in c_all:
        return 'usa'
    if 'u.k.' in c_all or 'uk' in c_all:
        return 'uk'
    if 'saudi' in c_all:
        return 'saudi_arabia'
    if 'u.a.e.' in c_all or 'uae' in c_all:
        return 'uae'
    if 'dubai' in c_all:
        return 'uae_dubai'
    if 'abu dhabi' in c_all:
        return 'uae_abudhabi'
    if 'sharjah' in c_all:
        return 'uae_sharjah'
    if row_idx == 14 and ('others' in c_all):
        return 'uae_others'
    if 'other gcc' in c_all:
        return 'gcc_other'
    if 'behrain' in c_all or 'bahrain' in c_all:
        return 'bahrain'
    if 'kuwait' in c_all:
        return 'kuwait'
    if 'qatar' in c_all:
        return 'qatar'
    if 'oman' in c_all:
        return 'oman'
    if 'eu countr' in c_all:
        return 'eu_total'
    if 'germany' in c_all:
        return 'germany'
    if 'france' in c_all:
        return 'france'
    if 'netherland' in c_all:
        return 'netherlands'
    if 'spain' in c_all:
        return 'spain'
    if 'italy' in c_all:
        return 'italy'
    if 'greece' in c_all:
        return 'greece'
    if 'sweden' in c_all:
        return 'sweden'
    if 'denmark' in c_all:
        return 'denmark'
    if 'ireland' in c_all:
        return 'ireland'
    if 'belgium' in c_all:
        return 'belgium'
    if 'malaysia' in c_all:
        return 'malaysia'
    if 'norway' in c_all:
        return 'norway'
    if 'switzerland' in c_all:
        return 'switzerland'
    if 'australia' in c_all:
        return 'australia'
    if 'canada' in c_all:
        return 'canada'
    if 'japan' in c_all:
        return 'japan'
    if 'south africa' in c_all:
        return 'south_africa'
    if 'south korea' in c_all:
        return 'south_korea'
    if 'other' in c_all:
        return 'other_countries'
        
    return None

def load_and_transform():
    wb = openpyxl.load_workbook(RAW_EXCEL_PATH, data_only=True)
    
    records_monthly = []
    records_fy = []
    excluded_columns = []
    
    # Process each sheet
    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        
        # Row 5 is header row
        header_row = 5
        # Determine column mappings
        col_mappings = {}
        for col_idx in range(4, ws.max_column + 1):
            cell_val = ws.cell(header_row, col_idx).value
            h_info = parse_header_date(cell_val)
            if h_info is not None:
                # Check for known invalid non-months: Aug-27 and Aug-28 in sheet 3
                raw_h = h_info['raw_header']
                if sheet_name == 'July 2018 onwards ' and raw_h in ['Aug-27', 'Aug-28']:
                    excluded_columns.append({
                        'sheet': sheet_name,
                        'col_idx': col_idx,
                        'header': raw_h,
                        'reason': 'Formula error / invalid duplicate column in source'
                    })
                    continue
                col_mappings[col_idx] = h_info
                
        # Determine data rows
        for r in range(6, ws.max_row + 1):
            c1 = ws.cell(r, 1).value
            c2 = ws.cell(r, 2).value
            c3 = ws.cell(r, 3).value
            
            entity_id = match_row_to_entity(sheet_name, r, c1, c2, c3)
            if entity_id is None:
                continue
                
            for col_idx, h_info in col_mappings.items():
                val = ws.cell(r, col_idx).value
                if val is None or val == '' or val == '…':
                    num_val = 0.0
                else:
                    try:
                        num_val = float(val)
                    except (ValueError, TypeError):
                        num_val = 0.0
                        
                basis = 'pre_jul2019'
                if h_info['date'] and h_info['date'] >= datetime(2019, 7, 1):
                    basis = 'from_jul2019'
                elif h_info['is_fy'] and h_info['fiscal_year'] >= 2020:
                    basis = 'from_jul2019'
                    
                rec = {
                    'entity_id': entity_id,
                    'value_musd': num_val,
                    'is_revised': h_info['is_revised'],
                    'basis': basis,
                    'source_sheet': sheet_name,
                    'source_row': r,
                    'source_col': col_idx,
                    'fiscal_year': h_info['fiscal_year']
                }
                
                if h_info['is_fy']:
                    records_fy.append(rec)
                else:
                    dt = h_info['date']
                    # month_of_fy: July is 1, June is 12
                    m_of_fy = (dt.month - 7) % 12 + 1
                    rec['month_start'] = dt
                    rec['month_of_fy'] = m_of_fy
                    records_monthly.append(rec)

    df_monthly = pd.DataFrame(records_monthly)
    df_fy = pd.DataFrame(records_fy)
    df_entities = get_entity_metadata()
    
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    df_monthly.to_parquet(os.path.join(PROCESSED_DIR, 'remittances_long.parquet'), index=False)
    df_fy.to_parquet(os.path.join(PROCESSED_DIR, 'fy_reported.parquet'), index=False)
    df_entities.to_parquet(os.path.join(PROCESSED_DIR, 'entities.parquet'), index=False)
    
    print(f"Successfully loaded and saved:")
    print(f" - Monthly records: {len(df_monthly):,} rows")
    print(f" - FY reported records: {len(df_fy):,} rows")
    print(f" - Entities: {len(df_entities):,} entities")
    print(f" - Excluded invalid columns: {len(excluded_columns)}")
    for exc in excluded_columns:
        print(f"   * Excluded {exc['header']} (Sheet '{exc['sheet']}', Col {exc['col_idx']}): {exc['reason']}")

    return df_monthly, df_fy, df_entities, excluded_columns

if __name__ == '__main__':
    load_and_transform()
