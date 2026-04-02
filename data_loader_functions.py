"""
Datahämtningsfunktioner för Ezzat's Controlling System
Hämtar RÄTT data från Excel-filer istället för hårdkodad data
"""

import pandas as pd
import os
from datetime import datetime

def get_file_paths(enhet_kst, base_path=None):
    """
    Returnerar sökvägar till alla datafiler för en enhet

    Args:
        enhet_kst: '102', '103', '601', '602' etc
        base_path: Bas-sökväg till data-mappen (om None, använd relativ sökväg)
    """
    if base_path is None:
        # Peka till rätt plats - VGR Alla enheter/Dashboard/data eller VGR Alla enheter/{enhet_kst}
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Testa olika möjliga platser:
        # 1. Dashboard/data/{enhet_kst} (för deployed/cloud version)
        # 2. VGR Alla enheter/{enhet_kst} (parent folder för lokal utveckling)
        # 3. Absolut sökväg till VGR Alla enheter

        if os.path.exists(os.path.join(script_dir, 'data', enhet_kst)):
            base_path = os.path.join(script_dir, 'data')
        else:
            # Kolla om vi är i Dashboard-mappen, då är parent = VGR Alla enheter
            parent_dir = os.path.dirname(script_dir)
            if os.path.exists(os.path.join(parent_dir, enhet_kst)):
                base_path = parent_dir
            else:
                # Absolut sökväg som fallback
                vgr_path = r'C:\Users\ezzat.rajab.AD\claude-workspace\VGR Alla enheter'
                if os.path.exists(os.path.join(vgr_path, enhet_kst)):
                    base_path = vgr_path
                else:
                    base_path = os.path.join(script_dir, 'data')

    enhet_path = os.path.join(base_path, enhet_kst)

    # Olika filnamn för olika enheter
    file_map = {
        '601': {
            'fte_actual': 'FTE Producerande per Yrkesgrupp (7).xlsx',
            'hr_cost': 'HR Cost (12).xlsx',
            'intakt_budget': 'Intäkt Budget Rehab (26).xlsx',
            'pl_actual': 'P&L Actual.xlsx',
            'pl_budget': 'P&L Budget.xlsx'
        },
        '602': {
            'fte_actual': 'FTE Producerande per Yrkesgrupp (8).xlsx',
            'hr_cost': 'HR Cost (13).xlsx',
            'intakt_budget': 'Intäkt Budget Rehab (27).xlsx',
            'pl_actual': 'P&L Actual.xlsx',
            'pl_budget': 'P&L Budget.xlsx'
        },
        '102': {
            'fte_actual': 'FTE Producerande per Yrkesgrupp (4).xlsx',
            'hr_cost': 'HR Cost (10).xlsx',
            'pl_actual': 'P&L Actual.xlsx',
            'pl_budget': 'P&L Budget.xlsx'
        },
        '103': {
            'fte_actual': 'FTE Producerande per Yrkesgrupp (5).xlsx',
            'hr_cost': 'HR Cost (11).xlsx',
            'pl_actual': 'P&L Actual.xlsx',
            'pl_budget': 'P&L Budget.xlsx'
        }
    }

    if enhet_kst not in file_map:
        raise ValueError(f"Enhet {enhet_kst} finns inte i file_map")

    paths = {}
    for key, filename in file_map[enhet_kst].items():
        paths[key] = os.path.join(enhet_path, filename)

    return paths


def load_fte_actual(enhet_kst, manad_str, base_path=None):
    """
    Hämtar actual FTE från "FTE Producerande per Yrkesgrupp"

    Args:
        enhet_kst: '102', '103', '601', '602'
        manad_str: '2026-01', '2026-02' etc
        base_path: Bas-sökväg till data-mappen

    Returns:
        float: Totalt antal FTE för månaden (från Total-kolumnen)
    """
    try:
        paths = get_file_paths(enhet_kst, base_path)
        df = pd.read_excel(paths['fte_actual'])

        # Konvertera månad till period-format (202601)
        year, month = manad_str.split('-')
        period = int(year + month)

        # Första kolumnen heter 'Yrkesgrupp' men innehåller period-nummer
        # Rad 0 innehåller texten "Period", rad 1+ innehåller period-nummer
        for idx, row in df.iterrows():
            if idx == 0:  # Hoppa över header-rad
                continue
            if idx > 20:  # Hoppa över rader efter de första perioderna
                break

            period_val = row['Yrkesgrupp']
            if pd.notna(period_val) and isinstance(period_val, (int, float)) and int(period_val) == period:
                # Returnera Total-kolumnen
                return float(row['Total']) if pd.notna(row['Total']) else 0.0

        return 0.0

    except Exception as e:
        print(f"Fel vid läsning av FTE actual för {enhet_kst}, {manad_str}: {e}")
        return 0.0


