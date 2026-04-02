"""
Läser Rehab-poäng och top performers från Poänguppföljning Rehab 2026.xlsx
"""

import pandas as pd
import os

# Mapping KST → Sheet-namn
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


def load_rehab_poang_och_top_performers(enhet_kst, manad_str, base_path=None):
    """
    Läser Rehab-poäng och top performers från Poänguppföljning Rehab 2026.xlsx

    Args:
        enhet_kst: '601', '602', etc
        manad_str: '2026-01', '2026-02', etc
        base_path: Bas-sökväg (default: ../Poänguppföljning Rehab 2026.xlsx)

    Returns:
        dict: {
            'total_poang': float,
            'top_performers': [{'namn': str, 'poang': float}, ...]
        }
    """
    try:
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
            'top_performers': top_performers
        }

    except Exception as e:
        print(f"Fel vid läsning av Rehab-poäng för {enhet_kst}, {manad_str}: {e}")
        return {'total_poang': 0, 'top_performers': []}


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
