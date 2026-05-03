"""
INFO.xlsx Loader - Centraliserad datakälla för Ezzat's Controlling System
Skapad: 2026-05-03
Syfte: Läsa ALLA data från INFO.xlsx istället för separata filer
"""

import pandas as pd
import os
from typing import Dict, Tuple, Optional


# ========================================
# ORG-MAPPNINGAR
# ========================================

def load_org_mappings(base_path=None) -> Dict[str, Dict[str, str]]:
    """
    Läser Org-fliken från INFO.xlsx och skapar mappningar.

    Returns:
        dict: {
            'kst_to_enhet': {'102': 'Frölunda Torg', '103': 'Grimmered', ...},
            'enhet_to_kst': {'Frölunda Torg': '102', 'Grimmered': '103', ...},
            'kst_to_vec': {'102': 'Anna Victorin', '103': 'Anna Victorin', ...},
            'kst_to_full_name': {'102': 'VC Frölunda Torg', '601': 'Rehab Frölunda Torg', ...}
        }
    """
    if base_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        base_path = os.path.dirname(script_dir)  # En nivå upp från Dashboard

    info_path = os.path.join(base_path, 'INFO.xlsx')

    # Läs Org-fliken
    df = pd.read_excel(info_path, sheet_name='Org', skiprows=4)

    # Byt namn på kolumner för enklare hantering
    df.columns = ['Empty', 'Enhetsnamn', 'KST', 'VEC']

    # Ta bort header-rader och NaN-rader
    df_clean = df[
        (df['Enhetsnamn'].notna()) &
        (df['KST'].notna()) &
        (df['Enhetsnamn'] != 'Enhetsnamn')  # Filtrera bort header
    ].copy()

    # Konvertera KST till string och ta bort .0
    df_clean['KST'] = df_clean['KST'].astype(str).str.replace('.0', '', regex=False)

    # Extrahera kort namn (ta bort "VC " och "Rehab " prefix)
    df_clean['KortNamn'] = df_clean['Enhetsnamn'].str.replace('VC ', '', regex=False).str.replace('Rehab ', '', regex=False)

    # Skapa mappningar
    mappings = {
        'kst_to_enhet': dict(zip(df_clean['KST'], df_clean['KortNamn'])),
        'enhet_to_kst': dict(zip(df_clean['KortNamn'], df_clean['KST'])),
        'kst_to_vec': dict(zip(df_clean['KST'], df_clean['VEC'])),
        'kst_to_full_name': dict(zip(df_clean['KST'], df_clean['Enhetsnamn']))
    }

    return mappings


def get_enhet_folder_name(kst: str, base_path=None) -> str:
    """
    Returnerar mappnamnet för en enhet baserat på KST.

    Args:
        kst: '102', '601', etc.
        base_path: Bas-sökväg (optional)

    Returns:
        str: Mappnamn t.ex. 'Frölunda Torg', 'Frölunda Torg Rehab'
    """
    mappings = load_org_mappings(base_path)
    full_name = mappings['kst_to_full_name'].get(kst, '')

    # Skapa mappnamn baserat på fullständigt namn
    if full_name.startswith('VC '):
        # VC-enheter: Ta bort "VC " prefix
        return full_name.replace('VC ', '')
    elif full_name.startswith('Rehab '):
        # Rehab-enheter: Byt ut "Rehab X" med "X Rehab"
        kort_namn = full_name.replace('Rehab ', '')
        return f"{kort_namn} Rehab"
    else:
        # Fallback
        return full_name


# ========================================
# KPI-DATA FRÅN INFO.xlsx
# ========================================

