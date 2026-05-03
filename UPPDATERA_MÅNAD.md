# 📅 Snabbguide: Uppdatera Dashboard med Nya Månadssiffror

**Tid:** ~5 minuter (när du vet vad du ska göra)

---

## 🎯 Steg-för-steg (April 2026 exempel)

### 1️⃣ Uppdatera INFO.xlsx
📁 **Plats:** `VGR Alla enheter/data/INFO.xlsx`

**Vad du gör:**
- Öppna INFO.xlsx i Excel
- Lägg till ny kolumn för April 2026 (202604)
- Fyll i siffrorna för alla enheter:
  - Antal listade pat
  - Listningspoäng
  - ACG Casemix
  - Huvudintäkter
  - Medical staff
- Spara och stäng

✅ **Detta är viktigaste filen - den innehåller 80% av all data!**

---

### 2️⃣ Uppdatera FTE-filer
📁 **Plats:** `VGR Alla enheter/[ENHET-NUMMER]/FTE Producerande per Yrkesgrupp (X).xlsx`

**För varje enhet:**
- Öppna FTE-filen
- Lägg till April 2026 i nästa kolumn
- Fyll i FTE Budget och Actual
- Spara

**Snabbast:** Om du får alla FTE-filer från ekonomisystemet, bara kopiera över dem!

---

### 3️⃣ Uppdatera P&L Budget-filer (för Tätort)
📁 **Plats:** `VGR Alla enheter/[ENHET-NUMMER]/P&L Budget.xlsx`

**Endast för Tätort-enheter:** 003, 005, 006, 008, 014, 305, 703, 705, 706, 708, 714, 650-670, 713

**Vad du gör:**
- Öppna P&L Budget.xlsx
- Kontrollera att April 2026 (202604) finns med
- Budget för Medical staff ska finnas
- Spara

**VIKTIGT:** 
- Personalkostnad **Actual** hämtas från INFO.xlsx (steg 1)
- Personalkostnad **Budget** hämtas från P&L Budget.xlsx (detta steg)

---

### 4️⃣ Uppdatera Dashboard-appen

**Öppna Claude Code och kör:**

```bash
cd "C:\Users\ezzat.rajab.AD\claude-workspace\VGR Alla enheter\Dashboard"
```

**Säg till Claude:**
> "Uppdatera dashboard för April 2026 - jag har uppdaterat alla Excel-filer"

**Claude kommer att:**
1. Testa att data laddas korrekt
2. Uppdatera versionsnummer (v5.2 → v5.3)
3. Committa och pusha till GitHub
4. Streamlit Cloud uppdateras automatiskt (2-3 min)

---

## 🚀 Snabbversion (när du är van)

1. **Uppdatera INFO.xlsx** (lägg till ny månad för alla enheter)
2. **Kopiera in nya FTE-filer** (från ekonomisystemet)
3. **Kopiera in nya P&L Budget-filer** (från ekonomisystemet)
4. **Säg till Claude:** "Uppdatera dashboard för [månad] - jag har uppdaterat filerna"
5. **Vänta 2-3 min** → Klart! ✅

---

## 📋 Checklista Filer per Enhet

### Stor-Göteborg (20 enheter):
- [ ] INFO.xlsx (alla enheter i EN fil)
- [ ] FTE Producerande per Yrkesgrupp (X).xlsx (per enhet)

### Tätort (14 enheter):
- [ ] INFO.xlsx (alla enheter i EN fil)
- [ ] FTE Producerande per Yrkesgrupp (X).xlsx (per enhet)
- [ ] P&L Budget.xlsx (per enhet - för personalkostnad budget)

---

## ⚠️ Vanliga Problem & Lösningar

### Problem: "Period 202604 hittades inte"
**Lösning:** Du har glömt lägga till månadens kolumn i INFO.xlsx eller FTE-filerna

### Problem: "Personalkostnad budget = 0"
**Lösning:** Kontrollera P&L Budget.xlsx för Tätort-enheter - kolumnen för rätt månad ska finnas

### Problem: Streamlit visar gamla siffror
**Lösning:** 
1. Vänta 2-3 minuter efter push
2. Hard refresh: Ctrl+F5
3. Om inte: Reboot app på Streamlit Cloud

---

## 💾 Backup

**Innan du börjar uppdatera:**
```bash
# Ta backup av data-mappen
cd "C:\Users\ezzat.rajab.AD\claude-workspace\VGR Alla enheter"
cp -r data data_backup_[DATUM]
```

**Om något går fel:**
```bash
# Återställ från backup
rm -rf data
cp -r data_backup_[DATUM] data
```

---

## 🎓 Tips för Snabbhet

1. **Automatisera Excel-uppdatering:** 
   - Be IT/ekonomi om export direkt från systemet
   - Power Query kan koppla Excel-filer direkt till datakällan

2. **Batch-uppdatera FTE-filer:**
   - Om alla FTE-filer har samma struktur, kopiera in en hel mapp

3. **Använd mallar:**
   - Spara en "mall-månad" som du kan kopiera

---

**Skapad:** 2026-04-12  
**Senast testad:** Mars 2026 → April 2026 (fungerar perfekt!)
