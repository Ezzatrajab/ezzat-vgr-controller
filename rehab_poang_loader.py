"""
Läser Rehab-poäng och top performers från Poänguppföljning Rehab 2026.xlsx
För Tätort-enheter: Beräknar poäng från P&L Actual-data
"""

import pandas as pd
import os

# Mapping KST → Sheet-namn (ENDAST STOR-GÖTEBORG)
KST_TO_SHEET = {
    '601': 'Frölunda Torg',
    '602': 'Grimmered',
    '603': 'Majorna',
    '604': 'Pedagogen Park',
    '605': 'Åby',
    '607': 'Olskroken',
    '660': 'Avenyn',
    '715': 'Karlastaden',
}

# Tätort Rehab-enheter (SAKNAS i Poänguppföljning - beräknas från P&L)
TATORT_REHAB_KST = ['703', '705', '706', '708', '714', '650-670', '713']

# Mapping KST → Enhetens namn i översiktsfliken
KST_TO_ENHETSNAMN = {
    '601': 'Frölunda Torget',
    '602': 'Grimmered',
    '603': 'Majorna',
    '604': 'Pedagogen Park',
    '605': 'Åby',
    '607': 'Olskroken',
    '660': 'Avenyn',
    '715': 'Karlastaden',
}

# Mapping månad → kolumnindex
MANAD_TO_COL = {
    '2026-01': 1,   # Jan
    '2026-02': 2,   # Feb
    '2026-03': 3,   # Mar
    '2026-04': 4,   # Apr
    '2026-05': 5,   # Maj
    '2026-06': 6,   # Jun
    '2026-07': 7,   # Jul
    '2026-08': 8,   # Aug
    '2026-09': 9,   # Sep
    '2026-10': 10,  # Okt
    '2026-11': 11,  # Nov
    '2026-12': 12,  # Dec
}


def load_rehab_poang_from_pl(enhet_kst, manad_str, base_path=None):
    """
    Beräknar Rehab-poäng från P&L Actual och Budget för Tätort-enheter

    Args:
        enhet_kst: '703', '705', '706', '708', '714', '650-670', '713'
        manad_str: '2026-01', '2026-02', '2026-03', etc
        base_path: Bas-sökväg

    Returns:
        dict: {
            'total_poang': float (beräknat från intäkt 3053 / grundbelopp),
            'budget_poang': float (från Intäkt Budget Rehab),
            'top_performers': [] (tom för Tätort-enheter)
        }
    """
    try:
        # Hitta data-mappen
        if base_path is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            base_path = os.path.join(script_dir, 'data')

        # === Läs P&L Actual för att få intäkt 3053 ===
        pl_actual_path = os.path.join(base_path, enhet_kst, 'P&L Actual.xlsx')
        if not os.path.exists(pl_actual_path):
            print(f"⚠️ P&L Actual saknas för {enhet_kst}")
            return {'total_poang': 0, 'budget_poang': 0, 'top_performers': []}

        df_pl = pd.read_excel(pl_actual_path, header=None)

        # Hitta kolumn för vald månad
        year, month = manad_str.split('-')
        target_month = int(year + month)  # 202603 för 2026-03

        # Rad 1 innehåller Year Month No
        month_row = df_pl.iloc[1, :].tolist()
        col_idx = None
        for i, val in enumerate(month_row):
            if pd.notna(val):
                try:
                    if int(float(val)) == target_month:
                        col_idx = i
                        break
                except (ValueError, TypeError):
                    continue

        if col_idx is None:
            print(f"⚠️ Månad {manad_str} hittades inte i P&L Actual för {enhet_kst}")
            return {'total_poang': 0, 'budget_poang': 0, 'top_performers': []}

        # Hitta rad 8: "3053 RG Prestationsersättning Rehab"
        intakt_3053 = 0
        for idx in range(len(df_pl)):
            cell = df_pl.iloc[idx, 3] if df_pl.shape[1] > 3 else None
            if pd.notna(cell) and '3053' in str(cell):
                intakt_3053 = df_pl.iloc[idx, col_idx]
                if pd.notna(intakt_3053):
                    intakt_3053 = abs(float(intakt_3053)) * 1000  # P&L är i TKRSE K → konvertera till kr
                break

        # === Läs grundbelopp från Intäkt Budget Rehab ===
        grundbelopp = 523  # Default
        budget_files = [f for f in os.listdir(os.path.join(base_path, enhet_kst))
                       if 'Intäkt Budget Rehab' in f and f.endswith('.xlsx')]

        if budget_files:
            df_budget = pd.read_excel(os.path.join(base_path, enhet_kst, budget_files[0]), header=None)
            if len(df_budget) > 2:
                gb = df_budget.iloc[2, 1]  # Rad 2, kolumn 1
                if pd.notna(gb):
                    grundbelopp = float(gb)

            # Beräkna budget poäng: Måltal × Antal anställda
            if len(df_budget) > 4:
                # Hitta kolumn för månaden
                month_header = df_budget.iloc[0, :].tolist()
                month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                             'July', 'August', 'September', 'October', 'November', 'December']
                month_name = month_names[int(month) - 1]

                budget_col_idx = None
                for i, val in enumerate(month_header):
                    if pd.notna(val) and val == month_name:
                        budget_col_idx = i
                        break

                budget_poang = 0
                if budget_col_idx:
                    maaltal = df_budget.iloc[3, budget_col_idx]  # Rad 3
                    antal_anstallda = df_budget.iloc[4, budget_col_idx]  # Rad 4
                    if pd.notna(maaltal) and pd.notna(antal_anstallda):
                        budget_poang = float(maaltal) * float(antal_anstallda)
        else:
            budget_poang = 0

        # Beräkna actual poäng = intäkt / grundbelopp
        actual_poang = intakt_3053 / grundbelopp if grundbelopp > 0 else 0

        return {
            'total_poang': actual_poang,
            'budget_poang': budget_poang,
            'top_performers': []  # Ingen individdata för Tätort-enheter
        }

    except Exception as e:
        print(f"Fel vid beräkning av Rehab-poäng från P&L för {enhet_kst}: {e}")
        return {'total_poang': 0, 'budget_poang': 0, 'top_performers': []}