def load_acg_casemix_from_info(enhet_namn: str, manad_str: str, base_path=None) -> Optional[float]:
    """
    Läser ACG Casemix för en enhet och månad från INFO-fliken.

    Args:
        enhet_namn: 'Frölunda Torg', 'Åby', 'Karlastaden', etc. (KORT namn)
        manad_str: '2026-01', '2026-02', '2026-03', etc.
        base_path: Bas-sökväg (optional)

    Returns:
        float eller None om data saknas
    """
    if base_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        base_path = os.path.dirname(script_dir)

    info_path = os.path.join(base_path, 'INFO.xlsx')

    # Läs INFO-fliken
    df = pd.read_excel(info_path, sheet_name='INFO', header=None)

    # Hitta ACG Casemix sektion (rad 47)
    acg_row_idx = None
    for idx, row in df.iterrows():
        if pd.notna(row[0]) and 'ACG casemix' in str(row[0]):
            acg_row_idx = idx
            break

    if acg_row_idx is None:
        return None

    # Hitta månad-kolumn
    year, month = manad_str.split('-')
    manad_excel_format = int(f"{year}{month}")  # '2026-02' -> 202602

    header_row = df.iloc[acg_row_idx]
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

    # Mappning från kort namn till fullständigt namn i INFO-fliken
    # INFO-fliken använder "Omtanken Vårdcentral Frölunda Torg", inte bara "Frölunda Torg"
    enhet_name_mapping = {
        'Frölunda Torg': 'Omtanken Vårdcentral Frölunda Torg',
        'Grimmered': 'Omtanken Vårdcentral Grimmered',
        'Majorna': 'Omtanken Vårdcentral Majorna',
        'Landala': 'Omtanken Vårdcentral Landala',
        'Pedagogen Park': 'Omtanken Vårdcentral Pedagogen Park',
        'Åby': 'Omtanken Vårdcentral Åby',
        'Kviberg': 'Omtanken Vårdcentral Kviberg',
        'Olskroken': 'Omtanken Vårdcentral Olskroken',
        'Kållered': 'Omtanken Vårdcentral Kållered',
        'Avenyn': 'Kvarterskliniken Avenyn',
        'Lorensberg': 'Kvarterskliniken Lorensberg',
        'Husaren': 'Kvarterskliniken Husaren',
        'Karlastaden': 'Kvarterskliniken Karlastaden',
        'Tanum': 'Kvarterskliniken Tanum',
        'City VC': 'Citysjukhuset Plus 7 vårdcentral',
        'Torpa': 'Medpro Clinic Brålanda-Torpa Vårdcentral',
        'Noltorp': 'Medpro Clinic Noltorp Vårdcentral',
        'Lilla Edet': 'Medpro Clinic Lilla Edet Vårdcentral',
        'Stavre': 'Medpro Clinic Stavre Vårdcentral',
        'Åmål': 'Medpro Clinic Åmål Vårdcentral',
    }

    full_name = enhet_name_mapping.get(enhet_namn, enhet_namn)

    # Sök efter enheten
    for idx in range(acg_row_idx + 1, len(df)):
        cell_value = df.iloc[idx, 0]
        if pd.isna(cell_value):
            break  # Slut på ACG sektion

        if str(cell_value).strip() == full_name:
            value = df.iloc[idx, manad_col_idx]
            try:
                return float(value) if pd.notna(value) else None
            except (ValueError, TypeError):
                return None

    return None


def load_kpi_from_info(kpi_name: str, enhet_namn: str, manad_str: str, base_path=None) -> Optional[float]:
    """
    Läser specifik KPI för en enhet och månad från KPI-fliken.

    Args:
        kpi_name: 'Listning', 'Teambesök / VGR', 'Rehab Poäng'
        enhet_namn: 'Frölunda Torg', 'Åby', 'Karlastaden', etc. (KORT namn utan VC/Rehab)
        manad_str: '2026-01', '2026-02', '2026-03', etc.
        base_path: Bas-sökväg (optional)

    Returns:
        float eller None om data saknas
    """
    if base_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        base_path = os.path.dirname(script_dir)

    info_path = os.path.join(base_path, 'INFO.xlsx')

    # Läs KPI-fliken
    df = pd.read_excel(info_path, sheet_name='KPI', header=None)

    # Hitta vilken rad som innehåller KPI-namnet
    kpi_row_idx = None
    for idx, row in df.iterrows():
        if row[0] == kpi_name:
            kpi_row_idx = idx
            break

    if kpi_row_idx is None:
        return None

    # Hitta vilken kolumn som matchar månaden
    # Format i Excel: 202602 = 2026-02, 202603 = 2026-03
    year, month = manad_str.split('-')
    manad_excel_format = int(f"{year}{month}")  # '2026-02' -> 202602

    # Header-raden är kpi_row_idx, månaderna börjar från kolumn 2
    header_row = df.iloc[kpi_row_idx]

    manad_col_idx = None
    for col_idx in range(2, len(header_row)):
        try:
            if int(header_row[col_idx]) == manad_excel_format:
                manad_col_idx = col_idx
                break
        except (ValueError, TypeError):
            continue

    if manad_col_idx is None:
        return None

    # Hitta rad med enhetsnamnet (börjar efter KPI header-raden)
    for idx in range(kpi_row_idx + 1, len(df)):
        cell_value = df.iloc[idx, 0]
        if pd.isna(cell_value):
            break  # Slut på denna KPI-sektion

        if str(cell_value).strip() == enhet_namn:
            value = df.iloc[idx, manad_col_idx]
            try:
                return float(value) if pd.notna(value) else None
            except (ValueError, TypeError):
                return None

    return None


