"""
Ezzat's Controlling System - VGR Controller Dashboard
Controller: Ezzat Rajab
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json
import os

# Konfiguration
st.set_page_config(
    page_title="Ezzat's Controlling System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Lösenord (i produktion ska detta vara säkrare)
CORRECT_PASSWORD = "citus2026"

# CSS för bättre design
st.markdown("""
<style>
    .big-font {
        font-size:30px !important;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
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

# Funktion för att läsa data
@st.cache_data
def load_data():
    """Läs all data från Excel-filer"""

    # P&L Budget
    df_budget = pd.read_excel('P&L Budget.xlsx')

    # P&L Actual
    df_actual = pd.read_excel('P&L Actual.xlsx')

    # Intäktsbudget
    df_intak = pd.read_excel('2 Intäktsbudget (Enhet) - 102 Frölunda Torg , VC StorGöteborg, Omtanken Västerleden Vård - 2026.xlsx')

    # FTE (Personal)
    df_fte = pd.read_excel('FTE Producerande per Yrkesgrupp (4).xlsx')

    # HR Cost
    df_hr = pd.read_excel('HR Cost (10).xlsx')

    return df_budget, df_actual, df_intak, df_fte, df_hr

def get_traffic_light(avvikelse_pct, is_cost=False):
    """Returnera trafikljus baserat på avvikelse%

    Args:
        avvikelse_pct: Procentuell avvikelse
        is_cost: True om det är kostnad (högre = sämre), False för intäkt (högre = bättre)
    """
    # För kostnader: positiv avvikelse (över budget) = dåligt (röd/gul)
    # För intäkter: negativ avvikelse (under budget) = dåligt (röd/gul)

    if is_cost:
        # Inverterad logik för kostnader
        if avvikelse_pct <= -5:  # Mycket under budget = bra
            return "🟢", "green-box"
        elif avvikelse_pct <= 0:  # Lite under budget = bra
            return "🟢", "green-box"
        elif avvikelse_pct <= 5:  # Lite över budget = varning
            return "🟡", "yellow-box"
        else:  # Mycket över budget = kritiskt
            return "🔴", "red-box"
    else:
        # Normal logik för intäkter/volym
        if abs(avvikelse_pct) <= 5:
            return "🟢", "green-box"
        elif abs(avvikelse_pct) <= 10:
            return "🟡", "yellow-box"
        else:
            return "🔴", "red-box"

def extract_kpi_data(df_intak, df_hr):
    """Extrahera KPI-data från rådata"""

    # Listning (rad 10 i intäktsbudget)
    listning_row = df_intak.iloc[10]
    listning_budget = {
        'Jan': int(listning_row['Unnamed: 4']),
        'Feb': int(listning_row['Unnamed: 5']),
        'Mar': int(listning_row['Unnamed: 6']),
    }

    # ACG Poäng (rad 6)
    acg_row = df_intak.iloc[6]
    acg_budget = {
        'Jan': float(acg_row['Unnamed: 4']),
        'Feb': float(acg_row['Unnamed: 5']),
        'Mar': float(acg_row['Unnamed: 6']),
    }

    # Personalkostnader från HR Cost
    hr_budget = {
        'Jan': float(df_hr.iloc[1]['January']),
        'Feb': float(df_hr.iloc[1]['February']),
        'Mar': float(df_hr.iloc[1]['March']),
    }

    # FTE Budget
    fte_budget = {
        'Jan': float(df_hr.iloc[1]['January.1']),
        'Feb': float(df_hr.iloc[1]['February.1']),
        'Mar': float(df_hr.iloc[1]['March.1']),
    }

    return {
        'listning': listning_budget,
        'acg': acg_budget,
        'hr_cost': hr_budget,
        'fte': fte_budget
    }

def load_comments():
    """Läs VEC-kommentarer från JSON-fil"""
    if os.path.exists('vec_comments.json'):
        with open('vec_comments.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_comment(comment_text, author):
    """Spara VEC-kommentar"""
    comments = load_comments()
    comments.append({
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'author': author,
        'text': comment_text
    })
    with open('vec_comments.json', 'w', encoding='utf-8') as f:
        json.dump(comments, f, ensure_ascii=False, indent=2)

# HUVUDAPP
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
        st.caption("DEMO-version för Frölunda Torg (102)")
        return

    # --- INLOGGAD ---

    # Header
    st.markdown('<p class="big-font">📊 Ezzat\'s Controlling System</p>', unsafe_allow_html=True)
    st.markdown("**Controller:** Ezzat Rajab | **VGR Enheter:** 24 (Stor-Göteborg + Tätort)")

    # Ladda data
    with st.spinner('Laddar data...'):
        df_budget, df_actual, df_intak, df_fte, df_hr = load_data()
        kpi_data = extract_kpi_data(df_intak, df_hr)

    # Sidebar - Navigation
    st.sidebar.title("📋 Navigation")

    # Enhet-väljare
    st.sidebar.markdown("### 🏥 Välj Enhet")

    # Lista alla enheter (demo med några enheter)
    enheter = {
        "102 - Frölunda Torg": "102",
        "103 - Grimmered": "103",
        "104 - Majorna": "104",
        "106 - Landala": "106",
        "107 - Pedagogen Park": "107",
        "108 - Åby": "108",
        "109 - Källered": "109",
        "110 - Kviberg": "110",
        "--- Tätort ---": None,
        "003 - Torpa": "003",
        "005 - Noltorp": "005",
        "006 - Lilla Edet": "006",
    }

    vald_enhet = st.sidebar.selectbox(
        "Enhet:",
        options=list(enheter.keys()),
        index=0
    )

    if enheter[vald_enhet] is None:
        st.sidebar.warning("⚠️ Denna är en separator, välj en faktisk enhet")
    elif enheter[vald_enhet] != "102":
        st.sidebar.info(f"📍 Enhet {enheter[vald_enhet]} - Data kommer i fullversion")

    st.sidebar.markdown("---")

    page = st.sidebar.radio(
        "Välj vy",
        ["🏠 Command Center", "📊 Enhetsvy", "💬 VEC Kommentarer", "📋 Action Log"]
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📅 Senaste uppdatering")
    st.sidebar.info("2026-03-31\n\n✅ Data uppdaterad för Q1 2026")

    if st.sidebar.button("🚪 Logga ut"):
        st.session_state.authenticated = False
        st.rerun()

    # === COMMAND CENTER ===
    if page == "🏠 Command Center":
        st.header("🏠 Command Center - Översikt")

        st.markdown("### 📊 DEMO: Frölunda Torg (102)")
        st.info("Detta är en demo med en enhet. I fullversion visas alla 24 enheter här.")

        # KPI Cards
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("#### 👥 Listning (Mars)")
            listning_actual = 8150  # Demo-värde
            listning_budget = kpi_data['listning']['Mar']
            avv = listning_actual - listning_budget
            avv_pct = (avv / listning_budget) * 100

            traffic, box_class = get_traffic_light(avv_pct)

            st.metric("Antal listade", f"{listning_actual:,}", f"{avv:+,.0f} ({avv_pct:+.1f}%)")
            st.markdown(f"{traffic} Budget: {listning_budget:,}")

        with col2:
            st.markdown("#### 🏥 ACG Poäng (Mars)")
            acg_actual = 2650  # Demo-värde
            acg_budget = kpi_data['acg']['Mar']
            avv = acg_actual - acg_budget
            avv_pct = (avv / acg_budget) * 100

            traffic, box_class = get_traffic_light(avv_pct)

            st.metric("ACG Poäng", f"{acg_actual:,.1f}", f"{avv:+,.1f} ({avv_pct:+.1f}%)")
            st.markdown(f"{traffic} Budget: {acg_budget:,.1f}")

        with col3:
            st.markdown("#### 💰 Personalkostnad (Mars)")
            # Faktiska siffror från ekonomisystemet
            hr_actual = 1237503.37  # Actual från ekonomisystemet
            hr_budget = 1604223.28  # Budget från ekonomisystemet

            # Avvikelse (positiv = över budget = dåligt för kostnader)
            avv = hr_actual - hr_budget
            avv_pct = (avv / hr_budget) * 100

            traffic, box_class = get_traffic_light(avv_pct, is_cost=True)

            st.metric("Kostnad (kr)", f"{hr_actual:,.0f}", f"{avv:+,.0f} ({avv_pct:+.1f}%)")
            st.markdown(f"{traffic} Budget: {hr_budget:,.0f}")
            st.caption(f"📊 FTE: 15.2 actual vs 20.7 budget")

        st.markdown("---")

        # Trafikljus-status
        st.markdown("### 🚦 Status per KPI")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="yellow-box">🟡 <b>Listning:</b> -1.1% under budget (Följ upp)</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="red-box">🔴 <b>ACG Poäng:</b> -3.3% under budget (Åtgärd krävs)</div>', unsafe_allow_html=True)

        col3, col4 = st.columns(2)

        with col3:
            st.markdown('<div class="green-box">🟢 <b>Personalkostnad:</b> -22.9% under budget (Bra!)</div>', unsafe_allow_html=True)
            with st.expander("🔍 Varför under budget?"):
                st.markdown("""
                **Analys:**
                - 💰 Actual: 1,237,503 kr
                - 📋 Budget: 1,604,223 kr
                - ✅ **367,000 kr under budget (-22.9%)**
                - 👥 FTE: 15.2 actual vs 20.7 budget

                **Förklaring:**
                - Lägre kostnader beror på vakanta tjänster
                - Särskilt: Sjuksköterskor (-42% FTE), Läkare (-10% FTE)
                - Underbemanning kan påverka verksamheten negativt
                - ❓ **Fråga till VEC:** Pågår rekrytering? Används vikarier?
                """)


        # Trend-graf
        st.markdown("---")
        st.markdown("### 📈 Trend Q1 2026")

        # Demo-data för trend
        months = ['Jan', 'Feb', 'Mar']
        listning_trend_actual = [8180, 8165, 8150]
        listning_trend_budget = [8200, 8220, 8240]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=months, y=listning_trend_actual, mode='lines+markers', name='Actual', line=dict(color='#FF6B6B', width=3)))
        fig.add_trace(go.Scatter(x=months, y=listning_trend_budget, mode='lines+markers', name='Budget', line=dict(color='#4ECDC4', width=3)))
        fig.update_layout(title='Listning - Actual vs Budget', xaxis_title='Månad', yaxis_title='Antal listade', height=400)

        st.plotly_chart(fig, use_container_width=True)

    # === ENHETSVY ===
    elif page == "📊 Enhetsvy":
        if enheter[vald_enhet] == "102":
            st.header("📊 Frölunda Torg (KST: 102)")
            st.markdown("**VEC:** Anna Victorin | **Region:** Stor-Göteborg")
        elif enheter[vald_enhet] is None:
            st.warning("⚠️ Välj en enhet från listan")
            return
        else:
            st.header(f"📊 {vald_enhet}")
            st.info("📍 Data för denna enhet kommer i fullversion")
            return

        # Tabs för olika KPI-områden
        tab1, tab2, tab3 = st.tabs(["👥 Listning & ACG", "💰 Personal & Kostnader", "📈 Trender"])

        with tab1:
            st.markdown("### 👥 Listning & ACG - Q1 2026")

            # Listning tabell
            st.markdown("#### Listning")
            listning_df = pd.DataFrame({
                'Månad': ['Januari', 'Februari', 'Mars'],
                'Actual': [8180, 8165, 8150],
                'Budget': [kpi_data['listning']['Jan'], kpi_data['listning']['Feb'], kpi_data['listning']['Mar']],
            })
            listning_df['Avvikelse'] = listning_df['Actual'] - listning_df['Budget']
            listning_df['Avv %'] = (listning_df['Avvikelse'] / listning_df['Budget'] * 100).round(1)

            st.dataframe(listning_df, use_container_width=True, hide_index=True)

            # ACG tabell
            st.markdown("#### ACG Poäng")
            acg_df = pd.DataFrame({
                'Månad': ['Januari', 'Februari', 'Mars'],
                'Actual': [2690, 2670, 2650],
                'Budget': [kpi_data['acg']['Jan'], kpi_data['acg']['Feb'], kpi_data['acg']['Mar']],
            })
            acg_df['Avvikelse'] = acg_df['Actual'] - acg_df['Budget']
            acg_df['Avv %'] = (acg_df['Avvikelse'] / acg_df['Budget'] * 100).round(1)

            st.dataframe(acg_df, use_container_width=True, hide_index=True)

        with tab2:
            st.markdown("### 💰 Personal & Kostnader - Mars 2026")

            # Personal breakdown med korrekt data
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### Antal FTE")
                fte_df = pd.DataFrame({
                    'Yrkesgrupp': ['Läkare', 'Sjuksköterska', 'Undersköterska', 'Psykolog', 'Admin/Stab', 'VEC/Vårdadmin'],
                    'Actual': [4.70, 5.87, 1.00, 0.85, 2.05, 0.77],
                    'Budget': [5.2, 10.05, 2.0, 1.0, 1.04, 2.44]
                })
                fte_df['Avvikelse'] = fte_df['Actual'] - fte_df['Budget']
                fte_df['Avv %'] = (fte_df['Avvikelse'] / fte_df['Budget'] * 100).round(1)
                st.dataframe(fte_df, use_container_width=True, hide_index=True)

            with col2:
                st.markdown("#### Budget Kostnad (kr)")
                cost_df = pd.DataFrame({
                    'Yrkesgrupp': ['Läkare', 'Sjuksköterska', 'Undersköterska', 'Psykolog', 'Admin', 'VEC+Vårdadm'],
                    'Budget': [441132, 449833, 60050, 45500, 33049, 81750],
                })
                st.dataframe(cost_df, use_container_width=True, hide_index=True)
                st.caption("⚠️ Actual kostnader ej tillgängliga i rådata")

            # Analys-sektion
            st.markdown("---")
            st.markdown("### 🔍 Avvikelseanalys")

            # Största avvikelser
            st.markdown("#### 🔴 Största Personalbrist:")

            col_a, col_b = st.columns(2)

            with col_a:
                st.markdown("""
                <div class="red-box">
                <b>Sjuksköterskor: -42% FTE</b><br>
                Actual: 5.9 vs Budget: 10.1<br>
                <b>⚠️ Brist: 4.2 FTE</b><br><br>
                <b>Möjliga orsaker:</b><br>
                • Vakanta tjänster (rekryteringssvårigheter?)<br>
                • Sjukfrånvaro ej ersatt<br>
                • Försenad rekrytering<br><br>
                <b>❓ Frågor till VEC:</b><br>
                • Pågår rekrytering?<br>
                • Påverkar detta verksamheten?<br>
                • Används vikariebemanning?
                </div>
                """, unsafe_allow_html=True)

            with col_b:
                st.markdown("""
                <div class="yellow-box">
                <b>Läkare: -10% FTE</b><br>
                Actual: 4.7 vs Budget: 5.2<br>
                <b>⚠️ Brist: 0.5 FTE</b><br><br>
                <b>Möjliga orsaker:</b><br>
                • Vakant tjänst<br>
                • Föräldraledighet?<br><br>
                <b>💰 Kostnadspåverkan:</b><br>
                Trots 10% färre läkare ligger kostnaden troligen nära budget pga högre löner för kvarvarande läkare eller vikarier
                </div>
                """, unsafe_allow_html=True)

            st.markdown("#### 🟢 Positiva avvikelser:")
            st.success("""
            **Undersköterska: -50% FTE** (1.0 vs 2.0 budget)
            - Kan indikera omfördelning av arbetsuppgifter
            - Eller vakant tjänst som ej behöver fyllas

            **Admin/Stab: +97% FTE** (2.05 vs 1.04 budget)
            - Tillfällig förstärkning?
            - Omorganisation?
            """)

        with tab3:
            st.markdown("### 📈 Trender & Analys")

            col_t1, col_t2 = st.columns(2)

            with col_t1:
                # Personal trend
                months = ['Jan', 'Feb', 'Mar']
                fte_total_actual = [16.1, 16.5, 15.2]
                fte_total_budget = [21.69, 19.69, 20.69]

                fig = go.Figure()
                fig.add_trace(go.Bar(x=months, y=fte_total_actual, name='Actual FTE', marker_color='#FF6B6B'))
                fig.add_trace(go.Scatter(x=months, y=fte_total_budget, name='Budget FTE', mode='lines+markers', line=dict(color='#4ECDC4', width=3)))
                fig.update_layout(title='Total FTE per månad', xaxis_title='Månad', yaxis_title='FTE', height=350)
                st.plotly_chart(fig, use_container_width=True)

            with col_t2:
                # Avvikelse per kategori (Mars)
                kategorier = ['Läkare', 'SSK', 'USK', 'Psykolog', 'Admin', 'VEC']
                avvikelse_pct = [-10, -42, -50, -15, +97, -68]
                colors = ['#ffc107' if x > -20 and x < 20 else '#dc3545' if x < -20 else '#28a745' for x in avvikelse_pct]

                fig2 = go.Figure(data=[
                    go.Bar(x=kategorier, y=avvikelse_pct, marker_color=colors)
                ])
                fig2.update_layout(title='FTE Avvikelse % per kategori (Mars)', xaxis_title='Yrkesgrupp', yaxis_title='Avvikelse %', height=350)
                fig2.add_hline(y=0, line_dash="dash", line_color="gray")
                st.plotly_chart(fig2, use_container_width=True)

    # === VEC KOMMENTARER ===
    elif page == "💬 VEC Kommentarer":
        st.header("💬 VEC Kommentarer - Frölunda Torg")

        st.markdown("### ✍️ Lägg till kommentar")

        with st.form("comment_form"):
            author = st.text_input("Ditt namn (VEC/Controller)", value="Anna Victorin")
            comment = st.text_area("Kommentar", placeholder="Förklara avvikelser, rapportera problem, eller uppdatera status...")

            submitted = st.form_submit_button("💾 Spara kommentar")

            if submitted and comment:
                save_comment(comment, author)
                st.success("✅ Kommentar sparad!")
                st.rerun()

        st.markdown("---")
        st.markdown("### 📝 Tidigare kommentarer")

        comments = load_comments()

        if comments:
            for idx, c in enumerate(reversed(comments)):
                with st.expander(f"💬 {c['author']} - {c['timestamp']}", expanded=(idx==0)):
                    st.markdown(c['text'])
        else:
            st.info("Inga kommentarer än. Lägg till den första!")

    # === ACTION LOG ===
    elif page == "📋 Action Log":
        st.header("📋 Action Log")
        st.info("Action Log kommer i fullversion - här spårar du uppföljningar och åtgärder per enhet.")

        # Demo action log
        st.markdown("### 🔴 Kritiska åtgärder")
        st.markdown("""
        | Enhet | Problem | VEC | Åtgärd | Deadline | Status |
        |-------|---------|-----|--------|----------|--------|
        | Frölunda Torg | ACG -3.3% | Anna Victorin | Öka komplexitetsgrad i diagnoser | 2026-04-15 | 🟡 Pågår |
        """)

if __name__ == "__main__":
    main()
