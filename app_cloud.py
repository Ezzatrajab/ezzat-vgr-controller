"""
Ezzat's Controlling System - Cloud Version v4.1
Controller: Ezzat Rajab
Uppdaterad: 2026-04-05
Multi-enhet support: Alla 20 enheter (Åby-Kållered & Avenyn-Lorensberg kombinerade)
RÄTT DATAKÄLLOR: KPIer Stor-GBG.xlsx + Budget-filer
KPI:er: Listning, ACG Casemix, Personalkostnad, FTE
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Import data loader functions
try:
    from data_loader_functions import load_all_data_for_enhet
    from rehab_poang_loader import load_rehab_poang_och_top_performers
except ImportError as e:
    st.error(f"Kunde inte importera data_loader_functions eller rehab_poang_loader: {e}")
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

@st.cache_data(ttl=300)  # 5 minuter cache istället för 1 timme
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


@st.cache_data(ttl=300, show_spinner=False)  # 5 minuter cache - v4.1
def load_kpi_data():
    """
    Läser KPI-data från KPIer Stor-GBG.xlsx
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
        kpi_path = os.path.join(script_dir, 'data', 'KPIer Stor-GBG.xlsx')
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
        # För kombinerade enheter: summera Åby (108) + Kållered (109) samt Avenyn (302) + Lorensberg (303)
        rehab_poang = {}
        rehab_temp = {}  # Temporär lagring för att kunna summera

        for row_idx in range(293, 301):
            row_data = df.iloc[row_idx, :].tolist()
            enhet_namn = str(row_data[0]) if pd.notna(row_data[0]) else ""
            enhet_kst = str(int(row_data[1])) if pd.notna(row_data[1]) else None

            if enhet_kst:
                rehab_temp[enhet_kst] = {}
                for col_idx, manad in col_to_month.items():
                    val = row_data[col_idx] if col_idx < len(row_data) else None
                    rehab_temp[enhet_kst][manad] = float(val) if pd.notna(val) else 0

        # Kombinera data för Åby-Kållered (108+109)
        if '108' in rehab_temp and '109' in rehab_temp:
            rehab_poang['108-109'] = {}
            for manad in col_to_month.values():
                aby_val = rehab_temp['108'].get(manad, 0)
                kallered_val = rehab_temp['109'].get(manad, 0)
                rehab_poang['108-109'][manad] = aby_val + kallered_val
        elif '108' in rehab_temp:
            rehab_poang['108-109'] = rehab_temp['108']

        # Kombinera data för Avenyn-Lorensberg (302+303)
        if '302' in rehab_temp and '303' in rehab_temp:
            rehab_poang['302-303'] = {}
            for manad in col_to_month.values():
                avenyn_val = rehab_temp['302'].get(manad, 0)
                lorensberg_val = rehab_temp['303'].get(manad, 0)
                rehab_poang['302-303'][manad] = avenyn_val + lorensberg_val
        elif '302' in rehab_temp:
            rehab_poang['302-303'] = rehab_temp['302']

        # Lägg till övriga enheter (ej kombinerade)
        for kst, data in rehab_temp.items():
            if kst not in ['108', '109', '302', '303']:
                rehab_poang[kst] = data

        # Läs TeamBesök (rad 305-312: Frölunda Torg=601, Grimmered=602, etc)
        # TeamBesök är för Rehab-enheter (605 = Åby Rehab, 660 = Avenyn Rehab, etc)
        # Dessa kombineras INTE eftersom de redan är separata Rehab-enheter
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

# Uppdaterad ENHETER_DATA med alla 20 enheter
# Månadsdatan hämtas dynamiskt från Excel-filer via get_current_data()

