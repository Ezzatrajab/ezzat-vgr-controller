# 📊 Ezzat's Controlling System - Startinstruktioner

## 🚀 HUR STARTAR JAG APPEN?

### Steg 1: Öppna Terminal/Command Prompt
- Tryck `Windows + R`
- Skriv `cmd` och tryck Enter

### Steg 2: Navigera till mappen
```bash
cd "C:\Users\ezzat.rajab.AD\claude-workspace\VGR Alla enheter\102"
```

### Steg 3: Starta appen
```bash
streamlit run citus_controller_demo.py --server.port 8502
```

### Steg 4: Öppna i browser
Appen öppnas automatiskt, eller gå till:

**På datorn:**
```
http://localhost:8502
```

**På mobil (samma WiFi):**
```
http://10.214.10.88:8502
```

---

## 🔐 INLOGGNING

**Lösenord:** `citus2026`

---

## 📱 ANVÄND PÅ MOBIL (SAMMA WIFI)

1. Öppna Safari/Chrome på telefonen
2. Gå till: `http://10.214.10.88:8502`
3. Logga in med lösenordet
4. Använd appen!

---

## 🛑 STOPPA APPEN

I terminalen där appen körs:
- Tryck `Ctrl + C`

---

## 💡 FELSÖKNING

### Problem: Port redan använd
```bash
# Använd en annan port
streamlit run citus_controller_demo.py --server.port 8503
```

### Problem: "streamlit not found"
```bash
# Installera Streamlit
python -m pip install streamlit plotly pandas openpyxl
```

### Problem: Kan inte öppna på mobil
- Kontrollera att du är på samma WiFi-nätverk
- Kontrollera att appen körs på datorn
- Prova: `http://localhost:8502` på datorn först

---

## ☁️ NÄSTA STEG: DEPLOYA TILL MOLNET

När du vill att appen ska fungera:
- ✅ På 4G/5G
- ✅ Utan att din dator är på
- ✅ Överallt i världen
- ✅ För alla användare (VEC, Magnus, etc)

**Då deployar vi till Streamlit Cloud (gratis!)**

Säg till Citus när du är redo!

---

## 📊 FILER I DENNA MAPP

- `citus_controller_demo.py` - Huvudappen
- `P&L Budget.xlsx` - Budget P&L data
- `P&L Actual.xlsx` - Actual P&L data
- `FTE Producerande per Yrkesgrupp (4).xlsx` - Personal FTE data
- `HR Cost (10).xlsx` - Personalkostnader
- `2 Intäktsbudget...xlsx` - Intäktsbudget
- `vec_comments.json` - Sparade VEC-kommentarer (skapas automatiskt)
- `START_APPEN.md` - Denna fil!

---

**Skapad:** 2026-04-01
**Controller:** Ezzat Rajab
**System:** Ezzat's Controlling System - Demo v1.0
