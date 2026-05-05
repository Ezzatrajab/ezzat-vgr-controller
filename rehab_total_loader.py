"""
Läser TOTALSUMMA för Rehab Poäng från Poänguppföljning Rehab 2026.xlsx Dashboard-flik
Rad 29: "TOTALT ALLA ENHETER"
"""

import pandas as pd
import os
from typing import Optional


def load_rehab_poang_total(manad_str: str, base_path=None) -> dict:
    """
    Läser total Rehab Poäng för alla enheter från Dashboard-fliken rad 29.

    Args:
        manad_str: '2026-01', '2026-02', '2026-03', etc.
        base_path: Bas-sökväg (optional)

    Returns:
        dict: {
            'actual': float (total Rehab Poäng actual för månaden),
            'budget': float (0 - budget finns inte på denna rad)
        }

    Exempel:
        load_rehab_poang_total('2026-03') -> {'actual': 14540, 'budget': 0}
    """
    if base_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, 'Poänguppföljning Rehab 2026.xlsx')
    else:
        file_path = os.path.join(base_path, 'Poänguppföljning Rehab 2026.xlsx')

    if not os.path.exists(file_path):
        print(f"VARNING: Filen {file_path} finns inte")
        return {'actual': 0, 'budget': 0}

    try:
        # Läs Dashboard-fliken
        df = pd.read_excel(file_path, sheet_name='Dashboard', header=None)

        # Hitta "TOTALT ALLA ENHETER"-raden (rad 29, index 28)
        total_row_idx = 28  # Rad 29 i Excel = index 28 i pandas

        # Verifiera att det är rätt rad
        if df.iloc[total_row_idx, 0] != 'TOTALT ALLA ENHETER':
            print(f"VARNING: Rad 29 innehåller inte 'TOTALT ALLA ENHETER', söker...")
            # Sök efter rätt rad
            for idx in range(len(df)):
                if pd.notna(df.iloc[idx, 0]) and str(df.iloc[idx, 0]).strip() == 'TOTALT ALLA ENHETER':
                    total_row_idx = idx
                    break

        # Hitta månad-kolumn
        # Dashboard-fliken har månader: Jan (B/1), Feb (C/2), Mar (D/3), Apr (E/4)...
        manad_mapping = {
            '2026-01': 1,  # Jan = kolumn B = index 1
            '2026-02': 2,  # Feb = kolumn C = index 2
            '2026-03': 3,  # Mar = kolumn D = index 3
            '2026-04': 4,  # Apr = kolumn E = index 4
            '2026-05': 5,  # Maj = kolumn F = index 5
            '2026-06': 6,  # Jun = kolumn G = index 6
            '2026-07': 7,  # Jul = kolumn H = index 7
            '2026-08': 8,  # Aug = kolumn I = index 8
            '2026-09': 9,  # Sep = kolumn J = index 9
            '2026-10': 10, # Okt = kolumn K = index 10
            '2026-11': 11, # Nov = kolumn L = index 11
            '2026-12': 12, # Dec = kolumn M = index 12
        }

        manad_col_idx = manad_mapping.get(manad_str)

        if manad_col_idx is None:
            print(f"VARNING: Ogiltig månad {manad_str}")
            return {'actual': 0, 'budget': 0}

        # Läs värdet från TOTALT ALLA ENHETER-raden
        total_value = df.iloc[total_row_idx, manad_col_idx]

        try:
            actual_value = float(total_value) if pd.notna(total_value) else 0
        except (ValueError, TypeError):
            actual_value = 0

        return {
            'actual': actual_value,
            'budget': 0  # Budget finns inte på denna rad
        }

    except Exception as e:
        print(f"Fel vid läsning av Rehab Poäng total från Dashboard för {manad_str}: {e}")
        return {'actual': 0, 'budget': 0}


# ========================================
# TEST-FUNKTIONER
# ========================================

if __name__ == "__main__":
    print("=== TEST REHAB POÄNG TOTALSUMMA ===")

    for manad in ['2026-01', '2026-02', '2026-03', '2026-04']:
        result = load_rehab_poang_total(manad)
        print(f"{manad}: Total = {result['actual']:.0f}")

    print("\nFORVANTAT (fran Dashboard rad 29):")
    print("2026-01: 11,490")
    print("2026-02: 12,544")
    print("2026-03: 14,540")
    print("2026-04: 13,908")
