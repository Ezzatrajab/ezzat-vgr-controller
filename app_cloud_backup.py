"""
Ezzat's Controlling System - Cloud Version
Controller: Ezzat Rajab
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
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
</style>
""", unsafe_allow_html=True)

# Hårdkodad data (Demo - Mars 2026)
DEMO_DATA = {
    'enhet_namn': 'Frölunda Torg',
    'kst': 102,
    'vec': 'Anna Victorin',
    'region': 'Stor-Göteborg',
    'listning': {
        'actual': 8150,
        'budget': 8240,
    },
    'acg': {
        'actual': 2650,
        'budget': 2737.1,
    },
    'personalkostnad': {
        'actual': 1237503,
        'budget': 1604223,
    },
    'fte': {
        'actual': 15.2,
        'budget': 20.7,
    },
    'fte_breakdown': {
        'Läkare': {'actual': 4.70, 'budget': 5.2},
        'Sjuksköterska': {'actual': 5.87, 'budget': 10.05},
        'Undersköterska': {'actual': 1.00, 'budget': 2.0},
        'Psykolog': {'actual': 0.85, 'budget': 1.0},
        'Admin/Stab': {'actual': 2.05, 'budget': 1.04},
        'VEC/Vårdadmin': {'actual': 0.77, 'budget': 2.44},
    },
    'trend_data': {
        'months': ['Jan', 'Feb', 'Mar'],
        'listning_actual': [8180, 8165, 8150],
        'listning_budget': [8200, 8220, 8240],
        'fte_actual': [16.1, 16.5, 15.2],
        'fte_budget': [21.69, 19.69, 20.69],
    }
}

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
        ["🏠 Command Center", "📊 Enhetsvy", "💬 VEC Kommentarer"]
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📅 Senaste uppdatering")
    st.sidebar.success("2026-03-31\n\n✅ Data uppdaterad")

    if st.sidebar.button("🚪 Logga ut"):
        st.session_state.authenticated = False
        st.rerun()

    # === COMMAND CENTER ===
    if page == "🏠 Command Center":
        st.header("🏠 Command Center - Översikt")

        col1, col2, col3 = st.columns(3)

        # Listning
        with col1:
            st.markdown("#### 👥 Listning (Mars)")
            actual = DEMO_DATA['listning']['actual']
            budget = DEMO_DATA['listning']['budget']
            avv = actual - budget
            avv_pct = (avv / budget) * 100
            traffic, _ = get_traffic_light(avv_pct)

            st.metric("Antal listade", f"{actual:,}", f"{avv:+,.0f} ({avv_pct:+.1f}%)")
            st.markdown(f"{traffic} Budget: {budget:,}")

        # ACG
        with col2:
            st.markdown("#### 🏥 ACG Poäng (Mars)")
            actual = DEMO_DATA['acg']['actual']
            budget = DEMO_DATA['acg']['budget']
            avv = actual - budget
            avv_pct = (avv / budget) * 100
            traffic, _ = get_traffic_light(avv_pct)

            st.metric("ACG Poäng", f"{actual:,.1f}", f"{avv:+,.1f} ({avv_pct:+.1f}%)")
            st.markdown(f"{traffic} Budget: {budget:,.1f}")

        # Personalkostnad
        with col3:
            st.markdown("#### 💰 Personalkostnad (Mars)")
            actual = DEMO_DATA['personalkostnad']['actual']
            budget = DEMO_DATA['personalkostnad']['budget']
            avv = actual - budget
            avv_pct = (avv / budget) * 100
            traffic, _ = get_traffic_light(avv_pct, is_cost=True)

            st.metric("Kostnad (kr)", f"{actual:,.0f}", f"{avv:+,.0f} ({avv_pct:+.1f}%)")
            st.markdown(f"{traffic} Budget: {budget:,.0f}")

        st.markdown("---")

        # Status
        st.markdown("### 🚦 Status per KPI")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="yellow-box">🟡 <b>Listning:</b> -1.1% under budget</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="red-box">🔴 <b>ACG Poäng:</b> -3.2% under budget</div>', unsafe_allow_html=True)

        col3, col4 = st.columns(2)
        with col3:
            st.markdown('<div class="green-box">🟢 <b>Personalkostnad:</b> -22.9% under budget (Bra!)</div>', unsafe_allow_html=True)
            with st.expander("🔍 Varför under budget?"):
                st.markdown("""
                **Analys:**
                - 💰 Actual: 1,237,503 kr
                - 📋 Budget: 1,604,223 kr
                - ✅ **367,000 kr under budget (-22.9%)**

                **Förklaring:**
                - Vakanta tjänster (särskilt SSK -42%)
                - Underbemanning kan påverka verksamhet
                - ❓ Pågår rekrytering?
                """)

        # Trend
        st.markdown("---")
        st.markdown("### 📈 Trend Q1 2026")

        trend = DEMO_DATA['trend_data']
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=trend['months'], y=trend['listning_actual'],
                                mode='lines+markers', name='Actual',
                                line=dict(color='#FF6B6B', width=3)))
        fig.add_trace(go.Scatter(x=trend['months'], y=trend['listning_budget'],
                                mode='lines+markers', name='Budget',
                                line=dict(color='#4ECDC4', width=3)))
        fig.update_layout(title='Listning - Actual vs Budget', height=400)
        st.plotly_chart(fig, use_container_width=True)

    # === ENHETSVY ===
    elif page == "📊 Enhetsvy":
        st.header(f"📊 {DEMO_DATA['enhet_namn']} (KST: {DEMO_DATA['kst']})")
        st.markdown(f"**VEC:** {DEMO_DATA['vec']} | **Region:** {DEMO_DATA['region']}")

        tab1, tab2, tab3 = st.tabs(["👥 Listning & ACG", "💰 Personal", "📈 Trender"])

        with tab1:
            st.markdown("### 👥 Listning & ACG - Mars 2026")

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Listning Actual", f"{DEMO_DATA['listning']['actual']:,}")
                st.metric("Listning Budget", f"{DEMO_DATA['listning']['budget']:,}")

            with col2:
                st.metric("ACG Actual", f"{DEMO_DATA['acg']['actual']:,.1f}")
                st.metric("ACG Budget", f"{DEMO_DATA['acg']['budget']:,.1f}")

        with tab2:
            st.markdown("### 💰 Personal & Kostnader - Mars 2026")

            # FTE tabell
            fte_data = []
            for kat, values in DEMO_DATA['fte_breakdown'].items():
                avv = values['actual'] - values['budget']
                avv_pct = (avv / values['budget'] * 100) if values['budget'] > 0 else 0
                fte_data.append({
                    'Yrkesgrupp': kat,
                    'Actual': values['actual'],
                    'Budget': values['budget'],
                    'Avvikelse': avv,
                    'Avv %': round(avv_pct, 1)
                })

            df_fte = pd.DataFrame(fte_data)
            st.dataframe(df_fte, use_container_width=True, hide_index=True)

            # Analys
            st.markdown("---")
            st.markdown("### 🔍 Avvikelseanalys")

            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("""
                <div class="red-box">
                <b>Sjuksköterskor: -42% FTE</b><br>
                Brist: 4.2 FTE<br><br>
                <b>Möjliga orsaker:</b><br>
                • Rekryteringssvårigheter<br>
                • Vakanta tjänster<br><br>
                <b>❓ Frågor till VEC:</b><br>
                • Pågår rekrytering?<br>
                • Används vikarier?
                </div>
                """, unsafe_allow_html=True)

        with tab3:
            st.markdown("### 📈 Trender")

            trend = DEMO_DATA['trend_data']
            fig = go.Figure()
            fig.add_trace(go.Bar(x=trend['months'], y=trend['fte_actual'],
                               name='Actual FTE', marker_color='#FF6B6B'))
            fig.add_trace(go.Scatter(x=trend['months'], y=trend['fte_budget'],
                                   name='Budget FTE', mode='lines+markers',
                                   line=dict(color='#4ECDC4', width=3)))
            fig.update_layout(title='FTE Trend', height=350)
            st.plotly_chart(fig, use_container_width=True)

    # === VEC KOMMENTARER ===
    elif page == "💬 VEC Kommentarer":
        st.header("💬 VEC Kommentarer")
        st.info("💡 I fullversionen kan VEC skriva kommentarer som sparas i Google Sheets")

        with st.form("comment_form"):
            author = st.text_input("Ditt namn", value="Anna Victorin")
            comment = st.text_area("Kommentar")
            submitted = st.form_submit_button("💾 Spara")

            if submitted and comment:
                st.success("✅ Kommentar mottagen (demo-läge)")

if __name__ == "__main__":
    main()
