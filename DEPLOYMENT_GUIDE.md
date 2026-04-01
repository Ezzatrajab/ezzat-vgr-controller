# 🚀 DEPLOYMENT TILL STREAMLIT CLOUD - Steg-för-steg

## 📋 ÖVERSIKT

Vi ska deploya din app till Streamlit Cloud så den fungerar:
- ✅ Överallt (4G/5G/WiFi)
- ✅ Utan att din dator är på
- ✅ För alla användare (VEC, Magnus, etc)
- ✅ **100% GRATIS**

---

## STEG 1: SKAPA GITHUB-KONTO (om du inte har)

1. Gå till: https://github.com/signup
2. Skapa konto med din email
3. Verifiera email
4. Logga in

---

## STEG 2: SKAPA GITHUB REPOSITORY

1. Gå till: https://github.com/new
2. Fyll i:
   - **Repository name:** `ezzat-vgr-controller`
   - **Description:** "Ezzat's Controlling System för VGR"
   - **Public** (krävs för gratis Streamlit Cloud)
3. Klicka **"Create repository"**

---

## STEG 3: LADDA UPP FILER TILL GITHUB

### Alternativ A: Via GitHub Web (ENKLAST)

1. På din nya repo-sida, klicka **"uploading an existing file"**

2. Dra och släpp dessa filer:
   ```
   - app_cloud.py
   - requirements.txt
   - .streamlit/config.toml
   ```

3. Skriv commit-meddelande: "Initial deployment"

4. Klicka **"Commit changes"**

### Alternativ B: Via Git Command Line

```bash
cd "C:\Users\ezzat.rajab.AD\claude-workspace\VGR Alla enheter\102"

git init
git add app_cloud.py requirements.txt .streamlit/
git commit -m "Initial deployment"
git branch -M main
git remote add origin https://github.com/DIN-GITHUB-USERNAME/ezzat-vgr-controller.git
git push -u origin main
```

---

## STEG 4: LOGGA IN PÅ STREAMLIT CLOUD

1. Gå till: https://share.streamlit.io/

2. Klicka **"Sign in with GitHub"**

3. Godkänn åtkomst till GitHub

---

## STEG 5: DEPLOYA APPEN

1. När du är inloggad, klicka **"New app"**

2. Fyll i:
   - **Repository:** `DIN-GITHUB-USERNAME/ezzat-vgr-controller`
   - **Branch:** `main`
   - **Main file path:** `app_cloud.py`

3. Klicka **"Deploy!"**

4. Vänta 2-3 minuter medan appen deployar...

---

## STEG 6: TESTA APPEN

När deployment är klar får du en URL typ:

```
https://ezzat-vgr-controller.streamlit.app
```

**Testa:**
1. Öppna länken i browser
2. Logga in med lösenord: `citus2026`
3. Testa på mobil (4G/5G)
4. Dela länken med VEC/Magnus

---

## 🎉 KLART!

Din app är nu live och fungerar överallt!

**Permanent URL:** https://[din-app-namn].streamlit.app

**Dela denna URL med:**
- VEC (Anna Victorin, etc)
- Magnus (CFO)
- Andra som behöver åtkomst

---

## 🔄 UPPDATERA APPEN

När du vill göra ändringar:

1. Redigera filen lokalt
2. Ladda upp till GitHub (samma sätt som STEG 3)
3. Streamlit Cloud uppdaterar automatiskt!

---

## 💡 NÄSTA STEG: KOPPLA TILL GOOGLE SHEETS

För att få real-time data för alla 24 enheter:

1. Flytta budget/actual-data till Google Sheets
2. Uppdatera appen att läsa från Google Sheets API
3. Redeploya

**Säg till när du vill göra detta!**

---

## ❓ FELSÖKNING

### Problem: "App error"
- Kolla att alla filer är uppladdade
- Kolla requirements.txt är korrekt

### Problem: "Module not found"
- Lägg till modulen i requirements.txt
- Redepo

loya

### Problem: Glömt lösenord
- Lösenord: `citus2026`
- Kan ändras i app_cloud.py

---

## 📞 HJÄLP

Om du fastnar, säg till Citus!

---

**Skapad:** 2026-04-01
**Controller:** Ezzat Rajab
**System:** Ezzat's Controlling System