def load_all_kpi_for_enhet(kst: str, manad_str: str, base_path=None) -> Dict[str, Optional[float]]:
    """
    Hämtar ALLA KPIer för en enhet från INFO.xlsx.

    LOGIK:
    - VC-enheter (KST < 600): Hämtar Listning + ACG Casemix
    - Rehab-enheter (KST >= 600): Hämtar TeamBesök + Rehab Poäng

    Args:
        kst: '102', '601', etc.
        manad_str: '2026-01', '2026-02', etc.
        base_path: Bas-sökväg (optional)

    Returns:
        dict: {
            'listning': float eller None (bara för VC),
            'acg_casemix': float eller None (bara för VC),
            'teambesok': float eller None (bara för Rehab),
            'rehab_poang': float eller None (bara för Rehab)
        }
    """
    # Hämta kort enhetsnamn från mappningar
    mappings = load_org_mappings(base_path)
    enhet_namn = mappings['kst_to_enhet'].get(kst)

    if not enhet_namn:
        return {'listning': None, 'acg_casemix': None, 'teambesok': None, 'rehab_poang': None}

    # Hantera specialfall för kombinerade enheter
    # Åby-Kållered (108-109) och Avenyn-Lorensberg (302-303)
    if kst == '108-109':
        # Summera Åby + Kållered (båda VC)
        aby_data = load_all_kpi_for_enhet('108', manad_str, base_path)
        kallered_data = load_all_kpi_for_enhet('109', manad_str, base_path)

        # Beräkna vägt genomsnitt för ACG Casemix
        aby_listning = aby_data.get('listning') or 0
        kallered_listning = kallered_data.get('listning') or 0
        total_listning = aby_listning + kallered_listning

        if total_listning > 0:
            acg_vagt = (
                (aby_data.get('acg_casemix') or 0) * aby_listning +
                (kallered_data.get('acg_casemix') or 0) * kallered_listning
            ) / total_listning
        else:
            acg_vagt = None

        return {
            'listning': total_listning if total_listning > 0 else None,
            'acg_casemix': acg_vagt,
            'teambesok': None,
            'rehab_poang': None
        }

    if kst == '302-303':
        # Summera Avenyn + Lorensberg (båda VC)
        avenyn_data = load_all_kpi_for_enhet('302', manad_str, base_path)
        lorensberg_data = load_all_kpi_for_enhet('303', manad_str, base_path)

        # Beräkna vägt genomsnitt för ACG Casemix
        avenyn_listning = avenyn_data.get('listning') or 0
        lorensberg_listning = lorensberg_data.get('listning') or 0
        total_listning = avenyn_listning + lorensberg_listning

        if total_listning > 0:
            acg_vagt = (
                (avenyn_data.get('acg_casemix') or 0) * avenyn_listning +
                (lorensberg_data.get('acg_casemix') or 0) * lorensberg_listning
            ) / total_listning
        else:
            acg_vagt = None

        return {
            'listning': total_listning if total_listning > 0 else None,
            'acg_casemix': acg_vagt,
            'teambesok': None,
            'rehab_poang': None
        }

    # Bestäm om det är VC eller Rehab baserat på KST
    try:
        kst_num = int(kst)
        is_rehab = kst_num >= 600
    except ValueError:
        # Om KST inte är nummer (t.ex. kombinerade), gissa baserat på namn
        is_rehab = 'rehab' in mappings['kst_to_full_name'].get(kst, '').lower()

    # Läs rätt KPIer baserat på enhet-typ
    if is_rehab:
        # Rehab-enheter: TeamBesök + Rehab Poäng
        return {
            'listning': None,
            'acg_casemix': None,
            'teambesok': load_kpi_from_info('Teambesök / VGR', enhet_namn, manad_str, base_path),
            'rehab_poang': load_kpi_from_info('Rehab Poäng', enhet_namn, manad_str, base_path)
        }
    else:
        # VC-enheter: Listning + ACG Casemix
        return {
            'listning': load_kpi_from_info('Listning', enhet_namn, manad_str, base_path),
            'acg_casemix': load_acg_casemix_from_info(enhet_namn, manad_str, base_path),
            'teambesok': None,
            'rehab_poang': None
        }


