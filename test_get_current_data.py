"""
Test av get_current_data() funktionen
"""
import pandas as pd

# Kopiera funktionerna från app_cloud.py

def load_rehab_intakter_from_pl(enhet_kst, manad_str):
    """Läser Revenue Total från P&L"""
    try:
        year, month = manad_str.split('-')
        manad_num = int(year) * 100 + int(month)

        base_path = r'C:\Users\ezzat.rajab.AD\claude-workspace\VGR Alla enheter'

        df_actual = pd.read_excel(f'{base_path}\\{enhet_kst}\\P&L Actual.xlsx')
        df_budget = pd.read_excel(f'{base_path}\\{enhet_kst}\\P&L Budget.xlsx')

        revenue_row_actual = df_actual[(df_actual['CG Item'] == 'Revenue') & (df_actual['Unnamed: 3'].isna())]
        revenue_row_budget = df_budget[(df_budget['CG Item'] == 'Revenue') & (df_budget['Unnamed: 3'].isna())]

        if revenue_row_actual.empty or revenue_row_budget.empty:
            return {'actual': 0, 'budget': 0}

        revenue_row_actual = revenue_row_actual.iloc[0]
        revenue_row_budget = revenue_row_budget.iloc[0]

        period_cols = [col for col in df_actual.columns if 'Selected Period' in str(col)]
        header_row = df_actual.iloc[0]

        col_idx = None
        for col in period_cols:
            val = header_row[col]
            if pd.notna(val) and int(val) == manad_num:
                col_idx = col
                break

        if col_idx is None:
            return {'actual': 0, 'budget': 0}

        actual_val = revenue_row_actual[col_idx]
        budget_val = revenue_row_budget[col_idx]

        return {
            'actual': float(actual_val) if pd.notna(actual_val) else 0,
            'budget': float(budget_val) if pd.notna(budget_val) else 0
        }
    except Exception as e:
        print(f"Fel: {e}")
        return {'actual': 0, 'budget': 0}


def load_kpi_data():
    """Läser KPI-data"""
    try:
        kpi_path = r'C:\Users\ezzat.rajab.AD\claude-workspace\VGR Alla enheter\KPIer Storg-GBG.xlsx'
        df = pd.read_excel(kpi_path, sheet_name='Data', header=None)

        rehab_poang_header_idx = 292
        teambesok_header_idx = 304

        header_row = df.iloc[rehab_poang_header_idx, :].tolist()
        col_to_month = {}
        for i, val in enumerate(header_row):
            if pd.notna(val) and str(val).replace('.0', '').isdigit():
                month_num = int(val)
                if month_num >= 202601:
                    year = month_num // 100
                    month = month_num % 100
                    col_to_month[i] = f'{year}-{month:02d}'

        rehab_poang = {}
        for row_idx in range(293, 301):
            row_data = df.iloc[row_idx, :].tolist()
            enhet_kst = str(int(row_data[1])) if pd.notna(row_data[1]) else None

            if enhet_kst:
                rehab_poang[enhet_kst] = {}
                for col_idx, manad in col_to_month.items():
                    val = row_data[col_idx] if col_idx < len(row_data) else None
                    rehab_poang[enhet_kst][manad] = float(val) if pd.notna(val) else 0

        teambesok = {}
        for row_idx in range(305, 313):
            row_data = df.iloc[row_idx, :].tolist()
            enhet_kst = str(int(row_data[1])) if pd.notna(row_data[1]) else None

            if enhet_kst:
                teambesok[enhet_kst] = {}
                for col_idx, manad in col_to_month.items():
                    val = row_data[col_idx] if col_idx < len(row_data) else None
                    teambesok[enhet_kst][manad] = float(val) if pd.notna(val) else 0

        return {'rehab_poang': rehab_poang, 'teambesok': teambesok}
    except Exception as e:
        print(f"Fel: {e}")
        return {'rehab_poang': {}, 'teambesok': {}}


# Simulera ENHETER_DATA
ENHETER_DATA = {
    '601': {
        'månader': {
            '2026-03': {
                'intakter_totalt': {'actual': 0, 'budget': 0},  # Placeholder
                'intakter_3053': {'actual': 0, 'budget': 0},
                'personalkostnad': {'actual': 550000, 'budget': 630000},
                'fte': {'actual': 9.0, 'budget': 10.6},
            }
        }
    }
}


def get_current_data(enhet_kst, manad):
    """Hämtar aktuell data för en enhet och månad"""
    base_data = ENHETER_DATA[enhet_kst]['månader'][manad].copy()

    if enhet_kst in ['601', '602']:
        # Hämta intäkter från P&L
        intakter = load_rehab_intakter_from_pl(enhet_kst, manad)
        base_data['intakter_totalt'] = intakter
        base_data['intakter_3053'] = intakter

        # Hämta KPI-data
        kpi_data = load_kpi_data()

        # Mapping
        rehab_to_vc = {'601': '102', '602': '103'}
        vc_kst = rehab_to_vc.get(enhet_kst)

        # Hämta Rehab-poäng
        if vc_kst and vc_kst in kpi_data.get('rehab_poang', {}):
            base_data['rehab_poang_kpi'] = kpi_data['rehab_poang'][vc_kst].get(manad, 0)
        else:
            base_data['rehab_poang_kpi'] = 0

        # Hämta TeamBesök
        if enhet_kst in kpi_data.get('teambesok', {}):
            base_data['teambesok'] = kpi_data['teambesok'][enhet_kst].get(manad, 0)
        else:
            base_data['teambesok'] = 0

    return base_data


# TEST
print("="*60)
print("TEST: get_current_data() för 601, Mars 2026")
print("="*60)

current_data = get_current_data('601', '2026-03')

print(f"\nIntäkter Total:")
print(f"  Actual: {current_data['intakter_totalt']['actual']:,.2f} kr")
print(f"  Budget: {current_data['intakter_totalt']['budget']:,.2f} kr")

print(f"\nRehab Poäng (från KPI):")
print(f"  {current_data.get('rehab_poang_kpi', 0)} poäng")

print(f"\nTeamBesök (från KPI):")
print(f"  {current_data.get('teambesok', 0)} besök")

print(f"\nPersonal:")
print(f"  FTE: {current_data['fte']['actual']}")
print(f"  Kostnad: {current_data['personalkostnad']['actual']:,} kr")

print("\n" + "="*60)
print("✅ FÖRVÄNTAT: 76,134 kr, 0 poäng, 0 besök")
print("="*60)
