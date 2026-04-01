@echo off
echo ========================================
echo   Testar CLOUD VERSION lokalt
echo   (samma version som kommer deployeras)
echo ========================================
echo.

cd /d "%~dp0"
streamlit run app_cloud.py --server.port 8503

pause
