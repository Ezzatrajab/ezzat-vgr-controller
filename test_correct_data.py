"""
Test att verifiera att korrekt data läses från P&L och KPIer
"""
import pandas as pd

def load_rehab_intakter_from_pl(enhet_kst, manad_str):
    """
    Läser Revenue Total från P&L Actual och P&L Budget filer.
    """
    try:
        year, month = manad_str.split('-')
        manad_num = int(year) * 100 + int(month)

        base_path = r'C:\Users\ezzat.rajab.AD\claude-workspace\VGR Alla enheter'

        # Läs P&L Actual
        df_actual = pd.read_excel(f'{base_path}\\{enhet_kst}\\P&L Actual.xlsx')
        # Läs P&L Budget
        df_budget = pd.read_excel(f'{base_path}\\{enhet_kst}\\P&L Budget.xlsx')

        # Hitta rad för Revenue Total
        revenue_row_actual = df_actual[(df_actual['CG Item'] == 'Revenue') & (df_actual['Unnamed: 3'].isna())]
        revenue_row_budget = df_budget[(df_budget['CG Item'] == 'Revenue') & (df_budget['Unnamed: 3'].isna())]

        if revenue_row_actual.empty or revenue_row_budget.empty:
            return {'actual': 0, 'budget': 0}

        revenue_row_actual = revenue_row_actual.iloc[0]
        revenue_row_budget = revenue_row_budget.iloc[0]

        # Hitta rätt kolumn
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
    """Läser KPI-data från KPIer Storg-GBG.xlsx"""
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

        # Rehab Poäng
        rehab_poang = {}
        for row_idx in range(293, 301):
            row_data = df.iloc[row_idx, :].tolist()
            enhet_kst = str(int(row_data[1])) if pd.notna(row_data[1]) else None

            if enhet_kst:
                rehab_poang[enhet_kst] = {}
                for col_idx, manad in col_to_month.items():
                    val = row_data[col_idx] if col_idx < len(row_data) else None
                    rehab_poang[enhet_kst][manad] = float(val) if pd.notna(val) else 0

        # TeamBesök
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


# TEST
print("="*60)
print("TEST: Frölunda Torg Rehab (601)")
print("="*60)

for manad in ['2026-01', '2026-02', '2026-03']:
    print(f"\n{manad}:")

    # P&L Revenue Total
    intakter = load_rehab_intakter_from_pl('601', manad)
    print(f"  Revenue Total Actual: {intakter['actual']:,.2f} kr")
    print(f"  Revenue Total Budget: {intakter['budget']:,.2f} kr")

# KPI data
kpi_data = load_kpi_data()
print("\n" + "="*60)
print("KPI DATA från KPIer Storg-GBG")
print("="*60)

# Rehab Poäng (från VC 102)
print("\nRehab Poäng (från VC 102 - Frölunda Torg):")
for manad in ['2026-01', '2026-02', '2026-03']:
    poang = kpi_data['rehab_poang'].get('102', {}).get(manad, 0)
    print(f"  {manad}: {poang} poäng")

# TeamBesök (601)
print("\nTeamBesök (601 - Frölunda Torg Rehab):")
for manad in ['2026-01', '2026-02', '2026-03']:
    teambesok = kpi_data['teambesok'].get('601', {}).get(manad, 0)
    print(f"  {manad}: {teambesok} besök")

print("\n" + "="*60)
print("FÖRVÄNTAT RESULTAT I DASHBOARD")
print("="*60)
print("\n2026-01:")
print("  Revenue Total: 475,462 kr (actual) vs 667,762 kr (budget)")
print("  Rehab Poäng: 779 poäng")
print("  TeamBesök: 23 besök")
print("\n2026-02:")
print("  Revenue Total: 577,129 kr (actual) vs 649,944 kr (budget)")
print("  Rehab Poäng: 900 poäng")
print("  TeamBesök: 25 besök")
print("\n2026-03:")
print("  Revenue Total: 76,134 kr (actual) vs 660,183 kr (budget)")
print("  Rehab Poäng: 0 (ingen data i KPI-filen)")
print("  TeamBesök: 0 (ingen data i KPI-filen)")