def load_fte_budget(enhet_kst, manad_str, base_path=None):
    """
    Hämtar budget FTE från "HR Cost"

    Args:
        enhet_kst: '102', '103', '601', '602'
        manad_str: '2026-01', '2026-02' etc
        base_path: Bas-sökväg till data-mappen

    Returns:
        float: Budget FTE för månaden
    """
    try:
        paths = get_file_paths(enhet_kst, base_path)
        df = pd.read_excel(paths['hr_cost'])

        # Konvertera månad till månad-namn (January, February etc)
        year, month = manad_str.split('-')
        month_num = int(month)
        month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December']
        month_name = month_names[month_num - 1]

        # Hitta kolumn för FTE (month_name.1, t.ex. "January.1")
        fte_col = f"{month_name}.1"

        if fte_col not in df.columns:
            print(f"Kolumn {fte_col} finns inte i HR Cost för {enhet_kst}")
            return 0.0

        # Hitta Total-raden dynamiskt (Month-kolumnen innehåller "Total")
        total_rows = df[df['Month'] == 'Total']

        if total_rows.empty:
            print(f"Ingen Total-rad hittades i HR Cost för {enhet_kst}")
            return 0.0

        # Ta första Total-raden
        total_row = total_rows.iloc[0]
        fte_budget = total_row[fte_col]

        return float(fte_budget) if pd.notna(fte_budget) else 0.0

    except Exception as e:
        print(f"Fel vid läsning av FTE budget för {enhet_kst}, {manad_str}: {e}")
        return 0.0


def load_rehab_poang_budget(enhet_kst, manad_str, base_path=None):
    """
    Hämtar budgeterade Rehab-poäng från "Intäkt Budget Rehab"
    OBS: Endast för Rehab-enheter (601, 602)

    Args:
        enhet_kst: '601', '602'
        manad_str: '2026-01', '2026-02' etc
        base_path: Bas-sökväg till data-mappen

    Returns:
        dict: {
            'maaltal': float (Måltal per prestationsanställd),
            'antal_anstallda': float (Antal Prestationsanställda),
            'budgeterad_intakt': float (Intäkt konto 3053)
        }
    """
    try:
        # Endast för Rehab-enheter
        if enhet_kst not in ['601', '602']:
            return {'maaltal': 0, 'antal_anstallda': 0, 'budgeterad_intakt': 0}

        paths = get_file_paths(enhet_kst, base_path)
        df = pd.read_excel(paths['intakt_budget'])

        # Konvertera månad till månad-namn
        year, month = manad_str.split('-')
        month_num = int(month)
        month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December']
        month_name = month_names[month_num - 1]

        if month_name not in df.columns:
            print(f"Kolumn {month_name} finns inte i Intäkt Budget Rehab för {enhet_kst}")
            return {'maaltal': 0, 'antal_anstallda': 0, 'budgeterad_intakt': 0}

        # Rad 2 = Måltal per prestationsanställd
        # Rad 3 = Antal Prestationsanställda
        # Rad 4 = Intäkt konto 3053

        maaltal = df.iloc[2][month_name] if pd.notna(df.iloc[2][month_name]) else 0
        antal_anstallda = df.iloc[3][month_name] if pd.notna(df.iloc[3][month_name]) else 0
        budgeterad_intakt = df.iloc[4][month_name] if pd.notna(df.iloc[4][month_name]) else 0

        return {
            'maaltal': float(maaltal),
            'antal_anstallda': float(antal_anstallda),
            'budgeterad_intakt': float(budgeterad_intakt)
        }

    except Exception as e:
        print(f"Fel vid läsning av Rehab poäng budget för {enhet_kst}, {manad_str}: {e}")
        return {'maaltal': 0, 'antal_anstallda': 0, 'budgeterad_intakt': 0}


