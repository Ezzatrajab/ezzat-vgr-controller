"""
Super-enkel data loader - läser från INFO.xlsx
Skapad av Ezzat - perfekt struktur! 🎯
"""

import pandas as pd
import os


def load_all_kpi_from_info(enhet_kst, manad_str, base_path=None):
    """
    Hämtar ALL KPI-data från INFO.xlsx

    Args:
        enhet_kst: '102', '103', '008', '3', etc
        manad_str: '2026-01', '2026-02', '2026-03'
        base_path: Sökväg till mappen med INFO.xlsx (default: 'VGR Alla enheter')

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
            # Gå upp en nivå från Dashboard till VGR Alla enheter
            script_dir = os.path.dirname(os.path.abspath(__file__))
            base_path = os.path.dirname(script_dir)

        info_file = os.path.join(base_path, 'INFO.xlsx')

        if not os.path.exists(info_file):
            print(f"INFO.xlsx hittades inte: {info_file}")
            return _empty_result()

        # Läs hela Blad1 utan headers
        df = pd.read_excel(info_file, sheet_name='Blad1', header=None)

        # Konvertera månad till period (202601, 202602, 202603)
        year, month = manad_str.split('-')
        period = int(year + month)

        # Hitta kolumn-index för rätt period
        # Period finns i rad 0, kolumn 1 och framåt
        header_row = df.iloc[0, :]
        col_idx = None
        for i, val in enumerate(header_row):
            if pd.notna(val):
                try:
                    # Konvertera till int (hanterar både "202603" och "202603.0")
                    val_int = int(float(val))
                    if val_int == period:
                        col_idx = i
                        break
                except (ValueError, TypeError):
                    continue

        if col_idx is None:
            print(f"Period {period} hittades inte i INFO.xlsx")
            return _empty_result()

        # KST finns i kolumn 12
        kst_col = 12

        # Normalisera KST (ta bort leading zeros)
        target_kst = str(int(enhet_kst)) if enhet_kst.isdigit() else enhet_kst

        # Hitta värden från varje sektion
        result = {}

        # 1. ANTAL LISTADE PAT (rad 1-23)
        result['listning_actual'] = _find_value_in_section(
            df, target_kst, kst_col, 1, 24, col_idx
        )

        # 2. ANTAL LISTNINGPOÄNG (rad 25-46)
        result['listningpoang_actual'] = _find_value_in_section(
            df, target_kst, kst_col, 25, 47, col_idx
        )

        # 3. ACG CASEMIX (rad 48-69)
        result['acg_casemix_actual'] = _find_value_in_section(
            df, target_kst, kst_col, 48, 70, col_idx
        )

        # 4. HUVUDINTÄKTER (rad 71-92)
        result['huvudintakter_actual'] = _find_value_in_section(
            df, target_kst, kst_col, 71, 93, col_idx
        )

        # 5. MEDICAL STAFF (rad 94+)
        result['medical_staff_actual'] = _find_value_in_section(
            df, target_kst, kst_col, 94, len(df), col_idx
        )

        return result

    except Exception as e:
        print(f"Fel vid läsning från INFO.xlsx för {enhet_kst}, {manad_str}: {e}")
        import traceback
        traceback.print_exc()
        return _empty_result()


def _find_value_in_section(df, enhet_kst, kst_col, start_row, end_row, value_col):
    """
    Hittar värde för en enhet i en sektion

    Args:
        df: DataFrame med INFO.xlsx Blad1
        enhet_kst: '102', '3', '8', etc (normaliserat utan leading zeros)
        kst_col: Kolumn där KST finns (12)
        start_row: Startrad för sektionen
        end_row: Slutrad för sektionen
        value_col: Kolumn där värdet finns

    Returns:
        Värde som float eller int, eller 0 om inte hittat
    """
    for row_idx in range(start_row, min(end_row, len(df))):
        kst_value = df.iloc[row_idx, kst_col]

        if pd.notna(kst_value):
            # Normalisera KST från filen (ta bort leading zeros)
            if isinstance(kst_value, (int, float)):
                kst_str = str(int(kst_value))
            else:
                # String KST (t.ex. "003", "008") - ta bort leading zeros
                kst_str = str(kst_value).strip().lstrip('0') or '0'

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
    # Testa för olika enheter - Mars 2026
    test_enheter = [
        ('102', 'Frölunda Torg'),
        ('8', 'Stavre'),
        ('3', 'Brålanda-Torpa'),
        ('305', 'Tanum')
    ]

    for kst, namn in test_enheter:
        print(f'\n=== {kst} - {namn} - Mars 2026 ===')
        result = load_all_kpi_from_info(kst, '2026-03')
        for key, value in result.items():
            print(f'  {key}: {value}')
