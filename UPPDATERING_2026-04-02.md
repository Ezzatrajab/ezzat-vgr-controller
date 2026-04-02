# UPPDATERING: Ezzat's Controlling System - RÄTT DATA! ✅

**Datum:** 2026-04-02  
**Status:** KLAR FÖR DEPLOYMENT

---

## 🎯 Problemet som fixats

Tidigare version hade **hårdkodad demo-data** som inte stämde med verkligheten:
- ❌ FTE-siffror felaktiga
- ❌ Personalkostnader felaktiga  
- ❌ Rehab resultat felaktiga

---

## ✅ Lösningen: Dynamisk datahämtning

### Ny fil: `data_loader_functions.py`

Alla funktioner som hämtar **RÄTT** data från Excel-filer:

#### 1. **FTE Actual** 
- Källa: `FTE Producerande per Yrkesgrupp (X).xlsx`
- Funktion: `load_fte_actual(enhet_kst, manad_str)`

#### 2. **FTE Budget**
- Källa: `HR Cost (X).xlsx` 
- Funktion: `load_fte_budget(enhet_kst, manad_str)`
- Läser från Total-raden (dynamiskt)

#### 3. **Personalkostnader (Actual & Budget)**
- Källa: `P&L Actual.xlsx` och `P&L Budget.xlsx`
- Funktion: `load_personalkostnad(enhet_kst, manad_str)`
- Läser från: COGS > Medical staff > Total

#### 4. **Rehab Budgeterade Poäng** (endast Rehab-enheter)
- Källa: `Intäkt Budget Rehab (X).xlsx`
- Funktion: `load_rehab_poang_budget(enhet_kst, manad_str)`
- Returnerar:
  - Måltal per prestationsanställd
  - Antal prestationsanställda
  - Budgeterad intäkt

#### 5. **All-in-one funktion**
- Funktion: `load_all_data_for_enhet(enhet_kst, manad_str)`
- Returnerar ALL data för en enhet och månad

---

## 📊 Verifierade Resultat (2026-01)

### 601 - Frölunda Torg Rehab
```
FTE Actual:              4.38
FTE Budget:              5.38
FTE Avvikelse:          -1.00
Personalkostnad Actual:  327,791 kr
Personalkostnad Budget:  285,303 kr
Avvikelse:              +42,488 kr

Rehab Budget:
  Måltal:                240
  Antal anställda:       4.67
  Budgeterad intäkt:     585,760 kr
```

### 602 - Grimmered Rehab
```
FTE Actual:              4.12
FTE Budget:              5.58
FTE Avvikelse:          -1.46
Personalkostnad Actual:  296,692 kr
Personalkostnad Budget:  300,738 kr
Avvikelse:              -4,046 kr

Rehab Budget:
  Måltal:                240
  Antal anställda:       4.19
  Budgeterad intäkt:     525,615 kr
```

### 102 - Frölunda Torg VC
```
FTE Actual:             16.12
FTE Budget:             21.69
FTE Avvikelse:          -5.57
Personalkostnad Actual:  1,639,770 kr
Personalkostnad Budget:  1,742,291 kr
Avvikelse:              -102,521 kr
```

### 103 - Grimmered VC
```
FTE Actual:             15.50
FTE Budget:             19.19
FTE Avvikelse:          -3.69
Personalkostnad Actual:  1,572,593 kr
Personalkostnad Budget:  1,487,013 kr
Avvikelse:              +85,581 kr   ⚠️ ÖVER BUDGET trots färre FTE!
```

---

## 🔧 Ändringar i `app_cloud.py`

### 1. **Ny import**
```python
from data_loader_functions import load_all_data_for_enhet, load_rehab_poang_budget
```

### 2. **Uppdaterad `get_current_data()`**
- ❌ Tar INTE längre data från hårdkodad `ENHETER_DATA`
- ✅ Hämtar ALL data dynamiskt från Excel-filer
- Uppdaterar:
  - `fte` (actual & budget)
  - `personalkostnad` (actual & budget)
  - `rehab_budget_*` (för Rehab-enheter)