def load_rehab_budget_poang(enhet_kst, manad_str, base_path=None):
    """
    Läser budgeterade Rehab-poäng från fliken "Enheterna AO Stor-GBG"

    Args:
        enhet_kst: '601', '602', etc
        manad_str: '2026-01', '2026-02', etc
        base_path: Bas-sökväg

    Returns:
        float: Budgeterade poäng för månaden
    """
    try:
        # Hitta filen
        if base_path is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(script_dir, 'data', 'Poänguppföljning Rehab 2026.xlsx')
            if not os.path.exists(file_path):
                parent_dir = os.path.dirname(script_dir)
                file_path = os.path.join(parent_dir, 'Poänguppföljning Rehab 2026.xlsx')
        else:
            file_path = os.path.join(base_path, 'Poänguppföljning Rehab 2026.xlsx')

        if not os.path.exists(file_path):
            return 0

        # Hämta enhetsnamn och kolumnindex
        enhetsnamn = KST_TO_ENHETSNAMN.get(enhet_kst)
        if not enhetsnamn:
            return 0

        col_idx = MANAD_TO_COL.get(manad_str)
        if col_idx is None:
            return 0

        # Läs översiktsfliken
        df = pd.read_excel(file_path, sheet_name='Enheterna AO Stor-GBG', header=None)

        # Hitta raden med enhetsnamnet
        for idx in range(len(df)):
            cell_value = df.iloc[idx, 0]
            if pd.notna(cell_value) and isinstance(cell_value, str):
                if enhetsnamn.lower() in cell_value.lower():
                    # Nästa rad är "Poäng ACTUAL", sedan "Poäng Budget"
                    budget_row_idx = idx + 2  # +1 för ACTUAL, +2 för Budget
                    if budget_row_idx < len(df):
                        budget_value = df.iloc[budget_row_idx, col_idx]
                        if pd.notna(budget_value) and isinstance(budget_value, (int, float)):
                            return float(budget_value)

        return 0

    except Exception as e:
        print(f"Fel vid läsning av Rehab budget för {enhet_kst}, {manad_str}: {e}")
        return 0


