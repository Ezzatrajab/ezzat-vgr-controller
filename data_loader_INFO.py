"""
Ny och förbättrad data loader - läser från Info-fliken i KPIer Stor-GBG.xlsx
Mycket enklare och mer robust än att leta i olika filer!
"""

import pandas as pd
import os


def load_from_info_sheet(enhet_kst, manad_str, base_path=None):
    """
    Hämtar all data från Info-fliken i KPIer Stor-GBG.xlsx

    Args:
        enhet_kst: '102', '103', '008', etc
        manad_str: '2026-01', '2026-02', '2026-03'
        base_path: Sökväg till data-mappen (default: script dir + 'data')

    Returns:
        dict med:
        {
            'listning_actual': int,
            'listningpoang_actual': float,
            'acg_casemix_actual': float,
            'huvudintakter_actual': float,
            'medical_staff_actual': float
        }
    """
    try:
        if base_path is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            base_path = os.path.join(script_dir, 'data')

        kpi_file = os.path.join(base_path, 'KPIer Stor-GBG.xlsx')

        if not os.path.exists(kpi_file):
            print(f"KPIer-fil hittades inte: {kpi_file}")
            return _empty_result()

        # Läs Info-fliken utan headers
        df = pd.read_excel(kpi_file, sheet_name='Info', header=None)

        # Konvertera månad till period (202601, 202602, 202603)
        year, month = manad_str.split('-')
        period = int(year + month)

        # Hitta kolumn-index för rätt period
        # Periods finns i rad 2, från kolumn 2 och framåt
        header_row = df.iloc[2, :]
        col_idx = None
        for i, val in enumerate(header_row):
            if pd.notna(val) and int(val) == period:
                col_idx = i
                break

        if col_idx is None:
            print(f"Period {period} hittades inte i Info-fliken")
            return _empty_result()

        # KST finns i kolumn 28 för alla sektioner
        kst_col = 28

        # Hitta rad för rätt enhet i varje sektion
        result = {}

        # 1. LISTNING (rad 3-16)
        result['listning_actual'] = _find_value_in_section(df, enhet_kst, kst_col, 3, 17, col_idx)

        # 2. LISTNINGPOÄNG (rad 20-34)
        result['listningpoang_actual'] = _find_value_in_section(df, enhet_kst, kst_col, 20, 35, col_idx)

        # 3. ACG CASEMIX (rad 38-51)
        result['acg_casemix_actual'] = _find_value_in_section(df, enhet_kst, kst_col, 38, 52, col_idx)

        # 4. HUVUDINTÄKTER (rad 55-68)
        result['huvudintakter_actual'] = _find_value_in_section(df, enhet_kst, kst_col, 55, 69, col_idx)

        # 5. MEDICAL STAFF (rad 72-85)
        result['medical_staff_actual'] = _find_value_in_section(df, enhet_kst, kst_col, 72, 86, col_idx)

        return result

    except Exception as e:
        print(f"Fel vid läsning från Info-fliken för {enhet_kst}, {manad_str}: {e}")
        import traceback
        traceback.print_exc()
        return _empty_result()


def _find_value_in_section(df, enhet_kst, kst_col, start_row, end_row, value_col):
    """
    Hittar värde för en enhet i en sektion av Info-fliken

    Args:
        df: DataFrame med Info-fliken
        enhet_kst: '102', '103', '008', etc
        kst_col: Kolumn där KST finns (28)
        start_row: Startrad för sektionen
        end_row: Slutrad för sektionen
        value_col: Kolumn där värdet finns

    Returns:
        Värde som float eller int, eller 0 om inte hittat
    """
    for row_idx in range(start_row, end_row):
        if row_idx >= len(df):
            break

        kst_value = df.iloc[row_idx, kst_col]

        if pd.notna(kst_value):
            # Konvertera till string och jämför
            kst_str = str(int(kst_value)) if isinstance(kst_value, (int, float)) else str(kst_value)

            if kst_str == enhet_kst:
                # Hittade rätt rad! Läs värdet
                value = df.iloc[row_idx, value_col]
                if pd.notna(value):
                    return float(value) if isinstance(value, (int, float)) else 0
                else:
                    return 0

    return 0


def _empty_result():
    """Returnerar tom result med alla värden = 0"""
    return {
        'listning_actual': 0,
        'listningpoang_actual': 0,
        'acg_casemix_actual': 0,
        'huvudintakter_actual': 0,
        'medical_staff_actual': 0
    }


# Test-funktion
if __name__ == '__main__':
    # Testa för 102 (Frölunda Torg) - Mars 2026
    result = load_from_info_sheet('102', '2026-03')
    print('=== 102 Frölunda Torg - Mars 2026 ===')
    for key, value in result.items():
        print(f'{key}: {value}')

    print('\n=== 008 Stavre - Mars 2026 ===')
    result2 = load_from_info_sheet('008', '2026-03')
    for key, value in result2.items():
        print(f'{key}: {value}')