### 3. **Uppdaterad `analyze_personal_avvikelser()`**
- ❌ Använder INTE längre hårdkodad `fte_breakdown`
- ✅ Analyserar total FTE och personalkostnadsavvikelser
- Flaggar avvikelser > 5%
- Kritisk varning vid > 20%

---

## 📁 Filstruktur

```
Dashboard/
├── app_cloud.py                    (Uppdaterad med nya funktioner)
├── data_loader_functions.py        (NY FIL - alla datahämtningsfunktioner)
├── data/
│   ├── 601/
│   │   ├── FTE Producerande per Yrkesgrupp (7).xlsx
│   │   ├── HR Cost (12).xlsx
│   │   ├── Intäkt Budget Rehab (26).xlsx
│   │   ├── P&L Actual.xlsx
│   │   └── P&L Budget.xlsx
│   ├── 602/
│   │   ├── FTE Producerande per Yrkesgrupp (8).xlsx
│   │   ├── HR Cost (13).xlsx
│   │   ├── Intäkt Budget Rehab (27).xlsx
│   │   ├── P&L Actual.xlsx
│   │   └── P&L Budget.xlsx
│   └── KPIer Storg-GBG.xlsx
└── UPPDATERING_2026-04-02.md       (Detta dokument)
```

**OBS:** För 102 och 103 hämtas data från:
```
VGR Alla enheter/
├── 102/
│   ├── FTE Producerande per Yrkesgrupp (4).xlsx
│   ├── HR Cost (10).xlsx
│   ├── P&L Actual.xlsx
│   └── P&L Budget.xlsx
└── 103/
    ├── FTE Producerande per Yrkesgrupp (5).xlsx
    ├── HR Cost (11).xlsx
    ├── P&L Actual.xlsx
    └── P&L Budget.xlsx
```

---

## 🚀 Nästa Steg

### 1. Testa lokalt
```bash
cd "C:\Users\ezzat.rajab.AD\claude-workspace\VGR Alla enheter\Dashboard"
streamlit run app_cloud.py
```

### 2. Uppdatera GitHub Repository
```bash
git add app_cloud.py data_loader_functions.py
git commit -m "Fix: Hämta RÄTT data från Excel-filer (FTE, personalkostnader, Rehab budget)"
git push origin main
```

### 3. Streamlit Cloud deployment
- Streamlit Cloud kommer automatiskt att deployas när du pushar till `main`
- URL: https://ezzat-vgr-controller-egmledvvicrntapps59uurv.streamlit.app/
- **OBS:** Data-filerna måste finnas i `data/` mappen i GitHub-repo

### 4. Kopiera data-filer till GitHub
För att Streamlit Cloud ska fungera behöver du:
```bash
# Från lokalt Dashboard
cp -r data/ [path-to-github-repo]/data/
```

Eller:
- Manuellt lägga till alla Excel-filer i repo under `data/601/`, `data/602/`, etc.

---

## 💡 Viktiga Insikter från Data

### 103 - Grimmered VC (VARNING! 🔴)
- FTE: **15.50 actual** vs **19.19 budget** = **-3.69 FTE** (-19.2%)
- Personalkostnad: **1,572,593 kr** vs **1,487,013 kr** = **+85,581 kr** (+5.8%)

**ANALYS:**
- Färre anställda än budgeterat (-19%)
- Men HÖGRE kostnader än budget (+6%)
- **Trolig orsak:** Högre löner, övertid, eller dyra konsulter?
- **ÅTGÄRD:** Undersök lönekostnader per FTE och identifiera varför kostnaden är så hög

### 601 & 602 Rehab
- Båda har färre FTE än budgeterat
- 601: +42,488 kr över budget
- 602: -4,046 kr under budget

---

## ✅ Verifiering

Kör testfilen:
```bash
python data_loader_functions.py
```

Output visar korrekt data för alla 4 enheter (102, 103, 601, 602).

---

**Skapad av:** Citus (Ezzats AI Agent)  
**Datum:** 2026-04-02