def load_personalkostnad(enhet_kst, manad_str, base_path=None):
    """
    Hämtar personalkostnader från P&L Actual och P&L Budget
    Personalkostnader ligger under COGS > Medical staff > Total

    Args:
        enhet_kst: '102', '103', '601', '602'
        manad_str: '2026-01', '2026-02' etc
        base_path: Bas-sökväg till data-mappen

    Returns:
        dict: {'actual': float, 'budget': float}
    """
    try:
        paths = get_file_paths(enhet_kst, base_path)

        # Läs P&L Actual och Budget
        df_actual = pd.read_excel(paths['pl_actual'])
        df_budget = pd.read_excel(paths['pl_budget'])

        # Konvertera månad till period-nummer (202601)
        year, month = manad_str.split('-')
        manad_num = int(year) * 100 + int(month)

        # Hitta kolumn för rätt månad (kolumn med period-nummer i header)
        # Header row (rad 0) innehåller månaderna som Selected Period (x)
        period_cols = [col for col in df_actual.columns if 'Selected Period' in str(col)]

        header_row_actual = df_actual.iloc[0]
        header_row_budget = df_budget.iloc[0]

        col_idx = None
        for col in period_cols:
            val = header_row_actual[col]
            if pd.notna(val) and int(val) == manad_num:
                col_idx = col
                break

        if col_idx is None:
            return {'actual': 0, 'budget': 0}

        # Hitta rad för personalkostnader: COGS > Medical staff > Total
        # Rad där CG Item = 'COGS' OCH Unnamed: 1 = 'Medical staff' OCH Unnamed: 2 = 'Total'
        medical_staff_actual = df_actual[
            (df_actual['CG Item'] == 'COGS') &
            (df_actual['Unnamed: 1'] == 'Medical staff') &
            (df_actual['Unnamed: 2'] == 'Total')
        ]

        medical_staff_budget = df_budget[
            (df_budget['CG Item'] == 'COGS') &
            (df_budget['Unnamed: 1'] == 'Medical staff') &
            (df_budget['Unnamed: 2'] == 'Total')
        ]

        if medical_staff_actual.empty or medical_staff_budget.empty:
            # Om Medical staff inte finns, försök med COGS > Total
            cogs_total_actual = df_actual[
                (df_actual['CG Item'] == 'COGS') &
                (df_actual['Unnamed: 1'] == 'Total')
            ]
            cogs_total_budget = df_budget[
                (df_budget['CG Item'] == 'COGS') &
                (df_budget['Unnamed: 1'] == 'Total')
            ]

            if cogs_total_actual.empty or cogs_total_budget.empty:
                return {'actual': 0, 'budget': 0}

            actual_val = cogs_total_actual.iloc[0][col_idx]
            budget_val = cogs_total_budget.iloc[0][col_idx]
        else:
            # Ta första raden (Medical staff Total)
            actual_val = medical_staff_actual.iloc[0][col_idx]
            budget_val = medical_staff_budget.iloc[0][col_idx]

        return {
            'actual': abs(float(actual_val)) if pd.notna(actual_val) else 0,  # abs() eftersom COGS är negativt
            'budget': abs(float(budget_val)) if pd.notna(budget_val) else 0
        }

    except Exception as e:
        print(f"Fel vid läsning av personalkostnader för {enhet_kst}, {manad_str}: {e}")
        return {'actual': 0, 'budget': 0}


def load_all_data_for_enhet(enhet_kst, manad_str, base_path=None):
    """
    Hämtar ALL data för en enhet och månad

    Args:
        enhet_kst: '102', '103', '601', '602'
        manad_str: '2026-01', '2026-02' etc
        base_path: Bas-sökväg till data-mappen

    Returns:
        dict: {
            'fte_actual': float,
            'fte_budget': float,
            'personalkostnad_actual': float,
            'personalkostnad_budget': float,
            'rehab_budget': dict (endast för Rehab-enheter)
        }
    """
    data = {
        'fte_actual': load_fte_actual(enhet_kst, manad_str, base_path),
        'fte_budget': load_fte_budget(enhet_kst, manad_str, base_path),
    }

    # Lägg till personalkostnader
    personalkostnad = load_personalkostnad(enhet_kst, manad_str, base_path)
    data['personalkostnad_actual'] = personalkostnad['actual']
    data['personalkostnad_budget'] = personalkostnad['budget']

    # Om det är en Rehab-enhet, lägg till Rehab-budget
    if enhet_kst in ['601', '602']:
        data['rehab_budget'] = load_rehab_poang_budget(enhet_kst, manad_str, base_path)

    return data


# Test-funktion
if __name__ == "__main__":
    # Test för 601 (Rehab)
    print("=" * 60)
    print("TEST: Enhet 601 (Frölunda Torg Rehab), Månad 2026-01")
    print("=" * 60)

    data = load_all_data_for_enhet('601', '2026-01')

    print(f"\nFTE Actual: {data['fte_actual']:.2f}")
    print(f"FTE Budget: {data['fte_budget']:.2f}")
    print(f"Personalkostnad Actual: {data['personalkostnad_actual']:,.0f} kr")
    print(f"Personalkostnad Budget: {data['personalkostnad_budget']:,.0f} kr")

    if 'rehab_budget' in data:
        print(f"\nRehab Budget:")
        print(f"  Måltal: {data['rehab_budget']['maaltal']:.0f}")
        print(f"  Antal anställda: {data['rehab_budget']['antal_anstallda']:.2f}")
        print(f"  Budgeterad intäkt: {data['rehab_budget']['budgeterad_intakt']:,.0f} kr")

    print("\n" + "=" * 60)
    print("TEST: Enhet 102 (Frölunda Torg VC), Månad 2026-01")
    print("=" * 60)

    data = load_all_data_for_enhet('102', '2026-01')

    print(f"\nFTE Actual: {data['fte_actual']:.2f}")
    print(f"FTE Budget: {data['fte_budget']:.2f}")
    print(f"Personalkostnad Actual: {data['personalkostnad_actual']:,.0f} kr")
    print(f"Personalkostnad Budget: {data['personalkostnad_budget']:,.0f} kr")
