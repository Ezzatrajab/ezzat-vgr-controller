"""
Ezzat's Controlling System - Cloud Version v2
Controller: Ezzat Rajab
Uppdaterad: 2026-04-01
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

# Hårdkodad data - Månadsdata Jan-Mars 2026
MONTHLY_DATA = {
    '2026-01': {
        'månad': 'Januari 2026',
        'enhet_namn': 'Frölunda Torg',
        'kst': 102,
        'vec': 'Anna Victorin',
        'region': 'Stor-Göteborg',
        'listning': {'actual': 8180, 'budget': 8200},
        'acg_poang': {'actual': 2698, 'budget': 2750},
        'acg_casemix': {'actual': 1.02, 'budget': 1.04},
        'intakter_totalt': {'actual': 3420000, 'budget': 3500000},
        'intakter_3053': {'actual': 523000, 'budget': 550000},  # Rehab-intäkter
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
        'månad': 'Februari 2026',
        'enhet_namn': 'Frölunda Torg',
        'kst': 102,
        'vec': 'Anna Victorin',
        'region': 'Stor-Göteborg',
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
        'månad': 'Mars 2026',
        'enhet_namn': 'Frölunda Torg',
        'kst': 102,
        'vec': 'Anna Victorin',
        'region': 'Stor-Göteborg',
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

# Session state initiering
if 'vec_comments' not in st.session_state:
    st.session_state.vec_comments = []

def calculate_rehab_poang(intakter_3053):
    """Beräkna antal Rehab-poäng (intäkter / 523 kr per poäng)"""
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

def analyze_personal_avvikelser(data, vald_manad):
    """Analysera personalkostnader per kategori och identifiera stora avvikelser"""
    fte_breakdown = data[vald_manad]['fte_breakdown']

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
                if kategori == "Sjuksköterska":
                    förklaring += "\n- Trolig orsak: Vakanta tjänster, rekryteringssvårigheter"
                    förklaring += f"\n- Saknas: {abs(fte_avv):.1f} FTE"
                elif kategori == "VEC/Vårdadmin":
                    förklaring += "\n- Trolig orsak: Vakant VEC/Vårdadmin-tjänst"
                    förklaring += f"\n- Saknas: {abs(fte_avv):.1f} FTE"
            else:
                förklaring = f"**Över budget**: +{kostnad_avv_pct:.1f}% (+{kostnad_avv:,.0f} kr)"
                if kategori == "Admin/Stab":
                    förklaring += "\n- Trolig orsak: Extra bemanning, konsulter?"
                    förklaring += f"\n- Över: +{fte_avv:.1f} FTE"

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
        st.caption("Cloud Demo-version för Frölunda Torg (102)")
        return

    # --- INLOGGAD ---

    # Header
    st.markdown('<p class="big-font">📊 Ezzat\'s Controlling System</p>', unsafe_allow_html=True)
    st.markdown("**Controller:** Ezzat Rajab | **VGR Enheter:** 24 (Stor-Göteborg + Tätort)")
    st.info("☁️ **CLOUD VERSION** - Fungerar överallt på alla enheter!")

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
    enheter = {
        "102 - Frölunda Torg": "102",
        "103 - Grimmered": "103",
        "104 - Majorna": "104",
        "--- Tätort ---": None,
        "003 - Torpa": "003",
        "005 - Noltorp": "005",
    }

    vald_enhet = st.sidebar.selectbox("Enhet:", options=list(enheter.keys()), index=0)

    if enheter[vald_enhet] != "102":
        st.sidebar.info("📍 Endast Frölunda Torg i denna demo")

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

    # Hämta månadens data
    current_data = MONTHLY_DATA[vald_manad]

    # === ÖVERSIKT (tidigare Command Center) ===
    if page == "🏠 Översikt":
        st.header(f"🏠 Översikt - {current_data['månad']}")

        # KPI-rader
        col1, col2, col3, col4 = st.columns(4)

        # Listning
        with col1:
            st.markdown("#### 👥 Listning")
            actual = current_data['listning']['actual']
            budget = current_data['listning']['budget']
            avv = actual - budget
            avv_pct = (avv / budget) * 100
            traffic, _ = get_traffic_light(avv_pct)

            st.metric("Antal listade", f"{actual:,}", f"{avv:+,.0f} ({avv_pct:+.1f}%)")
            st.markdown(f"{traffic} Budget: {budget:,}")

        # ACG Poäng
        with col2:
            st.markdown("#### 🏥 ACG Poäng")
            actual = current_data['acg_poang']['actual']
            budget = current_data['acg_poang']['budget']
            avv = actual - budget
            avv_pct = (avv / budget) * 100
            traffic, _ = get_traffic_light(avv_pct)

            st.metric("ACG Poäng", f"{actual:,.0f}", f"{avv:+,.0f} ({avv_pct:+.1f}%)")
            st.markdown(f"{traffic} Budget: {budget:,.0f}")

        # ACG Casemix
        with col3:
            st.markdown("#### 📊 ACG Casemix")
            actual = current_data['acg_casemix']['actual']
            budget = current_data['acg_casemix']['budget']
            avv = actual - budget
            avv_pct = (avv / budget) * 100
            traffic, _ = get_traffic_light(avv_pct)

            st.metric("Casemix", f"{actual:.2f}", f"{avv:+.2f} ({avv_pct:+.1f}%)")
            st.markdown(f"{traffic} Budget: {budget:.2f}")

        # Rehab Poäng
        with col4:
            st.markdown("#### 💪 Rehab Poäng")
            intakter = current_data['intakter_3053']['actual']
            budget_intakter = current_data['intakter_3053']['budget']
            actual = calculate_rehab_poang(intakter)
            budget = calculate_rehab_poang(budget_intakter)
            avv = actual - budget
            avv_pct = (avv / budget) * 100
            traffic, _ = get_traffic_light(avv_pct)

            st.metric("Poäng (3053/523)", f"{actual:,.0f}", f"{avv:+,.0f} ({avv_pct:+.1f}%)")
            st.markdown(f"{traffic} Budget: {budget:,.0f}")

        st.markdown("---")

        # Personalkostnad översikt
        col5, col6 = st.columns(2)

        with col5:
            st.markdown("#### 💰 Personalkostnad")
            actual = current_data['personalkostnad']['actual']
            budget = current_data['personalkostnad']['budget']
            avv = actual - budget
            avv_pct = (avv / budget) * 100
            traffic, _ = get_traffic_light(avv_pct, is_cost=True)

            st.metric("Kostnad (kr)", f"{actual:,.0f}", f"{avv:+,.0f} ({avv_pct:+.1f}%)")
            st.markdown(f"{traffic} Budget: {budget:,.0f}")

        with col6:
            st.markdown("#### 👔 FTE Total")
            actual = current_data['fte']['actual']
            budget = current_data['fte']['budget']
            avv = actual - budget
            avv_pct = (avv / budget) * 100
            traffic, _ = get_traffic_light(avv_pct)

            st.metric("FTE", f"{actual:.1f}", f"{avv:+.1f} ({avv_pct:+.1f}%)")
            st.markdown(f"{traffic} Budget: {budget:.1f}")

        st.markdown("---")

        # Avvikelseanalys - Personalkostnader
        st.markdown("### 🔍 Avvikelseanalys - Personalkostnader")

        analyser = analyze_personal_avvikelser(MONTHLY_DATA, vald_manad)

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

        st.markdown("---")

        # Trend Q1 2026
        st.markdown("### 📈 Trend Q1 2026 - Alla Månader")

        # Skapa trend-data från alla månader
        months = ['Jan', 'Feb', 'Mar']
        listning_actual = [MONTHLY_DATA['2026-01']['listning']['actual'],
                          MONTHLY_DATA['2026-02']['listning']['actual'],
                          MONTHLY_DATA['2026-03']['listning']['actual']]
        listning_budget = [MONTHLY_DATA['2026-01']['listning']['budget'],
                          MONTHLY_DATA['2026-02']['listning']['budget'],
                          MONTHLY_DATA['2026-03']['listning']['budget']]
        acg_actual = [MONTHLY_DATA['2026-01']['acg_poang']['actual'],
                     MONTHLY_DATA['2026-02']['acg_poang']['actual'],
                     MONTHLY_DATA['2026-03']['acg_poang']['actual']]
        acg_budget = [MONTHLY_DATA['2026-01']['acg_poang']['budget'],
                     MONTHLY_DATA['2026-02']['acg_poang']['budget'],
                     MONTHLY_DATA['2026-03']['acg_poang']['budget']]

        tab1, tab2, tab3 = st.tabs(["👥 Listning", "🏥 ACG Poäng", "📊 ACG Casemix"])

        with tab1:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=months, y=listning_actual,
                                    mode='lines+markers', name='Actual',
                                    line=dict(color='#FF6B6B', width=3),
                                    marker=dict(size=10)))
            fig.add_trace(go.Scatter(x=months, y=listning_budget,
                                    mode='lines+markers', name='Budget',
                                    line=dict(color='#4ECDC4', width=3),
                                    marker=dict(size=10)))
            fig.update_layout(title='Listning - Actual vs Budget', height=400)
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=months, y=acg_actual,
                                    mode='lines+markers', name='Actual',
                                    line=dict(color='#FF6B6B', width=3),
                                    marker=dict(size=10)))
            fig.add_trace(go.Scatter(x=months, y=acg_budget,
                                    mode='lines+markers', name='Budget',
                                    line=dict(color='#4ECDC4', width=3),
                                    marker=dict(size=10)))
            fig.update_layout(title='ACG Poäng - Actual vs Budget', height=400)
            st.plotly_chart(fig, use_container_width=True)

        with tab3:
            casemix_actual = [MONTHLY_DATA['2026-01']['acg_casemix']['actual'],
                            MONTHLY_DATA['2026-02']['acg_casemix']['actual'],
                            MONTHLY_DATA['2026-03']['acg_casemix']['actual']]
            casemix_budget = [MONTHLY_DATA['2026-01']['acg_casemix']['budget'],
                            MONTHLY_DATA['2026-02']['acg_casemix']['budget'],
                            MONTHLY_DATA['2026-03']['acg_casemix']['budget']]

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=months, y=casemix_actual,
                                    mode='lines+markers', name='Actual',
                                    line=dict(color='#FF6B6B', width=3),
                                    marker=dict(size=10)))
            fig.add_trace(go.Scatter(x=months, y=casemix_budget,
                                    mode='lines+markers', name='Budget',
                                    line=dict(color='#4ECDC4', width=3),
                                    marker=dict(size=10)))
            fig.update_layout(title='ACG Casemix - Utveckling', height=400)
            st.plotly_chart(fig, use_container_width=True)

    # === ENHETSVY ===
    elif page == "📊 Enhetsvy":
        st.header(f"📊 {current_data['enhet_namn']} (KST: {current_data['kst']})")
        st.markdown(f"**VEC:** {current_data['vec']} | **Region:** {current_data['region']} | **Period:** {current_data['månad']}")

        tab1, tab2, tab3 = st.tabs(["👥 Listning & ACG", "💰 Personal", "📈 Trender"])

        with tab1:
            st.markdown(f"### 👥 Listning & ACG - {current_data['månad']}")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Listning Actual", f"{current_data['listning']['actual']:,}")
                st.metric("Listning Budget", f"{current_data['listning']['budget']:,}")

            with col2:
                st.metric("ACG Poäng Actual", f"{current_data['acg_poang']['actual']:,.0f}")
                st.metric("ACG Poäng Budget", f"{current_data['acg_poang']['budget']:,.0f}")

            with col3:
                st.metric("ACG Casemix Actual", f"{current_data['acg_casemix']['actual']:.2f}")
                st.metric("ACG Casemix Budget", f"{current_data['acg_casemix']['budget']:.2f}")

            st.markdown("---")

            # Rehab
            col4, col5 = st.columns(2)
            with col4:
                intakter = current_data['intakter_3053']['actual']
                poang = calculate_rehab_poang(intakter)
                st.metric("Rehab Intäkter (3053)", f"{intakter:,.0f} kr")
                st.metric("Rehab Poäng", f"{poang:,.0f} poäng")
                st.caption("Beräkning: Intäkter / 523 kr per poäng")

        with tab2:
            st.markdown(f"### 💰 Personal & Kostnader - {current_data['månad']}")

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

            analyser = analyze_personal_avvikelser(MONTHLY_DATA, vald_manad)

            if analyser:
                for analys in analyser:
                    with st.expander(f"{analys['status']} - {analys['kategori']} ({analys['kostnad_avv_pct']:+.1f}%)"):
                        st.markdown(analys['förklaring'])
            else:
                st.success("✅ Alla personalkategorier inom acceptabelt intervall")

        with tab3:
            st.markdown("### 📈 Trender Q1 2026")

            # FTE Trend
            fte_actual = [MONTHLY_DATA['2026-01']['fte']['actual'],
                         MONTHLY_DATA['2026-02']['fte']['actual'],
                         MONTHLY_DATA['2026-03']['fte']['actual']]
            fte_budget = [MONTHLY_DATA['2026-01']['fte']['budget'],
                         MONTHLY_DATA['2026-02']['fte']['budget'],
                         MONTHLY_DATA['2026-03']['fte']['budget']]

            fig = go.Figure()
            fig.add_trace(go.Bar(x=months, y=fte_actual,
                               name='Actual FTE', marker_color='#FF6B6B'))
            fig.add_trace(go.Scatter(x=months, y=fte_budget,
                                   name='Budget FTE', mode='lines+markers',
                                   line=dict(color='#4ECDC4', width=3)))
            fig.update_layout(title='FTE Trend', height=350)
            st.plotly_chart(fig, use_container_width=True)

            # Personalkostnad Trend
            pk_actual = [MONTHLY_DATA['2026-01']['personalkostnad']['actual'],
                        MONTHLY_DATA['2026-02']['personalkostnad']['actual'],
                        MONTHLY_DATA['2026-03']['personalkostnad']['actual']]
            pk_budget = [MONTHLY_DATA['2026-01']['personalkostnad']['budget'],
                        MONTHLY_DATA['2026-02']['personalkostnad']['budget'],
                        MONTHLY_DATA['2026-03']['personalkostnad']['budget']]

            fig = go.Figure()
            fig.add_trace(go.Bar(x=months, y=pk_actual,
                               name='Actual Kostnad', marker_color='#FF6B6B'))
            fig.add_trace(go.Scatter(x=months, y=pk_budget,
                                   name='Budget Kostnad', mode='lines+markers',
                                   line=dict(color='#4ECDC4', width=3)))
            fig.update_layout(title='Personalkostnad Trend (kr)', height=350)
            st.plotly_chart(fig, use_container_width=True)

    # === VEC KOMMENTARER ===
    elif page == "💬 VEC Kommentarer":
        st.header(f"💬 VEC Kommentarer - {current_data['månad']}")
        st.markdown(f"**Enhet:** {current_data['enhet_namn']} | **VEC:** {current_data['vec']}")

        # Visa befintliga kommentarer
        st.markdown("---")
        st.markdown("### 📝 Tidigare Kommentarer")

        if st.session_state.vec_comments:
            for i, comment in enumerate(reversed(st.session_state.vec_comments)):
                with st.expander(f"{comment['datum']} - {comment['författare']} ({comment['månad']})"):
                    st.markdown(comment['kommentar'])
        else:
            st.info("Inga kommentarer ännu")

        # Lägg till ny kommentar
        st.markdown("---")
        st.markdown("### ✍️ Lägg till Kommentar")

        with st.form("comment_form"):
            författare = st.text_input("Ditt namn", value=current_data['vec'])
            kommentar = st.text_area("Kommentar", height=150,
                                    placeholder="Beskriv situationen för denna månad...\n\nT.ex:\n- Status på rekrytering\n- Förklaring till avvikelser\n- Åtgärder som planeras")
            submitted = st.form_submit_button("💾 Spara Kommentar")

            if submitted and kommentar:
                # Spara kommentar i session state
                ny_kommentar = {
                    'datum': datetime.now().strftime("%Y-%m-%d %H:%M"),
                    'författare': författare,
                    'månad': current_data['månad'],
                    'kommentar': kommentar,
                    'enhet': current_data['enhet_namn']
                }
                st.session_state.vec_comments.append(ny_kommentar)
                st.success(f"✅ Kommentar sparad av {författare}!")
                st.rerun()

if __name__ == "__main__":
    main()
