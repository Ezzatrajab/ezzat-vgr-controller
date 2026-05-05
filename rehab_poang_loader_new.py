"""
Poänguppföljning Rehab 2026 Loader - NY VERSION
Skapad: 2026-05-05
Syfte: Läsa Rehab Poäng och Teambesök från Poänguppföljning Rehab 2026.xlsx
       enligt Ezzats Inställningar.xlsx

DATAKÄLLA:
- Rehab Poäng: Dashboard-fliken
- Teambesök: Teambesök VGR-fliken
"""

import pandas as pd
import os
from typing import Dict, Optional


def load_rehab_poang_from_file(enhet_namn: str, manad_str: str, base_path=None) -> Optional[float]:
    """
    Läser Rehab Poäng för en enhet och månad från Poänguppföljning Rehab 2026.xlsx Dashboard-flik.

    Args:
        enhet_namn: 'Frölunda Torg', 'Åby', 'Karlastaden', etc. (KORT namn utan 'Rehab' suffix)
        manad_str: '2026-01', '2026-02', '2026-03', etc.
        base_path: Bas-sökväg (optional)

    Returns:
        float eller None om data saknas

    Exempel:
        load_rehab_poang_from_file('Frölunda Torg', '2026-03') -> 883.0
    """
    if base_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, 'Poänguppföljning Rehab 2026.xlsx')
    else:
        file_path = os.path.join(base_path, 'Poänguppföljning Rehab 2026.xlsx')

    if not os.path.exists(file_path):
        return None

    try:
        # Läs Dashboard-fliken
        df = pd.read_excel(file_path, sheet_name='Dashboard', header=None)

        # Hitta header-raden (rad med "Enhet | Jan | Feb | Mar...")
        header_row_idx = None
        for idx, row in df.iterrows():
            if pd.notna(row[0]) and str(row[0]).strip() == 'Enhet':
                header_row_idx = idx
                break

        if header_row_idx is None:
            return None

        # Hitta månad-kolumn
        # manad_str '2026-03' -> kolumnnamn 'Mar', '2026-01' -> 'Jan'
        manad_mapping = {
            '01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr',
            '05': 'Maj', '06': 'Jun', '07': 'Jul', '08': 'Aug',
            '09': 'Sep', '10': 'Okt', '11': 'Nov', '12': 'Dec'
        }

        year, month = manad_str.split('-')
        manad_namn = manad_mapping.get(month)

        if not manad_namn:
            return None

        # Hitta kolumn-index för månaden
        header_row = df.iloc[header_row_idx]
        manad_col_idx = None
        for col_idx in range(1, len(header_row)):
            if pd.notna(header_row[col_idx]) and str(header_row[col_idx]).strip() == manad_namn:
                manad_col_idx = col_idx
                break

        if manad_col_idx is None:
            return None

        # Namnmappning - Dashboard-fliken använder kortnamn
        # Ta bort "Rehab" suffix om det finns
        search_name = enhet_namn.replace(' Rehab', '').strip()

        # Specialfall för kombinerade enheter
        if search_name == 'Tanum- Fjällbacka':
            search_name = 'Tanum och Fjällbacka'

        # Sök efter enheten (börjar efter header-raden)
        for idx in range(header_row_idx + 1, len(df)):
            cell_value = df.iloc[idx, 0]
            if pd.isna(cell_value):
                break  # Slut på data

            cell_str = str(cell_value).strip()
            if cell_str == search_name:
                value = df.iloc[idx, manad_col_idx]
                try:
                    return float(value) if pd.notna(value) else None
                except (ValueError, TypeError):
                    return None

        # Om vi inte hittade exakt match, testa variationer
        # Brålanda-Torpa kan vara listad som "Brålanda-Torpa"
        if 'Brålanda' in search_name or 'Torpa' in search_name:
            for idx in range(header_row_idx + 1, len(df)):
                cell_value = df.iloc[idx, 0]
                if pd.isna(cell_value):
                    break
                cell_str = str(cell_value).strip()
                if 'Brålanda-Torpa' in cell_str or 'Torpa' in cell_str:
                    value = df.iloc[idx, manad_col_idx]
                    try:
                        return float(value) if pd.notna(value) else None
                    except (ValueError, TypeError):
                        return None

        return None

    except Exception as e:
        print(f"Fel vid läsning av Rehab Poäng från Dashboard för {enhet_namn}, {manad_str}: {e}")
        return None


