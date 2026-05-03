# FINAL FIX - Korrekta Rehab-siffror

## Problem
Dashboard visade hårdkodade värden för Rehab-intäkter och beräknade Rehab-poäng istället för att läsa från P&L och KPI-filer.

**Exempel (Frölunda Torg Rehab, Mars 2026):**
- **Visat**: 810,000 kr (hårdkodat)
- **Verkligt (från P&L)**: 76,134 kr

## Lösning

### 1. **Satt Rehab-intäkter till 0 i ENHETER_DATA**
Alla intäkter för enheter 601 och 602 är nu 0 i hårdkodad data, eftersom de ska läsas från P&L-filer.

### 2. **Använder st.session_state**
```python
# Uppdatera data och lagra i session_state
if 'enheter_data' not in st.session_state:
    uppdatera_rehab_data()  # Läser från P&L och KPI-filer
    st.session_state.enheter_data = ENHETER_DATA.copy()

# Använd uppdaterad data från session_state
ENHETER_DATA = st.session_state.enheter_data
```

Detta gör att:
- Vid första körningen läses data från P&L och KPI-filer
- Data lagras i session_state
- Vid varje efterföljande körning används den uppdaterade datan

### 3. **Data som läses från filer:**

#### P&L Actual/Budget (Revenue Total):
- **Frölunda Torg Rehab (601)**:
  - Jan 2026: 475,462 kr (actual) vs 667,762 kr (budget)
  - Feb 2026: 577,129 kr (actual) vs 649,944 kr (budget)
  - Mars 2026: 76,134 kr (actual) vs 660,183 kr (budget)

#### KPIer Storg-GBG:
- **Rehab Poäng** (från VC 102 för 601):
  - Jan 2026: 779 poäng
  - Feb 2026: 900 poäng
  - Mars 2026: 0 (ingen data)

- **TeamBesök** (för 601):
  - Jan 2026: 23 besök
  - Feb 2026: 25 besök
  - Mars 2026: 0 (ingen data)

## Förväntad visning i Dashboard

### Frölunda Torg Rehab (601), Mars 2026:

**Rad 1:**
- 💰 **Intäkter Total**: 76,134 kr (actual) vs 660,183 kr (budget) ✅
- 💪 **Rehab Poäng**: 0 poäng (ingen data i KPI-filen) ✅
- 🏥 **TeamBesök**: 0 besök (ingen data i KPI-filen) ✅

**Rad 2:**
- 👔 **FTE**: 9.0 vs 10.6
- 💰 **Personalkostnad**: 550,000 kr vs 630,000 kr

## Filer ändrade
- `app_cloud.py` - Huvudfilen med alla fixar

## Test
```bash
streamlit run app_cloud.py
```

1. Välj enhet: **Frölunda Torg Rehab (601)**
2. Välj månad: **2026-03**
3. Verifiera att intäkterna visar **76,134 kr** (inte 810,000 kr)