def load_rehab_poang_och_top_performers(enhet_kst, manad_str, base_path=None):
    """
    Läser Rehab-poäng och top performers från Poänguppföljning Rehab 2026.xlsx
    För Tätort-enheter: Beräknar poäng från P&L Actual

    Args:
        enhet_kst: '601', '602', etc
        manad_str: '2026-01', '2026-02', etc
        base_path: Bas-sökväg (default: ../Poänguppföljning Rehab 2026.xlsx)

    Returns:
        dict: {
            'total_poang': float,
            'budget_poang': float,
            'top_performers': [{'namn': str, 'poang': float}, ...]
        }
    """
    try:
        # === TÄTORT REHAB-ENHETER: Beräkna från P&L ===
        if enhet_kst in TATORT_REHAB_KST:
            return load_rehab_poang_from_pl(enhet_kst, manad_str, base_path)

        # === STOR-GÖTEBORG: Läs från Poänguppföljning ===
        # Läs budget först
        budget_poang = load_rehab_budget_poang(enhet_kst, manad_str, base_path)
        # Hitta filen
        if base_path is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            # Kolla först om filen finns i data/
            file_path = os.path.join(script_dir, 'data', 'Poänguppföljning Rehab 2026.xlsx')
            if not os.path.exists(file_path):
                # Kolla i parent-mappen
                parent_dir = os.path.dirname(script_dir)
                file_path = os.path.join(parent_dir, 'Poänguppföljning Rehab 2026.xlsx')
        else:
            file_path = os.path.join(base_path, 'Poänguppföljning Rehab 2026.xlsx')

        if not os.path.exists(file_path):
            print(f"⚠️ Poänguppföljning-fil hittades inte på: {file_path}")
            return {'total_poang': 0, 'top_performers': []}

        # Hämta sheet-namn och kolumnindex
        sheet_name = KST_TO_SHEET.get(enhet_kst)
        if not sheet_name:
            return {'total_poang': 0, 'top_performers': []}

        col_idx = MANAD_TO_COL.get(manad_str)
        if col_idx is None:
            return {'total_poang': 0, 'top_performers': []}

        # Läs Excel-fil
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)

        # Rad 2 = "Actual" header
        # Rad 3+ = Personer med poäng

        total_poang = 0
        top_performers = []

        # Läs rad 3 till 30 (personer)
        for idx in range(3, min(30, len(df))):
            namn = df.iloc[idx, 0]

            # Stoppa om vi når en tom rad eller "NaN"
            if pd.isna(namn) or namn == '' or not isinstance(namn, str):
                break

            # Läs poäng för vald månad
            poang = df.iloc[idx, col_idx]

            if pd.notna(poang) and isinstance(poang, (int, float)):
                poang = float(poang)
                total_poang += poang

                # Lägg till i top_performers om över 200
                if poang >= 200:
                    top_performers.append({
                        'namn': namn.strip(),
                        'poang': poang
                    })

        # Sortera top_performers efter poäng (högst först)
        top_performers.sort(key=lambda x: x['poang'], reverse=True)

        return {
            'total_poang': total_poang,
            'budget_poang': budget_poang,
            'top_performers': top_performers
        }

    except Exception as e:
        print(f"Fel vid läsning av Rehab-poäng för {enhet_kst}, {manad_str}: {e}")
        return {'total_poang': 0, 'budget_poang': 0, 'top_performers': []}


# Test-funktion
if __name__ == "__main__":
    print("TEST: Frölunda Torg (601) - Februari 2026")
    print("="*80)

    result = load_rehab_poang_och_top_performers('601', '2026-02')

    print(f"\nTotal Poäng: {result['total_poang']:.0f}")
    print(f"\nTop Performers (≥200 poäng):")
    if result['top_performers']:
        for i, person in enumerate(result['top_performers'], 1):
            print(f"  {i}. {person['namn']:<25} {person['poang']:>6.0f} poäng")
    else:
        print("  (Ingen över 200 poäng)")

    print("\n" + "="*80)
    print("TEST: Grimmered (602) - Januari 2026")
    print("="*80)

    result = load_rehab_poang_och_top_performers('602', '2026-01')

    print(f"\nTotal Poäng: {result['total_poang']:.0f}")
    print(f"\nTop Performers (≥200 poäng):")
    if result['top_performers']:
        for i, person in enumerate(result['top_performers'], 1):
            print(f"  {i}. {person['namn']:<25} {person['poang']:>6.0f} poäng")
    else:
        print("  (Ingen över 200 poäng)")
