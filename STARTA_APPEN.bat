@echo off
echo ========================================
echo   Ezzat's Controlling System
echo   Startar Streamlit-appen...
echo ========================================
echo.

cd /d "%~dp0"
streamlit run citus_controller_demo.py --server.port 8502

pause
