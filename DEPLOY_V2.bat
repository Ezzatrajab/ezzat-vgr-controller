@echo off
echo ================================================
echo DEPLOYA DASHBOARD V2 TILL STREAMLIT CLOUD
echo ================================================
echo.

cd /d "%~dp0"

echo [1/3] Staging filer...
git add app_cloud.py
git add UPPDATERINGAR_V2.md
git add DEPLOY_V2.bat

echo.
echo [2/3] Skapar commit...
git commit -m "Dashboard v2: Manadsval, ACG Casemix, Rehab-poang, forbattrad avvikelseanalys"

echo.
echo [3/3] Pushar till GitHub...
git push origin main

echo.
echo ================================================
echo ✅ KLART!
echo ================================================
echo.
echo Streamlit Cloud uppdaterar nu automatiskt...
echo Vanta 1-2 minuter, sen ladda om:
echo.
echo https://ezzat-vgr-controller-egmledvvicrntapps59uurv.streamlit.app/
echo.
echo Losenord: citus2026
echo.
pause
