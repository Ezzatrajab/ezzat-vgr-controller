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
                'intakter_totalt': {'actual': 780000, 'budget': 850000},
                'intakter_3053': {'actual': 780000, 'budget': 850000},  # Alla intäkter är Rehab
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
                'intakter_totalt': {'actual': 795000, 'budget': 860000},
                'intakter_3053': {'actual': 795000, 'budget': 860000},
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
                'intakter_totalt': {'actual': 810000, 'budget': 870000},
                'intakter_3053': {'actual': 810000, 'budget': 870000},
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
                'intakter_totalt': {'actual': 680000, 'budget': 750000},
                'intakter_3053': {'actual': 680000, 'budget': 750000},
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
                'intakter_totalt': {'actual': 695000, 'budget': 760000},
                'intakter_3053': {'actual': 695000, 'budget': 760000},
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
                'intakter_totalt': {'actual': 710000, 'budget': 770000},
                'intakter_3053': {'actual': 710000, 'budget': 770000},
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
    """Analysera personalkostnader per kategori och identifiera stora avvikelser"""
    fte_breakdown = ENHETER_DATA[enhet_kst]['månader'][vald_manad]['fte_breakdown']

    analyser = []
    for kategori, values in fte_breakdown.items():
        kostnad_avv = values['kostnad_actual'] - values['kostnad_budget']
        kostnad_avv_pct = (kostnad_avv / values['kostnad_budget'] * 100) if values['kostnad_budget'] > 0 else 0

        fte_avv = values['actual'] - values['budget']
        fte_avv_pct = (fte_avv / values['budget'] * 100) if values['budget'] > 0 else 0

        # Identifiera stora avvikelser (över 15% eller under -15%)
        if abs(kostnad_avv_pct) > 15:
            status = "🔴 Kritisk" if abs(kostnad_avv_pct) > 30 else "🟡 Varning"
            förklaring = ""

            if kostnad_avv_pct < -15:
                förklaring = f"**Under budget**: {abs(kostnad_avv_pct):.1f}% (-{abs(kostnad_avv):,.0f} kr)"
                förklaring += f"\n- Saknas: {abs(fte_avv):.1f} FTE"
                förklaring += "\n- Trolig orsak: Vakanta tjänster, rekryteringssvårigheter"
            else:
                förklaring = f"**Över budget**: +{kostnad_avv_pct:.1f}% (+{kostnad_avv:,.0f} kr)"
                förklaring += f"\n- Över: +{fte_avv:.1f} FTE"
                förklaring += "\n- Trolig orsak: Extra bemanning, konsulter?"

            analyser.append({
                'kategori': kategori,
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
    current_data = enhet_info['månader'][vald_manad]

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

            # Rehab Poäng (om VC har rehab-intäkter)
            with col4:
                st.markdown("#### 💪 Rehab Poäng")
                intakter = current_data['intakter_3053']['actual']
                budget_intakter = current_data['intakter_3053']['budget']

                if intakter > 0:
                    actual = calculate_rehab_poang(intakter)
                    budget = calculate_rehab_poang(budget_intakter)
                    avv = actual - budget
                    avv_pct = (avv / budget) * 100 if budget > 0 else 0
                    traffic, _ = get_traffic_light(avv_pct)

                    st.metric("Poäng (3053/523)", f"{actual:,.0f}", f"{avv:+,.0f} ({avv_pct:+.1f}%)")
                    st.markdown(f"{traffic} Budget: {budget:,.0f}")
                else:
                    st.info("Ingen Rehab-verksamhet")

        else:
            # REHAB: Visa Intäkter, Rehab-poäng, FTE, Personalkostnad
            col1, col2, col3, col4 = st.columns(4)

            # Rehab Intäkter
            with col1:
                st.markdown("#### 💰 Rehab Intäkter")
                actual = current_data['intakter_totalt']['actual']
                budget = current_data['intakter_totalt']['budget']
                avv = actual - budget
                avv_pct = (avv / budget) * 100 if budget > 0 else 0
                traffic, _ = get_traffic_light(avv_pct)

                st.metric("Intäkter (kr)", f"{actual:,.0f}", f"{avv:+,.0f} ({avv_pct:+.1f}%)")
                st.markdown(f"{traffic} Budget: {budget:,.0f}")

            # Rehab Poäng
            with col2:
                st.markdown("#### 💪 Rehab Poäng")
                intakter = current_data['intakter_3053']['actual']
                budget_intakter = current_data['intakter_3053']['budget']
                actual = calculate_rehab_poang(intakter)
                budget = calculate_rehab_poang(budget_intakter)
                avv = actual - budget
                avv_pct = (avv / budget) * 100 if budget > 0 else 0
                traffic, _ = get_traffic_light(avv_pct)

                st.metric("Poäng (3053/523)", f"{actual:,.0f}", f"{avv:+,.0f} ({avv_pct:+.1f}%)")
                st.markdown(f"{traffic} Budget: {budget:,.0f}")

            # FTE
            with col3:
                st.markdown("#### 👔 FTE Total")
                actual = current_data['fte']['actual']
                budget = current_data['fte']['budget']
                avv = actual - budget
                avv_pct = (avv / budget) * 100 if budget > 0 else 0
                traffic, _ = get_traffic_light(avv_pct)

                st.metric("FTE", f"{actual:.1f}", f"{avv:+.1f} ({avv_pct:+.1f}%)")
                st.markdown(f"{traffic} Budget: {budget:.1f}")

            # Personalkostnad
            with col4:
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
