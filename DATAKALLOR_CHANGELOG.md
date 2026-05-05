# Datakällor Changelog - Ezzat's Controlling System

## 2026-05-05: Uppdatering av Rehab KPI-datakällor

### Ändring
Flyttade Rehab KPI-data från INFO.xlsx KPI-flik till Poänguppföljning Rehab 2026.xlsx.

### Motivering
- Centraliserad datakälla för Rehab-specifik data
- Undvika dubletter och inkonsistens
- Följer Ezzats Inställningar.xlsx

### Nya datakällor (enligt Inställningar.xlsx)

#### Rehab Poäng
- **Tidigare:** INFO.xlsx → KPI-flik → "Rehab Poäng"
- **Nu:** Poänguppföljning Rehab 2026.xlsx → Dashboard-flik → Månatlig data per enhet

#### Teambesök
- **Tidigare:** INFO.xlsx → KPI-flik → "Teambesök / VGR"
- **Nu:** Poänguppföljning Rehab 2026.xlsx → Teambesök VGR-flik → Månatlig data per enhet

### Tekniska ändringar

#### Nya filer
- `rehab_poang_loader_new.py` - Läser Rehab Poäng och Teambesök från Poänguppföljning Rehab 2026.xlsx
  - `load_rehab_poang_from_file()` - Läser från Dashboard-fliken
  - `load_teambesok_from_file()` - Läser från Teambesök VGR-fliken
  - `load_rehab_kpi_from_poang_file()` - Kombinerad funktion för båda KPI:er

#### Uppdaterade filer
- `info_loader.py` - Uppdaterad `load_all_kpi_for_enhet()` för Rehab-enheter
  - Använder nu `rehab_poang_loader_new.py` istället för INFO.xlsx KPI-flik
  - Fallback till INFO.xlsx vid fel

### Påverkade enheter
Alla 16 Rehab-enheter:
- **Stor-Göteborg (8):** Frölunda Torg, Grimmered, Majorna, Pedagogen Park, Åby, Olskroken, Avenyn, Karlastaden
- **Tätort (8):** Torpa, Brålanda, Noltorp, Lilla Edet, Stavre, Åmål, Tanum, Fjällbacka

### Inte påverkat
- VC-enheter: Läser fortfarande Listning och ACG Casemix från INFO.xlsx (INFO-flik och Listning KPI)
- Organisationsdata: Läses fortfarande från INFO.xlsx (Org-flik)

### Test-resultat
✅ Rehab Poäng Dashboard-flik: Fungerar
✅ Teambesök Teambesök VGR-flik: Fungerar
✅ Kombinerad hämtning: Fungerar

---
*Uppdaterad: 2026-05-05*
*Ansvarig: Ezzat Rajab (via Citus)*
