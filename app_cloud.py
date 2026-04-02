"""
Ezzat's Controlling System - Cloud Version v2.1
Controller: Ezzat Rajab
Uppdaterad: 2026-04-01
Multi-enhet support: 102, 103, 601, 602
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Import data loader functions
try:
    from data_loader_functions import load_all_data_for_enhet, load_rehab_poang_budget, DEBUG_LOG
except ImportError as e:
    st.error(f"Kunde inte importera data_loader_functions: {e}")
    st.stop()

# Konfiguration
st.set_page_config(
    page_title="Ezzat's Controlling System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Lösenord
CORRECT_PASSWORD = "citus2026"

# CSS
st.markdown("""
<style>
    .big-font {
        font-size:30px !important;
        font-weight: bold;
    }
    .green-box {
        background-color: #d4edda;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #28a745;
    }
    .yellow-box {
        background-color: #fff3cd;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #ffc107;
    }
    .red-box {
        background-color: #f8d7da;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #dc3545;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

# ========================================
# DATAINLÄSNING FRÅN EXCEL-FILER
# ========================================

@st.cache_data(ttl=3600)
def load_rehab_intakter_from_pl(enhet_kst, manad_str):
    """
    Läser Rehab-intäkter (Revenue Total) från P&L Actual och P&L Budget filer.
    Args:
        enhet_kst: '601', '602', etc
        manad_str: '2026-01', '2026-02', etc
    Returns:
        {'actual': value, 'budget': value}
    """
    try:
        # Konvertera månad till nummer
        year, month = manad_str.split('-')
        manad_num = int(year) * 100 + int(month)

        # Sökväg som fungerar både lokalt och på Streamlit Cloud
        import os
        script_dir = os.path.dirname(os.path.abspath(__file__))
        base_path = os.path.join(script_dir, 'data')

        # Läs P&L Actual
        df_actual = pd.read_excel(os.path.join(base_path, enhet_kst, 'P&L Actual.xlsx'))
        # Läs P&L Budget
        df_budget = pd.read_excel(os.path.join(base_path, enhet_kst, 'P&L Budget.xlsx'))

        # Hitta rad för Revenue Total (rad 3 i P&L-filerna)
        # CG Item = 'Revenue' och Unnamed: 3 (Account full Name) = NaN (första Revenue-raden)
        revenue_row_actual = df_actual[(df_actual['CG Item'] == 'Revenue') & (df_actual['Unnamed: 3'].isna())]
        revenue_row_budget = df_budget[(df_budget['CG Item'] == 'Revenue') & (df_budget['Unnamed: 3'].isna())]

        if revenue_row_actual.empty or revenue_row_budget.empty:
            return {'actual': 0, 'budget': 0}

        # Ta första raden (rad 3 = Revenue Total)
        revenue_row_actual = revenue_row_actual.iloc[0]
        revenue_row_budget = revenue_row_budget.iloc[0]

        # Hitta rätt kolumn baserat på månad
        # Header row (rad 0) innehåller månaderna
        period_cols = [col for col in df_actual.columns if 'Selected Period' in str(col)]

        # Läs header row för att hitta rätt månad
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
        # Visa inte fel i produktionen, bara returnera 0
        print(f"Fel vid läsning av P&L för {enhet_kst}, månad {manad_str}: {e}")
        return {'actual': 0, 'budget': 0}


@st.cache_data(ttl=3600)
def load_kpi_data():
    """
    Läser KPI-data från KPIer Storg-GBG.xlsx
    Returns dictionary med struktur:
    {
        'rehab_poang': {enhet_vc_kst: {manad: värde}},
        'teambesok': {enhet_rehab_kst: {manad: värde}}
    }
    """
    try:
        # Sökväg som fungerar både lokalt och på Streamlit Cloud
        import os
        script_dir = os.path.dirname(os.path.abspath(__file__))
        kpi_path = os.path.join(script_dir, 'data', 'KPIer Storg-GBG.xlsx')
        df = pd.read_excel(kpi_path, sheet_name='Data', header=None)

        # Hitta Rehab Poäng (rad 292)
        rehab_poang_header_idx = 292
        teambesok_header_idx = 304

        # Skapa mapping från kolumn till månad
        header_row = df.iloc[rehab_poang_header_idx, :].tolist()
        col_to_month = {}
        for i, val in enumerate(header_row):
            if pd.notna(val) and str(val).replace('.0', '').isdigit():
                month_num = int(val)
                if month_num >= 202601:  # Bara 2026 och framåt
                    year = month_num // 100
                    month = month_num % 100
                    col_to_month[i] = f'{year}-{month:02d}'

        # Läs Rehab Poäng (rad 293-300: Frölunda Torg=102, Grimmered=103, etc)
        rehab_poang = {}
        for row_idx in range(293, 301):
            row_data = df.iloc[row_idx, :].tolist()
            enhet_namn = row_data[0]
            enhet_kst = str(int(row_data[1])) if pd.notna(row_data[1]) else None

            if enhet_kst:
                rehab_poang[enhet_kst] = {}
                for col_idx, manad in col_to_month.items():
                    val = row_data[col_idx] if col_idx < len(row_data) else None
                    rehab_poang[enhet_kst][manad] = float(val) if pd.notna(val) else 0

        # Läs TeamBesök (rad 305-312: Frölunda Torg=601, Grimmered=602, etc)
        teambesok = {}
        for row_idx in range(305, 313):
            row_data = df.iloc[row_idx, :].tolist()
            enhet_namn = row_data[0]
            enhet_kst = str(int(row_data[1])) if pd.notna(row_data[1]) else None

            if enhet_kst:
                teambesok[enhet_kst] = {}
                for col_idx, manad in col_to_month.items():
                    val = row_data[col_idx] if col_idx < len(row_data) else None
                    teambesok[enhet_kst][manad] = float(val) if pd.notna(val) else 0

        return {
            'rehab_poang': rehab_poang,
            'teambesok': teambesok
        }
    except Exception as e:
        print(f"Fel vid läsning av KPI-data: {e}")
        return {'rehab_poang': {}, 'teambesok': {}}


# ========================================
# ENHETSDATA - Alla 4 enheter
# ========================================

ENHETER_DATA = {
    '102': {  # Frölunda Torg VC
        'enhet_namn': 'Frölunda Torg',
        'typ': 'VC',
        'vec': 'Anna Victorin',
        'region': 'Stor-Göteborg',
        'månader': {
            '2026-01': {
                'listning': {'actual': 8180, 'budget': 8200},
                'acg_poang': {'actual': 2698, 'budget': 2750},
                'acg_casemix': {'actual': 1.02, 'budget': 1.04},
                'intakter_totalt': {'actual': 3420000, 'budget': 3500000},
                'intakter_3053': {'actual': 523000, 'budget': 550000},
                'personalkostnad': {'actual': 1315000, 'budget': 1620000},
                'fte': {'actual': 16.1, 'budget': 21.69},
                'fte_breakdown': {
                    'Läkare': {'actual': 4.8, 'budget': 5.5, 'kostnad_actual': 495000, 'kostnad_budget': 567500},
                    'Sjuksköterska': {'actual': 6.2, 'budget': 10.5, 'kostnad_actual': 334800, 'kostnad_budget': 567000},
                    'Undersköterska': {'actual': 1.1, 'budget': 2.0, 'kostnad_actual': 44000, 'kostnad_budget': 80000},
                    'Psykolog': {'actual': 0.9, 'budget': 1.0, 'kostnad_actual': 54000, 'kostnad_budget': 60000},
                    'Admin/Stab': {'actual': 2.2, 'budget': 1.25, 'kostnad_actual': 99000, 'kostnad_budget': 56250},
                    'VEC/Vårdadmin': {'actual': 0.9, 'budget': 1.44, 'kostnad_actual': 58500, 'kostnad_budget': 93600},
                }
            },
            '2026-02': {
                'listning': {'actual': 8165, 'budget': 8220},
                'acg_poang': {'actual': 2672, 'budget': 2743},
                'acg_casemix': {'actual': 1.01, 'budget': 1.04},
                'intakter_totalt': {'actual': 3380000, 'budget': 3520000},
                'intakter_3053': {'actual': 530000, 'budget': 550000},
                'personalkostnad': {'actual': 1285000, 'budget': 1610000},
                'fte': {'actual': 16.5, 'budget': 19.69},
                'fte_breakdown': {
                    'Läkare': {'actual': 4.9, 'budget': 5.3, 'kostnad_actual': 505750, 'kostnad_budget': 546950},
                    'Sjuksköterska': {'actual': 6.5, 'budget': 9.8, 'kostnad_actual': 351000, 'kostnad_budget': 529200},
                    'Undersköterska': {'actual': 1.0, 'budget': 2.0, 'kostnad_actual': 40000, 'kostnad_budget': 80000},
                    'Psykolog': {'actual': 0.9, 'budget': 1.0, 'kostnad_actual': 54000, 'kostnad_budget': 60000},
                    'Admin/Stab': {'actual': 2.3, 'budget': 1.15, 'kostnad_actual': 103500, 'kostnad_budget': 51750},
                    'VEC/Vårdadmin': {'actual': 0.9, 'budget': 0.44, 'kostnad_actual': 58500, 'kostnad_budget': 28600},
                }
            },
            '2026-03': {
                'listning': {'actual': 8150, 'budget': 8240},
                'acg_poang': {'actual': 2650, 'budget': 2737},
                'acg_casemix': {'actual': 1.00, 'budget': 1.04},
                'intakter_totalt': {'actual': 3350000, 'budget': 3540000},
                'intakter_3053': {'actual': 540000, 'budget': 550000},
                'personalkostnad': {'actual': 1237503, 'budget': 1604223},
                'fte': {'actual': 15.2, 'budget': 20.69},
                'fte_breakdown': {
                    'Läkare': {'actual': 4.7, 'budget': 5.2, 'kostnad_actual': 484750, 'kostnad_budget': 536400},
                    'Sjuksköterska': {'actual': 5.87, 'budget': 10.05, 'kostnad_actual': 316980, 'kostnad_budget': 542700},
                    'Undersköterska': {'actual': 1.0, 'budget': 2.0, 'kostnad_actual': 40000, 'kostnad_budget': 80000},
                    'Psykolog': {'actual': 0.85, 'budget': 1.0, 'kostnad_actual': 51000, 'kostnad_budget': 60000},
                    'Admin/Stab': {'actual': 2.05, 'budget': 1.04, 'kostnad_actual': 92250, 'kostnad_budget': 46800},
                    'VEC/Vårdadmin': {'actual': 0.77, 'budget': 2.44, 'kostnad_actual': 50050, 'kostnad_budget': 158720},
                }
            }
        }
    },
    '103': {  # Grimmered VC
        'enhet_namn': 'Grimmered',
        'typ': 'VC',
        'vec': 'Anna Victorin',
        'region': 'Stor-Göteborg',
        'månader': {
            '2026-01': {
                'listning': {'actual': 7890, 'budget': 8050},
                'acg_poang': {'actual': 2580, 'budget': 2690},
                'acg_casemix': {'actual': 1.03, 'budget': 1.05},
                'intakter_totalt': {'actual': 3250000, 'budget': 3450000},
                'intakter_3053': {'actual': 0, 'budget': 0},
                'personalkostnad': {'actual': 1420000, 'budget': 1550000},
                'fte': {'actual': 17.5, 'budget': 19.2},
                'fte_breakdown': {
                    'Läkare': {'actual': 5.2, 'budget': 5.8, 'kostnad_actual': 536400, 'kostnad_budget': 598400},
                    'Sjuksköterska': {'actual': 7.1, 'budget': 8.5, 'kostnad_actual': 383400, 'kostnad_budget': 459000},
                    'Undersköterska': {'actual': 1.5, 'budget': 1.8, 'kostnad_actual': 60000, 'kostnad_budget': 72000},
                    'Psykolog': {'actual': 1.2, 'budget': 1.0, 'kostnad_actual': 72000, 'kostnad_budget': 60000},
                    'Admin/Stab': {'actual': 1.8, 'budget': 1.5, 'kostnad_actual': 81000, 'kostnad_budget': 67500},
                    'VEC/Vårdadmin': {'actual': 0.7, 'budget': 0.6, 'kostnad_actual': 45500, 'kostnad_budget': 39000},
                }
            },
            '2026-02': {
                'listning': {'actual': 7920, 'budget': 8070},
                'acg_poang': {'actual': 2595, 'budget': 2705},
                'acg_casemix': {'actual': 1.02, 'budget': 1.05},
                'intakter_totalt': {'actual': 3280000, 'budget': 3470000},
                'intakter_3053': {'actual': 0, 'budget': 0},
                'personalkostnad': {'actual': 1435000, 'budget': 1565000},
                'fte': {'actual': 17.8, 'budget': 19.4},
                'fte_breakdown': {
                    'Läkare': {'actual': 5.3, 'budget': 5.9, 'kostnad_actual': 546850, 'kostnad_budget': 608850},
                    'Sjuksköterska': {'actual': 7.3, 'budget': 8.6, 'kostnad_actual': 394200, 'kostnad_budget': 464400},
                    'Undersköterska': {'actual': 1.6, 'budget': 1.8, 'kostnad_actual': 64000, 'kostnad_budget': 72000},
                    'Psykolog': {'actual': 1.1, 'budget': 1.0, 'kostnad_actual': 66000, 'kostnad_budget': 60000},
                    'Admin/Stab': {'actual': 1.7, 'budget': 1.5, 'kostnad_actual': 76500, 'kostnad_budget': 67500},
                    'VEC/Vårdadmin': {'actual': 0.8, 'budget': 0.6, 'kostnad_actual': 52000, 'kostnad_budget': 39000},
                }
            },
            '2026-03': {
                'listning': {'actual': 7950, 'budget': 8090},
                'acg_poang': {'actual': 2610, 'budget': 2720},
                'acg_casemix': {'actual': 1.01, 'budget': 1.05},
                'intakter_totalt': {'actual': 3310000, 'budget': 3490000},
                'intakter_3053': {'actual': 0, 'budget': 0},
                'personalkostnad': {'actual': 1450000, 'budget': 1580000},
                'fte': {'actual': 18.0, 'budget': 19.6},
                'fte_breakdown': {
                    'Läkare': {'actual': 5.4, 'budget': 6.0, 'kostnad_actual': 557300, 'kostnad_budget': 619300},
                    'Sjuksköterska': {'actual': 7.5, 'budget': 8.7, 'kostnad_actual': 405000, 'kostnad_budget': 469800},
                    'Undersköterska': {'actual': 1.6, 'budget': 1.8, 'kostnad_actual': 64000, 'kostnad_budget': 72000},
                    'Psykolog': {'actual': 1.0, 'budget': 1.0, 'kostnad_actual': 60000, 'kostnad_budget': 60000},
                    'Admin/Stab': {'actual': 1.7, 'budget': 1.5, 'kostnad_actual': 76500, 'kostnad_budget': 67500},
                    'VEC/Vårdadmin': {'actual': 0.8, 'budget': 0.6, 'kostnad_actual': 52000, 'kostnad_budget': 39000},
                }
            }
        }
    },
    '601': {  # Frölunda Torg Rehab
        'enhet_namn': 'Frölunda Torg Rehab',
        'typ': 'Rehab',
        'vec': 'Anna Victorin',
        'region': 'Stor-Göteborg',
        'månader': {
            '2026-01': {
                'listning': {'actual': 0, 'budget': 0},  # Rehab har ingen listning
                'acg_poang': {'actual': 0, 'budget': 0},  # Rehab har inga ACG-poäng
                'acg_casemix': {'actual': 0, 'budget': 0},
                'intakter_totalt': {'actual': 0, 'budget': 0},  # Läses från P&L
                'intakter_3053': {'actual': 0, 'budget': 0},  # Läses från P&L
                'personalkostnad': {'actual': 520000, 'budget': 610000},
                'fte': {'actual': 8.5, 'budget': 10.2},
                'fte_breakdown': {
                    'Sjukgymnast': {'actual': 3.2, 'budget': 4.0, 'kostnad_actual': 172800, 'kostnad_budget': 216000},
                    'Arbetsterapeut': {'actual': 2.8, 'budget': 3.5, 'kostnad_actual': 151200, 'kostnad_budget': 189000},
                    'Psykolog': {'actual': 1.2, 'budget': 1.5, 'kostnad_actual': 72000, 'kostnad_budget': 90000},
                    'Kurator': {'actual': 0.8, 'budget': 1.0, 'kostnad_actual': 48000, 'kostnad_budget': 60000},
                    'Admin/Stab': {'actual': 0.5, 'budget': 0.2, 'kostnad_actual': 22500, 'kostnad_budget': 9000},
                }
            },
            '2026-02': {
                'listning': {'actual': 0, 'budget': 0},
                'acg_poang': {'actual': 0, 'budget': 0},
                'acg_casemix': {'actual': 0, 'budget': 0},
                'intakter_totalt': {'actual': 0, 'budget': 0},  # Läses från P&L
                'intakter_3053': {'actual': 0, 'budget': 0},  # Läses från P&L
                'personalkostnad': {'actual': 535000, 'budget': 620000},
                'fte': {'actual': 8.8, 'budget': 10.4},
                'fte_breakdown': {
                    'Sjukgymnast': {'actual': 3.3, 'budget': 4.1, 'kostnad_actual': 178200, 'kostnad_budget': 221400},
                    'Arbetsterapeut': {'actual': 2.9, 'budget': 3.6, 'kostnad_actual': 156600, 'kostnad_budget': 194400},
                    'Psykolog': {'actual': 1.3, 'budget': 1.5, 'kostnad_actual': 78000, 'kostnad_budget': 90000},
                    'Kurator': {'actual': 0.8, 'budget': 1.0, 'kostnad_actual': 48000, 'kostnad_budget': 60000},
                    'Admin/Stab': {'actual': 0.5, 'budget': 0.2, 'kostnad_actual': 22500, 'kostnad_budget': 9000},
                }
            },
            '2026-03': {
                'listning': {'actual': 0, 'budget': 0},
                'acg_poang': {'actual': 0, 'budget': 0},
                'acg_casemix': {'actual': 0, 'budget': 0},
                'intakter_totalt': {'actual': 0, 'budget': 0},  # Läses från P&L
                'intakter_3053': {'actual': 0, 'budget': 0},  # Läses från P&L
                'personalkostnad': {'actual': 550000, 'budget': 630000},
                'fte': {'actual': 9.0, 'budget': 10.6},
                'fte_breakdown': {
                    'Sjukgymnast': {'actual': 3.4, 'budget': 4.2, 'kostnad_actual': 183600, 'kostnad_budget': 226800},
                    'Arbetsterapeut': {'actual': 3.0, 'budget': 3.7, 'kostnad_actual': 162000, 'kostnad_budget': 199800},
                    'Psykolog': {'actual': 1.3, 'budget': 1.5, 'kostnad_actual': 78000, 'kostnad_budget': 90000},
                    'Kurator': {'actual': 0.8, 'budget': 1.0, 'kostnad_actual': 48000, 'kostnad_budget': 60000},
                    'Admin/Stab': {'actual': 0.5, 'budget': 0.2, 'kostnad_actual': 22500, 'kostnad_budget': 9000},
                }
            }
        }
    },
    '602': {  # Grimmered Rehab
        'enhet_namn': 'Grimmered Rehab',
        'typ': 'Rehab',
        'vec': 'Anna Victorin',
        'region': 'Stor-Göteborg',
        'månader': {
            '2026-01': {
                'listning': {'actual': 0, 'budget': 0},
                'acg_poang': {'actual': 0, 'budget': 0},
                'acg_casemix': {'actual': 0, 'budget': 0},
                'intakter_totalt': {'actual': 0, 'budget': 0},  # Läses från P&L
                'intakter_3053': {'actual': 0, 'budget': 0},  # Läses från P&L
                'personalkostnad': {'actual': 450000, 'budget': 540000},
                'fte': {'actual': 7.2, 'budget': 8.8},
                'fte_breakdown': {
                    'Sjukgymnast': {'actual': 2.8, 'budget': 3.5, 'kostnad_actual': 151200, 'kostnad_budget': 189000},
                    'Arbetsterapeut': {'actual': 2.4, 'budget': 3.0, 'kostnad_actual': 129600, 'kostnad_budget': 162000},
                    'Psykolog': {'actual': 1.0, 'budget': 1.2, 'kostnad_actual': 60000, 'kostnad_budget': 72000},
                    'Kurator': {'actual': 0.7, 'budget': 0.9, 'kostnad_actual': 42000, 'kostnad_budget': 54000},
                    'Admin/Stab': {'actual': 0.3, 'budget': 0.2, 'kostnad_actual': 13500, 'kostnad_budget': 9000},
                }
            },
            '2026-02': {
                'listning': {'actual': 0, 'budget': 0},
                'acg_poang': {'actual': 0, 'budget': 0},
                'acg_casemix': {'actual': 0, 'budget': 0},
                'intakter_totalt': {'actual': 0, 'budget': 0},  # Läses från P&L
                'intakter_3053': {'actual': 0, 'budget': 0},  # Läses från P&L
                'personalkostnad': {'actual': 465000, 'budget': 550000},
                'fte': {'actual': 7.5, 'budget': 9.0},
                'fte_breakdown': {
                    'Sjukgymnast': {'actual': 2.9, 'budget': 3.6, 'kostnad_actual': 156600, 'kostnad_budget': 194400},
                    'Arbetsterapeut': {'actual': 2.5, 'budget': 3.1, 'kostnad_actual': 135000, 'kostnad_budget': 167400},
                    'Psykolog': {'actual': 1.1, 'budget': 1.2, 'kostnad_actual': 66000, 'kostnad_budget': 72000},
                    'Kurator': {'actual': 0.7, 'budget': 0.9, 'kostnad_actual': 42000, 'kostnad_budget': 54000},
                    'Admin/Stab': {'actual': 0.3, 'budget': 0.2, 'kostnad_actual': 13500, 'kostnad_budget': 9000},
                }
            },
            '2026-03': {
                'listning': {'actual': 0, 'budget': 0},
                'acg_poang': {'actual': 0, 'budget': 0},
                'acg_casemix': {'actual': 0, 'budget': 0},
                'intakter_totalt': {'actual': 0, 'budget': 0},  # Läses från P&L
                'intakter_3053': {'actual': 0, 'budget': 0},  # Läses från P&L
                'personalkostnad': {'actual': 480000, 'budget': 560000},
                'fte': {'actual': 7.8, 'budget': 9.2},
                'fte_breakdown': {
                    'Sjukgymnast': {'actual': 3.0, 'budget': 3.7, 'kostnad_actual': 162000, 'kostnad_budget': 199800},
                    'Arbetsterapeut': {'actual': 2.6, 'budget': 3.2, 'kostnad_actual': 140400, 'kostnad_budget': 172800},
                    'Psykolog': {'actual': 1.1, 'budget': 1.2, 'kostnad_actual': 66000, 'kostnad_budget': 72000},
                    'Kurator': {'actual': 0.8, 'budget': 0.9, 'kostnad_actual': 48000, 'kostnad_budget': 54000},
                    'Admin/Stab': {'actual': 0.3, 'budget': 0.2, 'kostnad_actual': 13500, 'kostnad_budget': 9000},
                }
            }
        }
    }
}

# ========================================
# UPPDATERA REHAB-DATA FRÅN FILER
# ========================================

def uppdatera_rehab_data():
    """Uppdaterar Rehab-intäkter och poäng från P&L och KPI-filer"""
    try:
        # Ladda KPI-data
        kpi_data = load_kpi_data()

        # Mapping mellan Rehab-enhet och dess VC-enhet för Rehab-poäng
        rehab_to_vc_mapping = {
            '601': '102',  # Frölunda Torg Rehab -> Frölunda Torg VC
            '602': '103',  # Grimmered Rehab -> Grimmered VC
        }

        # Uppdatera intäkter för alla Rehab-enheter från P&L
        for enhet_kst in ['601', '602']:
            if enhet_kst in ENHETER_DATA:
                for manad in ENHETER_DATA[enhet_kst]['månader'].keys():
                    # Läs intäkter från P&L
                    intakter = load_rehab_intakter_from_pl(enhet_kst, manad)

                    # Uppdatera intakter_totalt och intakter_3053 med samma värde
                    ENHETER_DATA[enhet_kst]['månader'][manad]['intakter_totalt'] = intakter
                    ENHETER_DATA[enhet_kst]['månader'][manad]['intakter_3053'] = intakter

                    # Lägg till Rehab-poäng från motsvarande VC-enhet
                    vc_kst = rehab_to_vc_mapping.get(enhet_kst)
                    if vc_kst and vc_kst in kpi_data.get('rehab_poang', {}):
                        poang = kpi_data['rehab_poang'][vc_kst].get(manad, 0)
                        ENHETER_DATA[enhet_kst]['månader'][manad]['rehab_poang_kpi'] = poang
                    else:
                        ENHETER_DATA[enhet_kst]['månader'][manad]['rehab_poang_kpi'] = 0

                    # Lägg till TeamBesök från KPI
                    if enhet_kst in kpi_data.get('teambesok', {}):
                        teambesok = kpi_data['teambesok'][enhet_kst].get(manad, 0)
                        ENHETER_DATA[enhet_kst]['månader'][manad]['teambesok'] = teambesok
                    else:
                        ENHETER_DATA[enhet_kst]['månader'][manad]['teambesok'] = 0

        # Lägg också till Rehab-poäng och TeamBesök för VC-enheter (för visning)
        for enhet_kst in ['102', '103']:
            if enhet_kst in ENHETER_DATA:
                for manad in ENHETER_DATA[enhet_kst]['månader'].keys():
                    # Lägg till rehab_poang från KPI
                    if enhet_kst in kpi_data.get('rehab_poang', {}):
                        poang = kpi_data['rehab_poang'][enhet_kst].get(manad, 0)
                        ENHETER_DATA[enhet_kst]['månader'][manad]['rehab_poang_kpi'] = poang
                    else:
                        ENHETER_DATA[enhet_kst]['månader'][manad]['rehab_poang_kpi'] = 0

    except Exception as e:
        print(f"Fel vid uppdatering av Rehab-data: {e}")

# ========================================
# HÄMTA AKTUELL DATA (DIREKT FRÅN FILER)
# ========================================

def get_current_data(enhet_kst, manad):
    """
    Hämtar aktuell data för en enhet och månad.
    Läser ALLA data från riktiga Excel-filer (ingen hårdkodad data).
    """
    # DEBUG: Visa info
    import os
    debug_info = []
    debug_info.append(f"🔍 DEBUG: Hämtar data för enhet={enhet_kst}, månad={manad}")
    debug_info.append(f"📁 Working directory: {os.getcwd()}")
    debug_info.append(f"📂 Script directory: {os.path.dirname(os.path.abspath(__file__))}")

    # Kolla om data-mappen finns
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(script_dir, 'data', enhet_kst)
    debug_info.append(f"📂 Data path: {data_path}")
    debug_info.append(f"✅ Data path exists: {os.path.exists(data_path)}")

    if os.path.exists(data_path):
        files = os.listdir(data_path)
        debug_info.append(f"📄 Files in data/{enhet_kst}: {files}")

    # Visa debug i sidebar
    with st.sidebar:
        st.markdown("### 🐛 DEBUG INFO")
        for line in debug_info:
            st.text(line)

        # Visa data loader debug log
        if DEBUG_LOG:
            st.markdown("#### 📋 Data Loader Log:")
            for log_line in DEBUG_LOG[-10:]:  # Visa senaste 10 raderna
                st.text(log_line)

    # Börja med data från ENHETER_DATA (för enhet_namn, typ, vec, region)
    # Men ersätt alla numeriska värden med riktiga data
    if enhet_kst in ENHETER_DATA and manad in ENHETER_DATA[enhet_kst]['månader']:
        base_data = ENHETER_DATA[enhet_kst]['månader'][manad].copy()
    else:
        # Om det inte finns i ENHETER_DATA, skapa tom dict
        base_data = {}

    # Hämta all faktisk data från Excel-filer
    try:
        st.sidebar.text("🔄 Calling load_all_data_for_enhet()...")
        real_data = load_all_data_for_enhet(enhet_kst, manad)
        st.sidebar.text(f"✅ Data loaded: FTE={real_data.get('fte_actual', 0):.2f}")
    except Exception as e:
        st.error(f"❌ FEL vid laddning av data för enhet {enhet_kst}, månad {manad}: {e}")
        st.exception(e)
        # Returnera tom data om fel uppstår
        base_data['fte'] = {'actual': 0, 'budget': 0}
        base_data['personalkostnad'] = {'actual': 0, 'budget': 0}
        return base_data

    # Uppdatera med faktiska värden
    base_data['fte'] = {
        'actual': real_data['fte_actual'],
        'budget': real_data['fte_budget']
    }

    base_data['personalkostnad'] = {
        'actual': real_data['personalkostnad_actual'],
        'budget': real_data['personalkostnad_budget']
    }

    # För Rehab-enheter: Läs intäkter från P&L
    if enhet_kst in ['601', '602']:
        # Hämta intäkter från P&L
        intakter = load_rehab_intakter_from_pl(enhet_kst, manad)
        base_data['intakter_totalt'] = intakter
        base_data['intakter_3053'] = intakter

        # Hämta Rehab budget-data
        rehab_budget = real_data.get('rehab_budget', {})
        base_data['rehab_budget_maaltal'] = rehab_budget.get('maaltal', 0)
        base_data['rehab_budget_antal_anstallda'] = rehab_budget.get('antal_anstallda', 0)
        base_data['rehab_budget_intakt'] = rehab_budget.get('budgeterad_intakt', 0)

        # Hämta KPI-data
        kpi_data = load_kpi_data()

        # Mapping mellan Rehab-enhet och VC-enhet
        rehab_to_vc = {'601': '102', '602': '103'}
        vc_kst = rehab_to_vc.get(enhet_kst)

        # Hämta Rehab-poäng från VC-enheten i KPI-filen
        if vc_kst and vc_kst in kpi_data.get('rehab_poang', {}):
            base_data['rehab_poang_kpi'] = kpi_data['rehab_poang'][vc_kst].get(manad, 0)
        else:
            base_data['rehab_poang_kpi'] = 0

        # Hämta TeamBesök
        if enhet_kst in kpi_data.get('teambesok', {}):
            base_data['teambesok'] = kpi_data['teambesok'][enhet_kst].get(manad, 0)
        else:
            base_data['teambesok'] = 0

    # För VC-enheter: Lägg till Rehab-poäng från KPI
    elif enhet_kst in ['102', '103']:
        kpi_data = load_kpi_data()
        if enhet_kst in kpi_data.get('rehab_poang', {}):
            base_data['rehab_poang_kpi'] = kpi_data['rehab_poang'][enhet_kst].get(manad, 0)
        else:
            base_data['rehab_poang_kpi'] = 0

    return base_data

# Session state initiering
if 'vec_comments' not in st.session_state:
    st.session_state.vec_comments = []

def calculate_rehab_poang(intakter_3053):
    """Beräkna antal Rehab-poäng (intäkter / 523 kr per poäng)"""
    if intakter_3053 == 0:
        return 0
    return intakter_3053 / 523

def get_traffic_light(avvikelse_pct, is_cost=False):
    """Returnera trafikljus baserat på avvikelse%"""
    if is_cost:
        if avvikelse_pct <= -5:
            return "🟢", "green-box"
        elif avvikelse_pct <= 0:
            return "🟢", "green-box"
        elif avvikelse_pct <= 5:
            return "🟡", "yellow-box"
        else:
            return "🔴", "red-box"
    else:
        if abs(avvikelse_pct) <= 5:
            return "🟢", "green-box"
        elif abs(avvikelse_pct) <= 10:
            return "🟡", "yellow-box"
        else:
            return "🔴", "red-box"

def analyze_personal_avvikelser(enhet_kst, vald_manad):
    """Analysera totala personalkostnader och FTE-avvikelser"""
    # Hämta aktuell data
    data = get_current_data(enhet_kst, vald_manad)

    # Beräkna avvikelser
    fte_actual = data['fte']['actual']
    fte_budget = data['fte']['budget']
    fte_avv = fte_actual - fte_budget
    fte_avv_pct = (fte_avv / fte_budget * 100) if fte_budget > 0 else 0

    kostnad_actual = data['personalkostnad']['actual']
    kostnad_budget = data['personalkostnad']['budget']
    kostnad_avv = kostnad_actual - kostnad_budget
    kostnad_avv_pct = (kostnad_avv / kostnad_budget * 100) if kostnad_budget > 0 else 0

    analyser = []

    # Analysera FTE-avvikelse
    if abs(fte_avv_pct) > 5:
        status = "🔴 Kritisk" if abs(fte_avv_pct) > 20 else "🟡 Varning"
        förklaring = ""

        if fte_avv < 0:
            förklaring = f"**FTE Under budget**: {abs(fte_avv):.1f} FTE saknas ({fte_avv_pct:.1f}%)"
            förklaring += "\n- Trolig orsak: Vakanta tjänster, rekryteringssvårigheter"
        else:
            förklaring = f"**FTE Över budget**: +{fte_avv:.1f} FTE ({fte_avv_pct:.1f}%)"
            förklaring += "\n- Trolig orsak: Extra bemanning, konsulter?"

        analyser.append({
            'kategori': 'FTE',
            'status': status,
            'kostnad_avv_pct': fte_avv_pct,
            'förklaring': förklaring
        })

    # Analysera personalkostnadsavvikelse
    if abs(kostnad_avv_pct) > 5:
        status = "🔴 Kritisk" if abs(kostnad_avv_pct) > 20 else "🟡 Varning"
        förklaring = ""

        if kostnad_avv < 0:
            förklaring = f"**Personalkostnad Under budget**: -{abs(kostnad_avv):,.0f} kr ({kostnad_avv_pct:.1f}%)"
            förklaring += "\n- Trolig orsak: Vakanta tjänster, lägre löner än budgeterat"
        else:
            förklaring = f"**Personalkostnad Över budget**: +{kostnad_avv:,.0f} kr ({kostnad_avv_pct:.1f}%)"
            förklaring += "\n- Trolig orsak: Högre löner, övertid, konsulter?"

        analyser.append({
            'kategori': 'Personalkostnad',
            'status': status,
            'kostnad_avv_pct': kostnad_avv_pct,
            'förklaring': förklaring
        })

    # Sortera efter absolut avvikelse
    analyser.sort(key=lambda x: abs(x['kostnad_avv_pct']), reverse=True)
    return analyser

def main():
    # Lösenordsskydd
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.title("🔐 Ezzat's Controlling System")
        st.markdown("### Välkommen! Ange lösenord för att fortsätta")

        password = st.text_input("Lösenord", type="password")

        if st.button("Logga in"):
            if password == CORRECT_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ Fel lösenord! Försök igen.")

        st.markdown("---")
        st.caption("Cloud Version - 4 enheter: 102, 103, 601, 602")
        return

    # --- INLOGGAD ---

    # Header
    st.markdown('<p class="big-font">📊 Ezzat\'s Controlling System</p>', unsafe_allow_html=True)
    st.markdown("**Controller:** Ezzat Rajab | **VGR Enheter:** 24 (Stor-Göteborg + Tätort)")
    st.info("☁️ **CLOUD VERSION** - 4 enheter aktiva: 102, 103, 601, 602")

    # Sidebar
    st.sidebar.title("📋 Navigation")

    # Månadsväljare
    st.sidebar.markdown("### 📅 Välj Period")
    manader = {
        "Mars 2026": "2026-03",
        "Februari 2026": "2026-02",
        "Januari 2026": "2026-01"
    }
    vald_manad_namn = st.sidebar.selectbox("Månad:", options=list(manader.keys()), index=0)
    vald_manad = manader[vald_manad_namn]

    st.sidebar.markdown("---")

    # Enhet-väljare
    st.sidebar.markdown("### 🏥 Välj Enhet")
    enheter_lista = {
        "102 - Frölunda Torg (VC)": "102",
        "103 - Grimmered (VC)": "103",
        "601 - Frölunda Torg Rehab": "601",
        "602 - Grimmered Rehab": "602",
    }

    vald_enhet_namn = st.sidebar.selectbox("Enhet:", options=list(enheter_lista.keys()), index=0)
    vald_enhet_kst = enheter_lista[vald_enhet_namn]

    st.sidebar.markdown("---")

    page = st.sidebar.radio(
        "Välj vy",
        ["🏠 Översikt", "📊 Enhetsvy", "💬 VEC Kommentarer"]
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📅 Senaste uppdatering")
    st.sidebar.success(f"{vald_manad_namn}\n\n✅ Data uppdaterad")

    if st.sidebar.button("🚪 Logga ut"):
        st.session_state.authenticated = False
        st.rerun()

    # Hämta enhetens data
    enhet_info = ENHETER_DATA[vald_enhet_kst]
    # Använd get_current_data() för att hämta färsk data från P&L och KPI-filer
    current_data = get_current_data(vald_enhet_kst, vald_manad)

    # Är det en Rehab-enhet?
    is_rehab = enhet_info['typ'] == 'Rehab'

    # === ÖVERSIKT ===
    if page == "🏠 Översikt":
        st.header(f"🏠 Översikt - {vald_manad_namn}")
        st.subheader(f"**{enhet_info['enhet_namn']}** ({enhet_info['typ']}) - KST: {vald_enhet_kst}")

        # KPI-rader (olika för VC vs Rehab)
        if not is_rehab:
            # VC: Visa Listning, ACG, Casemix, Rehab-poäng
            col1, col2, col3, col4 = st.columns(4)

            # Listning
            with col1:
                st.markdown("#### 👥 Listning")
                actual = current_data['listning']['actual']
                budget = current_data['listning']['budget']
                avv = actual - budget
                avv_pct = (avv / budget) * 100 if budget > 0 else 0
                traffic, _ = get_traffic_light(avv_pct)

                st.metric("Antal listade", f"{actual:,}", f"{avv:+,.0f} ({avv_pct:+.1f}%)")
                st.markdown(f"{traffic} Budget: {budget:,}")

            # ACG Poäng
            with col2:
                st.markdown("#### 🏥 ACG Poäng")
                actual = current_data['acg_poang']['actual']
                budget = current_data['acg_poang']['budget']
                avv = actual - budget
                avv_pct = (avv / budget) * 100 if budget > 0 else 0
                traffic, _ = get_traffic_light(avv_pct)

                st.metric("ACG Poäng", f"{actual:,.0f}", f"{avv:+,.0f} ({avv_pct:+.1f}%)")
                st.markdown(f"{traffic} Budget: {budget:,.0f}")

            # ACG Casemix
            with col3:
                st.markdown("#### 📊 ACG Casemix")
                actual = current_data['acg_casemix']['actual']
                budget = current_data['acg_casemix']['budget']
                avv = actual - budget
                avv_pct = (avv / budget) * 100 if budget > 0 else 0
                traffic, _ = get_traffic_light(avv_pct)

                st.metric("Casemix", f"{actual:.2f}", f"{avv:+.2f} ({avv_pct:+.1f}%)")
                st.markdown(f"{traffic} Budget: {budget:.2f}")

            # Rehab Poäng (från KPI-fil)
            with col4:
                st.markdown("#### 💪 Rehab Poäng")
                actual = current_data.get('rehab_poang_kpi', 0)

                if actual > 0:
                    st.metric("Poäng (KPI-fil)", f"{int(actual):,}")
                    st.markdown("📊 Från KPIer Storg-GBG")
                else:
                    st.info("Ingen Rehab-verksamhet")

        else:
            # REHAB: Visa Intäkter (P&L), Rehab-poäng (KPI), TeamBesök (KPI), FTE, Personalkostnad
            st.markdown("### 📊 Nyckeltal - Rehab")

            # Första raden: Intäkter och Poäng från filer
            col1, col2, col3 = st.columns(3)

            # Rehab Intäkter (från P&L Actual/Budget)
            with col1:
                st.markdown("#### 💰 Intäkter Total")
                actual = current_data['intakter_totalt']['actual']
                budget = current_data['intakter_totalt']['budget']
                avv = actual - budget
                avv_pct = (avv / budget) * 100 if budget > 0 else 0
                traffic, _ = get_traffic_light(avv_pct)

                st.metric("Revenue Total (P&L)", f"{actual:,.0f}", f"{avv:+,.0f} ({avv_pct:+.1f}%)")
                st.markdown(f"{traffic} Budget: {budget:,.0f}")

            # Rehab Poäng (från KPI-fil)
            with col2:
                st.markdown("#### 💪 Rehab Poäng")
                actual = current_data.get('rehab_poang_kpi', 0)

                if actual > 0:
                    st.metric("Poäng (KPI-fil)", f"{int(actual):,}")
                    st.markdown("📊 Från KPIer Storg-GBG")
                else:
                    st.info("Ingen data i KPI-filen")

            # TeamBesök (från KPI-fil)
            with col3:
                st.markdown("#### 🏥 TeamBesök (KPI)")
                actual = current_data.get('teambesok', 0)

                if actual > 0:
                    st.metric("TeamBesök", f"{int(actual)}")
                    st.markdown("📊 Data från KPI-filen")
                else:
                    st.info("Ingen data tillgänglig")

            st.markdown("---")

            # Andra raden: FTE och Personalkostnad
            col4, col5 = st.columns(2)

            # FTE
            with col4:
                st.markdown("#### 👔 FTE Total")
                actual = current_data['fte']['actual']
                budget = current_data['fte']['budget']
                avv = actual - budget
                avv_pct = (avv / budget) * 100 if budget > 0 else 0
                traffic, _ = get_traffic_light(avv_pct)

                st.metric("FTE", f"{actual:.1f}", f"{avv:+.1f} ({avv_pct:+.1f}%)")
                st.markdown(f"{traffic} Budget: {budget:.1f}")

            # Personalkostnad
            with col5:
                st.markdown("#### 💰 Personalkostnad")
                actual = current_data['personalkostnad']['actual']
                budget = current_data['personalkostnad']['budget']
                avv = actual - budget
                avv_pct = (avv / budget) * 100 if budget > 0 else 0
                traffic, _ = get_traffic_light(avv_pct, is_cost=True)

                st.metric("Kostnad (kr)", f"{actual:,.0f}", f"{avv:+,.0f} ({avv_pct:+.1f}%)")
                st.markdown(f"{traffic} Budget: {budget:,.0f}")

        st.markdown("---")

        # Personalkostnad och FTE för VC
        if not is_rehab:
            col5, col6 = st.columns(2)

            with col5:
                st.markdown("#### 💰 Personalkostnad")
                actual = current_data['personalkostnad']['actual']
                budget = current_data['personalkostnad']['budget']
                avv = actual - budget
                avv_pct = (avv / budget) * 100 if budget > 0 else 0
                traffic, _ = get_traffic_light(avv_pct, is_cost=True)

                st.metric("Kostnad (kr)", f"{actual:,.0f}", f"{avv:+,.0f} ({avv_pct:+.1f}%)")
                st.markdown(f"{traffic} Budget: {budget:,.0f}")

            with col6:
                st.markdown("#### 👔 FTE Total")
                actual = current_data['fte']['actual']
                budget = current_data['fte']['budget']
                avv = actual - budget
                avv_pct = (avv / budget) * 100 if budget > 0 else 0
                traffic, _ = get_traffic_light(avv_pct)

                st.metric("FTE", f"{actual:.1f}", f"{avv:+.1f} ({avv_pct:+.1f}%)")
                st.markdown(f"{traffic} Budget: {budget:.1f}")

            st.markdown("---")

        # Avvikelseanalys
        st.markdown("### 🔍 Avvikelseanalys - Personalkostnader")

        analyser = analyze_personal_avvikelser(vald_enhet_kst, vald_manad)

        if analyser:
            for analys in analyser:
                if analys['kostnad_avv_pct'] < -15:
                    box_class = "yellow-box" if analys['kostnad_avv_pct'] > -30 else "red-box"
                else:
                    box_class = "yellow-box" if analys['kostnad_avv_pct'] < 30 else "red-box"

                st.markdown(f"""
                <div class="{box_class}">
                <b>{analys['status']} - {analys['kategori']}</b><br>
                {analys['förklaring']}
                </div>
                """, unsafe_allow_html=True)
                st.markdown("")
        else:
            st.markdown('<div class="green-box">🟢 Alla personalkategorier inom acceptabelt intervall</div>', unsafe_allow_html=True)

    # === ENHETSVY ===
    elif page == "📊 Enhetsvy":
        st.header(f"📊 {enhet_info['enhet_namn']} (KST: {vald_enhet_kst})")
        st.markdown(f"**VEC:** {enhet_info['vec']} | **Region:** {enhet_info['region']} | **Typ:** {enhet_info['typ']} | **Period:** {vald_manad_namn}")

        tab1, tab2 = st.tabs(["💰 Personal", "📈 Trender"])

        with tab1:
            st.markdown(f"### 💰 Personal & Kostnader - {vald_manad_namn}")

            # FTE och Kostnadstabell
            fte_data = []
            for kat, values in current_data['fte_breakdown'].items():
                fte_avv = values['actual'] - values['budget']
                fte_avv_pct = (fte_avv / values['budget'] * 100) if values['budget'] > 0 else 0

                kostnad_avv = values['kostnad_actual'] - values['kostnad_budget']
                kostnad_avv_pct = (kostnad_avv / values['kostnad_budget'] * 100) if values['kostnad_budget'] > 0 else 0

                fte_data.append({
                    'Yrkesgrupp': kat,
                    'FTE Actual': values['actual'],
                    'FTE Budget': values['budget'],
                    'FTE Avv': round(fte_avv, 2),
                    'FTE Avv %': round(fte_avv_pct, 1),
                    'Kostnad Actual': f"{values['kostnad_actual']:,.0f}",
                    'Kostnad Budget': f"{values['kostnad_budget']:,.0f}",
                    'Kostnad Avv %': round(kostnad_avv_pct, 1)
                })

            df_fte = pd.DataFrame(fte_data)
            st.dataframe(df_fte, use_container_width=True, hide_index=True)

            # Detaljerad analys
            st.markdown("---")
            st.markdown("### 🔍 Detaljerad Avvikelseanalys")

            analyser = analyze_personal_avvikelser(vald_enhet_kst, vald_manad)

            if analyser:
                for analys in analyser:
                    with st.expander(f"{analys['status']} - {analys['kategori']} ({analys['kostnad_avv_pct']:+.1f}%)"):
                        st.markdown(analys['förklaring'])
            else:
                st.success("✅ Alla personalkategorier inom acceptabelt intervall")

        with tab2:
            st.markdown("### 📈 Trender Q1 2026")

            # Skapa trend-data för denna enhet
            months = ['Jan', 'Feb', 'Mar']

            # FTE Trend
            fte_actual = [enhet_info['månader']['2026-01']['fte']['actual'],
                         enhet_info['månader']['2026-02']['fte']['actual'],
                         enhet_info['månader']['2026-03']['fte']['actual']]
            fte_budget = [enhet_info['månader']['2026-01']['fte']['budget'],
                         enhet_info['månader']['2026-02']['fte']['budget'],
                         enhet_info['månader']['2026-03']['fte']['budget']]

            fig = go.Figure()
            fig.add_trace(go.Bar(x=months, y=fte_actual,
                               name='Actual FTE', marker_color='#FF6B6B'))
            fig.add_trace(go.Scatter(x=months, y=fte_budget,
                                   name='Budget FTE', mode='lines+markers',
                                   line=dict(color='#4ECDC4', width=3)))
            fig.update_layout(title=f'FTE Trend - {enhet_info["enhet_namn"]}', height=350)
            st.plotly_chart(fig, use_container_width=True)

            # Personalkostnad Trend
            pk_actual = [enhet_info['månader']['2026-01']['personalkostnad']['actual'],
                        enhet_info['månader']['2026-02']['personalkostnad']['actual'],
                        enhet_info['månader']['2026-03']['personalkostnad']['actual']]
            pk_budget = [enhet_info['månader']['2026-01']['personalkostnad']['budget'],
                        enhet_info['månader']['2026-02']['personalkostnad']['budget'],
                        enhet_info['månader']['2026-03']['personalkostnad']['budget']]

            fig = go.Figure()
            fig.add_trace(go.Bar(x=months, y=pk_actual,
                               name='Actual Kostnad', marker_color='#FF6B6B'))
            fig.add_trace(go.Scatter(x=months, y=pk_budget,
                                   name='Budget Kostnad', mode='lines+markers',
                                   line=dict(color='#4ECDC4', width=3)))
            fig.update_layout(title='Personalkostnad Trend (kr)', height=350)
            st.plotly_chart(fig, use_container_width=True)

            # Intäkter Trend
            int_actual = [enhet_info['månader']['2026-01']['intakter_totalt']['actual'],
                         enhet_info['månader']['2026-02']['intakter_totalt']['actual'],
                         enhet_info['månader']['2026-03']['intakter_totalt']['actual']]
            int_budget = [enhet_info['månader']['2026-01']['intakter_totalt']['budget'],
                         enhet_info['månader']['2026-02']['intakter_totalt']['budget'],
                         enhet_info['månader']['2026-03']['intakter_totalt']['budget']]

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=months, y=int_actual,
                                   mode='lines+markers', name='Actual',
                                   line=dict(color='#FF6B6B', width=3),
                                   marker=dict(size=10)))
            fig.add_trace(go.Scatter(x=months, y=int_budget,
                                   mode='lines+markers', name='Budget',
                                   line=dict(color='#4ECDC4', width=3),
                                   marker=dict(size=10)))
            fig.update_layout(title='Intäkter Trend (kr)', height=350)
            st.plotly_chart(fig, use_container_width=True)

    # === VEC KOMMENTARER ===
    elif page == "💬 VEC Kommentarer":
        st.header(f"💬 VEC Kommentarer - {vald_manad_namn}")
        st.markdown(f"**Enhet:** {enhet_info['enhet_namn']} | **VEC:** {enhet_info['vec']}")

        # Visa befintliga kommentarer för denna enhet
        st.markdown("---")
        st.markdown("### 📝 Tidigare Kommentarer")

        enhet_comments = [c for c in st.session_state.vec_comments if c['enhet_kst'] == vald_enhet_kst]

        if enhet_comments:
            for comment in reversed(enhet_comments):
                with st.expander(f"{comment['datum']} - {comment['författare']} ({comment['månad']})"):
                    st.markdown(comment['kommentar'])
        else:
            st.info(f"Inga kommentarer för {enhet_info['enhet_namn']} ännu")

        # Lägg till ny kommentar
        st.markdown("---")
        st.markdown("### ✍️ Lägg till Kommentar")

        with st.form("comment_form"):
            författare = st.text_input("Ditt namn", value=enhet_info['vec'])
            kommentar = st.text_area("Kommentar", height=150,
                                    placeholder="Beskriv situationen för denna månad...\n\nT.ex:\n- Status på rekrytering\n- Förklaring till avvikelser\n- Åtgärder som planeras")
            submitted = st.form_submit_button("💾 Spara Kommentar")

            if submitted and kommentar:
                # Spara kommentar i session state
                ny_kommentar = {
                    'datum': datetime.now().strftime("%Y-%m-%d %H:%M"),
                    'författare': författare,
                    'månad': vald_manad_namn,
                    'kommentar': kommentar,
                    'enhet': enhet_info['enhet_namn'],
                    'enhet_kst': vald_enhet_kst
                }
                st.session_state.vec_comments.append(ny_kommentar)
                st.success(f"✅ Kommentar sparad för {enhet_info['enhet_namn']}!")
                st.rerun()

if __name__ == "__main__":
    main()