def load_teambesok_from_file(enhet_namn: str, manad_str: str, base_path=None) -> Optional[float]:
    """
    Läser Teambesök för en enhet och månad från Poänguppföljning Rehab 2026.xlsx Teambesök VGR-flik.

    Args:
        enhet_namn: 'Frölunda Torg', 'Åby', 'Karlastaden', etc. (KORT namn utan 'Rehab' suffix)
        manad_str: '2025-04', '2025-05', '2026-01', etc.
        base_path: Bas-sökväg (optional)

    Returns:
        float eller None om data saknas

    Exempel:
        load_teambesok_from_file('Frölunda Torg', '2025-04') -> 41.0
    """
    if base_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, 'Poänguppföljning Rehab 2026.xlsx')
    else:
        file_path = os.path.join(base_path, 'Poänguppföljning Rehab 2026.xlsx')

    if not os.path.exists(file_path):
        return None

    try:
        # Läs Teambesök VGR-fliken (index 1)
        df = pd.read_excel(file_path, sheet_name=1, header=None)

        # Header-raden är rad 1 med "Teambesök / VGR" och månader i format 202504, 202505...
        header_row_idx = 1

        # Hitta månad-kolumn
        # manad_str '2025-04' -> 202504, '2026-01' -> 202601
        year, month = manad_str.split('-')
        manad_excel_format = int(f"{year}{month}")  # '2025-04' -> 202504

        header_row = df.iloc[header_row_idx]
        manad_col_idx = None
        for col_idx in range(1, len(header_row)):
            try:
                if int(header_row[col_idx]) == manad_excel_format:
                    manad_col_idx = col_idx
                    break
            except (ValueError, TypeError):
                continue

        if manad_col_idx is None:
            return None

        # Namnmappning - Teambesök-fliken använder kortnamn
        # Ta bort "Rehab" suffix om det finns
        search_name = enhet_namn.replace(' Rehab', '').strip()

        # Specialfall för kombinerade enheter
        if search_name == 'Tanum- Fjällbacka':
            search_name = 'Fjällbacka - Tanum'
        elif 'Brålanda' in search_name or 'Torpa' in search_name:
            # Teambesök-fliken har separata rader för Brålanda och Torpa - summera dem
            brlanda_val = None
            torpa_val = None
            for idx in range(2, len(df)):  # Börjar från rad 2 (efter header)
                cell_value = df.iloc[idx, 0]
                if pd.isna(cell_value):
                    break
                cell_str = str(cell_value).strip()
                if cell_str == 'Brålanda':
                    try:
                        brlanda_val = float(df.iloc[idx, manad_col_idx]) if pd.notna(df.iloc[idx, manad_col_idx]) else 0
                    except (ValueError, TypeError):
                        brlanda_val = 0
                elif cell_str == 'Torpa':
                    try:
                        torpa_val = float(df.iloc[idx, manad_col_idx]) if pd.notna(df.iloc[idx, manad_col_idx]) else 0
                    except (ValueError, TypeError):
                        torpa_val = 0

            if brlanda_val is not None or torpa_val is not None:
                total = (brlanda_val or 0) + (torpa_val or 0)
                return total if total > 0 else None
            return None

        # Sök efter enheten (börjar från rad 2)
        for idx in range(2, len(df)):
            cell_value = df.iloc[idx, 0]
            if pd.isna(cell_value):
                break  # Slut på data

            cell_str = str(cell_value).strip()
            if cell_str == search_name:
                value = df.iloc[idx, manad_col_idx]
                try:
                    return float(value) if pd.notna(value) else None
                except (ValueError, TypeError):
                    return None

        return None

    except Exception as e:
        print(f"Fel vid läsning av Teambesök från Teambesök VGR för {enhet_namn}, {manad_str}: {e}")
        return None


def load_rehab_kpi_from_poang_file(enhet_namn: str, manad_str: str, base_path=None) -> Dict[str, Optional[float]]:
    """
    Hämtar BÅDE Rehab Poäng och Teambesök från Poänguppföljning Rehab 2026.xlsx.

    Args:
        enhet_namn: 'Frölunda Torg Rehab', 'Åby Rehab', etc. (med eller utan 'Rehab' suffix)
        manad_str: '2026-01', '2026-02', etc.
        base_path: Bas-sökväg (optional)

    Returns:
        dict: {
            'rehab_poang': float eller None,
            'teambesok': float eller None
        }
    """
    # Ta bort "Rehab" suffix för att få kortnamn
    kort_namn = enhet_namn.replace(' Rehab', '').strip()

    return {
        'rehab_poang': load_rehab_poang_from_file(kort_namn, manad_str, base_path),
        'teambesok': load_teambesok_from_file(kort_namn, manad_str, base_path)
    }


# ========================================
# TEST-FUNKTIONER
# ========================================

if __name__ == "__main__":
    print("=== TEST REHAB POÄNG (Dashboard-fliken) ===")
    test_poang = load_rehab_poang_from_file('Frölunda Torg', '2026-03')
    print(f"Frölunda Torg Rehab Poäng Mars 2026: {test_poang}")

    test_poang2 = load_rehab_poang_from_file('Grimmered', '2026-04')
    print(f"Grimmered Rehab Poäng April 2026: {test_poang2}")

    print("\n=== TEST TEAMBESÖK (Teambesök VGR-fliken) ===")
    test_teambesok = load_teambesok_from_file('Frölunda Torg', '2025-04')
    print(f"Frölunda Torg Teambesök April 2025: {test_teambesok}")

    test_teambesok2 = load_teambesok_from_file('Grimmered', '2025-05')
    print(f"Grimmered Teambesök Maj 2025: {test_teambesok2}")

    print("\n=== TEST KOMBINERAD ===")
    test_kombinerad = load_rehab_kpi_from_poang_file('Frölunda Torg Rehab', '2026-03')
    print(f"Frölunda Torg Rehab Mars 2026: {test_kombinerad}")