# ========================================
# BYGG ENHETER_DATA FÖR STREAMLIT APP
# ========================================

def build_enheter_data(base_path=None) -> Dict[str, Dict]:
    """
    Bygger ENHETER_DATA dictionary för Streamlit-appen från INFO.xlsx Org-flik.

    Läser region direkt från Excel-filens struktur (REGION: STOR-GÖTEBORG / REGION: TÄTORT).

    Returns:
        dict: {
            'KST': {
                'enhet_namn': str,
                'typ': 'VC' eller 'Rehab',
                'vec': str,
                'region': 'Stor-Göteborg' eller 'Tätort',
                'månader': {}
            }
        }
    """
    if base_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        base_path = os.path.dirname(script_dir)

    info_path = os.path.join(base_path, 'INFO.xlsx')

    # Läs hela Org-fliken utan skiprows för att kunna läsa region-headers
    df = pd.read_excel(info_path, sheet_name='Org', header=None)

    # Bygg ENHETER_DATA
    enheter_data = {}
    current_region = None

    for i, row in df.iterrows():
        # Kolla om detta är en region-header
        if pd.notna(row[1]) and str(row[1]).startswith('REGION:'):
            # Extrahera region-namn (REGION: STOR-GÖTEBORG → Stor-Göteborg)
            region_text = str(row[1]).replace('REGION:', '').strip()
            if 'STOR' in region_text.upper():
                current_region = 'Stor-Göteborg'
            elif 'TÄTORT' in region_text.upper() or 'TATORT' in region_text.upper():
                current_region = 'Tätort'
            continue

        # Kolla om detta är en header-rad (Enhetsnamn, KST, VEC)
        if pd.notna(row[1]) and row[1] == 'Enhetsnamn':
            continue

        # Kolla om detta är en enhet
        if pd.notna(row[1]) and pd.notna(row[2]) and current_region:
            full_name = row[1]
            kst = str(row[2]).replace('.0', '')
            vec = row[3] if pd.notna(row[3]) else 'VEC saknas'

            # Bestäm typ (VC eller Rehab)
            if full_name.startswith('Rehab '):
                typ = 'Rehab'
                enhet_namn = full_name.replace('Rehab ', '') + ' Rehab'
            elif full_name.startswith('VC '):
                typ = 'VC'
                enhet_namn = full_name.replace('VC ', '')
            else:
                # Fallback
                try:
                    typ = 'VC' if int(kst) < 600 else 'Rehab'
                except ValueError:
                    typ = 'VC'
                enhet_namn = full_name

            enheter_data[kst] = {
                'enhet_namn': enhet_namn,
                'typ': typ,
                'vec': vec,
                'region': current_region,
                'månader': {'2026-01': {}, '2026-02': {}, '2026-03': {}}
            }

    return enheter_data


# ========================================
# TEST-FUNKTIONER
# ========================================

if __name__ == "__main__":
    # Test mappningar
    print("=== TEST ORG MAPPNINGAR ===")
    mappings = load_org_mappings()
    print(f"Totalt antal enheter: {len(mappings['kst_to_enhet'])}")
    print(f"\nExempel KST till Enhet: {list(mappings['kst_to_enhet'].items())[:5]}")
    print(f"\nExempel KST till VEC: {list(mappings['kst_to_vec'].items())[:5]}")

    # Test mappnamn
    print("\n=== TEST MAPPNAMN ===")
    test_kst = ['102', '601', '108', '302', '003', '703']
    for kst in test_kst:
        folder = get_enhet_folder_name(kst)
        print(f"KST {kst} till Mapp: '{folder}'")

    # Test KPI-data
    print("\n=== TEST KPI-DATA ===")
    test_data = load_all_kpi_for_enhet('102', '2026-03')
    print(f"Frölunda Torg (102) Mars 2026: {test_data}")

    test_data2 = load_all_kpi_for_enhet('601', '2026-03')
    print(f"Frölunda Torg Rehab (601) Mars 2026: {test_data2}")