ENHETER_DATA = {
    # Stor-Göteborg VC (12 enheter)
    '102': {
        'enhet_namn': 'Frölunda Torg',
        'typ': 'VC',
        'vec': 'Anna Victorin',
        'region': 'Stor-Göteborg',
        'månader': {'2026-01': {}, '2026-02': {}, '2026-03': {}}
    },
    '103': {
        'enhet_namn': 'Grimmered',
        'typ': 'VC',
        'vec': 'Ulrika Klugge',
        'region': 'Stor-Göteborg',
        'månader': {'2026-01': {}, '2026-02': {}, '2026-03': {}}
    },
    '104': {
        'enhet_namn': 'Majorna',
        'typ': 'VC',
        'vec': 'Susanne Törnblom',
        'region': 'Stor-Göteborg',
        'månader': {'2026-01': {}, '2026-02': {}, '2026-03': {}}
    },
    '106': {
        'enhet_namn': 'Landala',
        'typ': 'VC',
        'vec': 'Maria Nyqvist',
        'region': 'Stor-Göteborg',
        'månader': {'2026-01': {}, '2026-02': {}, '2026-03': {}}
    },
    '107': {
        'enhet_namn': 'Pedagogen Park',
        'typ': 'VC',
        'vec': 'Fredrik',
        'region': 'Stor-Göteborg',
        'månader': {'2026-01': {}, '2026-02': {}, '2026-03': {}}
    },
    '108-109': {
        'enhet_namn': 'Åby-Kållered',
        'typ': 'VC',
        'vec': 'Theres E',
        'region': 'Stor-Göteborg',
        'månader': {'2026-01': {}, '2026-02': {}, '2026-03': {}}
    },
    '110': {
        'enhet_namn': 'Kviberg',
        'typ': 'VC',
        'vec': 'VEC namn saknas',
        'region': 'Stor-Göteborg',
        'månader': {'2026-01': {}, '2026-02': {}, '2026-03': {}}
    },
    '111': {
        'enhet_namn': 'Olskroken',
        'typ': 'VC',
        'vec': 'VEC namn saknas',
        'region': 'Stor-Göteborg',
        'månader': {'2026-01': {}, '2026-02': {}, '2026-03': {}}
    },
    '302-303': {
        'enhet_namn': 'Avenyn-Lorensberg',
        'typ': 'VC',
        'vec': 'Mats Norin',
        'region': 'Stor-Göteborg',
        'månader': {'2026-01': {}, '2026-02': {}, '2026-03': {}}
    },
    '304': {
        'enhet_namn': 'Husaren',
        'typ': 'VC',
        'vec': 'Maria Sahl',
        'region': 'Stor-Göteborg',
        'månader': {'2026-01': {}, '2026-02': {}, '2026-03': {}}
    },
    '015': {
        'enhet_namn': 'Karlastaden',
        'typ': 'VC',
        'vec': 'Theresia Nilhag',
        'region': 'Stor-Göteborg',
        'månader': {'2026-01': {}, '2026-02': {}, '2026-03': {}}
    },
    '4020': {
        'enhet_namn': 'City VC',
        'typ': 'VC',
        'vec': 'Amanda Lidström',
        'region': 'Stor-Göteborg',
        'månader': {'2026-01': {}, '2026-02': {}, '2026-03': {}}
    },

    # Rehab (8 enheter)
    '601': {
        'enhet_namn': 'Frölunda Torg Rehab',
        'typ': 'Rehab',
        'vec': 'Elin Magnusson',
        'region': 'Stor-Göteborg',
        'månader': {'2026-01': {}, '2026-02': {}, '2026-03': {}}
    },
    '602': {
        'enhet_namn': 'Grimmered Rehab',
        'typ': 'Rehab',
        'vec': 'Elin Magnusson',
        'region': 'Stor-Göteborg',
        'månader': {'2026-01': {}, '2026-02': {}, '2026-03': {}}
    },
    '603': {
        'enhet_namn': 'Majorna Rehab',
        'typ': 'Rehab',
        'vec': 'Elin Magnusson',
        'region': 'Stor-Göteborg',
        'månader': {'2026-01': {}, '2026-02': {}, '2026-03': {}}
    },
    '604': {
        'enhet_namn': 'Pedagogen Park Rehab',
        'typ': 'Rehab',
        'vec': 'Elin Magnusson',
        'region': 'Stor-Göteborg',
        'månader': {'2026-01': {}, '2026-02': {}, '2026-03': {}}
    },
    '605': {
        'enhet_namn': 'Åby Rehab',
        'typ': 'Rehab',
        'vec': 'Elin Magnusson',
        'region': 'Stor-Göteborg',
        'månader': {'2026-01': {}, '2026-02': {}, '2026-03': {}}
    },
    '607': {
        'enhet_namn': 'Olskroken Rehab',
        'typ': 'Rehab',
        'vec': 'Elin Magnusson',
        'region': 'Stor-Göteborg',
        'månader': {'2026-01': {}, '2026-02': {}, '2026-03': {}}
    },
    '660': {
        'enhet_namn': 'Avenyn Rehab',
        'typ': 'Rehab',
        'vec': 'Elin Magnusson',
        'region': 'Stor-Göteborg',
        'månader': {'2026-01': {}, '2026-02': {}, '2026-03': {}}
    },
    '715': {
        'enhet_namn': 'Karlastaden Rehab',
        'typ': 'Rehab',
        'vec': 'Elin Magnusson',
        'region': 'Stor-Göteborg',
        'månader': {'2026-01': {}, '2026-02': {}, '2026-03': {}}
    },
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
            '601': '102',     # Frölunda Torg Rehab -> Frölunda Torg VC
            '602': '103',     # Grimmered Rehab -> Grimmered VC
            '603': '104',     # Majorna Rehab -> Majorna VC
            '604': '107',     # Pedagogen Park Rehab -> Pedagogen Park VC
            '605': '108-109', # Åby Rehab -> Åby-Kållered VC
            '607': '111',     # Olskroken Rehab -> Olskroken VC
            '660': '302-303', # Avenyn Rehab -> Avenyn-Lorensberg VC
            '715': '015',     # Karlastaden Rehab -> Karlastaden VC
        }

        # Uppdatera intäkter för ALLA Rehab-enheter från P&L
        for enhet_kst, enhet_data in ENHETER_DATA.items():
            if enhet_data['typ'] == 'Rehab':
                for manad in enhet_data['månader'].keys():
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

        # Lägg till Rehab-poäng för ALLA VC-enheter (för visning)
        for enhet_kst, enhet_data in ENHETER_DATA.items():
            if enhet_data['typ'] == 'VC':
                for manad in enhet_data['månader'].keys():
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
    # Börja med data från ENHETER_DATA (för enhet_namn, typ, vec, region)
    # Men ersätt alla numeriska värden med riktiga data
    if enhet_kst in ENHETER_DATA and manad in ENHETER_DATA[enhet_kst]['månader']:
        base_data = ENHETER_DATA[enhet_kst]['månader'][manad].copy()
    else:
        # Om det inte finns i ENHETER_DATA, skapa tom dict
        base_data = {}

    # Hämta all faktisk data från Excel-filer
    try:
        real_data = load_all_data_for_enhet(enhet_kst, manad)
    except Exception as e:
        st.error(f"❌ FEL vid laddning av data för enhet {enhet_kst}, månad {manad}: {e}")
        st.exception(e)
        # Returnera tom data om fel uppstår
        base_data['fte'] = {'actual': 0, 'budget': 0}
        base_data['personalkostnad'] = {'actual': 0, 'budget': 0}
        return base_data

    # Uppdatera med faktiska värden
    base_data['fte'] = {
        'actual': real_data.get('fte_actual', 0),
        'budget': real_data.get('fte_budget', 0)
    }

    base_data['personalkostnad'] = {
        'actual': real_data.get('personalkostnad_actual', 0),
        'budget': real_data.get('personalkostnad_budget', 0)
    }

    # För VC-enheter: Läs listning och ACG casemix från KPIer-fil och budget-fil
    base_data['listning'] = {
        'actual': real_data.get('listning_actual', 0),
        'budget': real_data.get('listning_budget', 0)
    }

    base_data['acg_casemix'] = {
        'actual': real_data.get('acg_casemix_actual', 0),
        'budget': real_data.get('acg_casemix_budget', 0)
    }

    # Default-värden för intäkter
    if 'intakter_totalt' not in base_data:
        base_data['intakter_totalt'] = {'actual': 0, 'budget': 0}
    if 'intakter_3053' not in base_data:
        base_data['intakter_3053'] = {'actual': 0, 'budget': 0}

    # För Rehab-enheter: Läs intäkter från P&L
    if enhet_kst in ['601', '602', '603', '604', '605', '607', '660', '715']:
        # Hämta intäkter från P&L
        intakter = load_rehab_intakter_from_pl(enhet_kst, manad)
        base_data['intakter_totalt'] = intakter
        base_data['intakter_3053'] = intakter

        # Hämta Rehab budget-data
        rehab_budget = real_data.get('rehab_budget', {})
        base_data['rehab_budget_maaltal'] = rehab_budget.get('maaltal', 0)
        base_data['rehab_budget_antal_anstallda'] = rehab_budget.get('antal_anstallda', 0)
        base_data['rehab_budget_intakt'] = rehab_budget.get('budgeterad_intakt', 0)

        # Hämta Rehab-poäng och top performers från Poänguppföljning Rehab 2026.xlsx
        try:
            rehab_data = load_rehab_poang_och_top_performers(enhet_kst, manad)
            base_data['rehab_poang_actual'] = rehab_data['total_poang']
            base_data['rehab_poang_budget'] = rehab_data['budget_poang']
            base_data['top_performers'] = rehab_data['top_performers']
        except Exception as e:
            st.sidebar.warning(f"⚠️ Kunde inte ladda Rehab-poäng: {e}")
            base_data['rehab_poang_actual'] = 0
            base_data['rehab_poang_budget'] = 0
            base_data['top_performers'] = []

        # Hämta KPI-data (för TeamBesök)
        kpi_data = load_kpi_data()

        # Hämta TeamBesök
        if enhet_kst in kpi_data.get('teambesok', {}):
            base_data['teambesok'] = kpi_data['teambesok'][enhet_kst].get(manad, 0)
        else:
            base_data['teambesok'] = 0

    # För VC-enheter: Lägg till Rehab-poäng från KPI (om VC har kopplad Rehab)
    else:
        # VC-enhet
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
        st.caption("Cloud Version - Alla 20 enheter (12 VC + 8 Rehab)")
        return

    # --- INLOGGAD ---

    # Header
    st.markdown('<p class="big-font">📊 Ezzat\'s Controlling System</p>', unsafe_allow_html=True)
    st.markdown("**Controller:** Ezzat Rajab | **VGR Enheter:** 20 (12 VC + 8 Rehab)")
    st.info("☁️ **CLOUD VERSION** - Alla 20 enheter aktiva (inkl. Åby-Kållered & Avenyn-Lorensberg)")

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

    # Enhet-väljare - Dynamiskt från ENHETER_DATA
    st.sidebar.markdown("### 🏥 Välj Enhet")

    # Filter: VC eller Rehab
    enhet_typ_filter = st.sidebar.radio("Typ:", ["Alla", "VC", "Rehab"], horizontal=True)

    # Bygg enheter_lista dynamiskt från ENHETER_DATA
    enheter_lista = {}
    for kst in sorted(ENHETER_DATA.keys(), key=lambda x: (x.replace('-','').zfill(10))):
        enhet = ENHETER_DATA[kst]

        # Filtrera baserat på vald typ
        if enhet_typ_filter == "VC" and enhet['typ'] != "VC":
            continue
        if enhet_typ_filter == "Rehab" and enhet['typ'] != "Rehab":
            continue

        # Format: "KST - Namn (Typ)"
        display_name = f"{kst} - {enhet['enhet_namn']} ({enhet['typ']})"
        enheter_lista[display_name] = kst

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
            # VC: Visa Listning, ACG Casemix, FTE
            col1, col2, col3 = st.columns(3)

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

            # ACG Casemix
            with col2:
                st.markdown("#### 📊 ACG Casemix")
                actual = current_data['acg_casemix']['actual']
                budget = current_data['acg_casemix']['budget']
                avv = actual - budget
                avv_pct = (avv / budget) * 100 if budget > 0 else 0
                traffic, _ = get_traffic_light(avv_pct)

                st.metric("Casemix", f"{actual:.2f}", f"{avv:+.2f} ({avv_pct:+.1f}%)")
                st.markdown(f"{traffic} Budget: {budget:.2f}")

            # FTE Total
            with col3:
                st.markdown("#### 👔 FTE Total")
                actual = current_data['fte']['actual']
                budget = current_data['fte']['budget']
                avv = actual - budget
                avv_pct = (avv / budget) * 100 if budget > 0 else 0
                traffic, _ = get_traffic_light(avv_pct, is_cost=True)

                st.metric("FTE", f"{actual:.1f}", f"{avv:+.1f} ({avv_pct:+.1f}%)")
                st.markdown(f"{traffic} Budget: {budget:.1f}")

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

            # Rehab Poäng (från Poänguppföljning Rehab 2026)
            with col2:
                st.markdown("#### 💪 Rehab Poäng")
                actual = current_data.get('rehab_poang_actual', 0)
                budget_poang = current_data.get('rehab_poang_budget', 0)

                if actual > 0 or budget_poang > 0:
                    # Beräkna avvikelse
                    avv = actual - budget_poang
                    avv_pct = (avv / budget_poang * 100) if budget_poang > 0 else 0
                    traffic, _ = get_traffic_light(avv_pct)

                    st.metric("Poäng (Actual)", f"{int(actual):,}", f"{int(avv):+,} ({avv_pct:+.1f}%)")
                    st.markdown(f"{traffic} **Budget:** {int(budget_poang):,} poäng")
                    st.markdown("📊 Från Poänguppföljning Rehab 2026")

                    # Visa top performers (≥200 poäng)
                    top_performers = current_data.get('top_performers', [])
                    if top_performers:
                        st.markdown("##### ⭐ Top Performers (≥200 poäng)")
                        for person in top_performers:
                            st.markdown(f"**{person['namn']}**: {person['poang']:.0f} poäng 🎉")
                else:
                    st.info("Ingen data ännu")

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

            # FTE och Personalkostnad översikt
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### 👥 FTE (Full-Time Equivalent)")
                fte_actual = current_data['fte']['actual']
                fte_budget = current_data['fte']['budget']
                fte_avv = fte_actual - fte_budget
                fte_avv_pct = (fte_avv / fte_budget * 100) if fte_budget > 0 else 0

                st.metric("FTE Actual", f"{fte_actual:.1f}", f"{fte_avv:+.1f} ({fte_avv_pct:+.1f}%)")
                st.markdown(f"**Budget:** {fte_budget:.1f}")

            with col2:
                st.markdown("#### 💰 Personalkostnad")
                pk_actual = current_data['personalkostnad']['actual']
                pk_budget = current_data['personalkostnad']['budget']
                pk_avv = pk_actual - pk_budget
                pk_avv_pct = (pk_avv / pk_budget * 100) if pk_budget > 0 else 0

                st.metric("Kostnad Actual", f"{pk_actual:,.0f} kr", f"{pk_avv:+,.0f} ({pk_avv_pct:+.1f}%)")
                st.markdown(f"**Budget:** {pk_budget:,.0f} kr")

            st.markdown("---")

            # Sammanfattning tabell
            st.markdown("#### 📊 Översikt")
            df_oversikt = pd.DataFrame([{
                'Kategori': 'FTE',
                'Actual': f"{fte_actual:.1f}",
                'Budget': f"{fte_budget:.1f}",
                'Avvikelse': f"{fte_avv:+.1f}",
                'Avv %': f"{fte_avv_pct:+.1f}%"
            }, {
                'Kategori': 'Personalkostnad',
                'Actual': f"{pk_actual:,.0f}",
                'Budget': f"{pk_budget:,.0f}",
                'Avvikelse': f"{pk_avv:+,.0f}",
                'Avv %': f"{pk_avv_pct:+.1f}%"
            }])
            st.dataframe(df_oversikt, use_container_width=True, hide_index=True)

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
