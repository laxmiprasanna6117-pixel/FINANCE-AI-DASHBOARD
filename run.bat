@echo off
title Finance Data Analysis & AI Automation Dashboard
echo =====================================================================
echo  Finance Data Analysis & AI Automation Dashboard
echo =====================================================================
echo Checking Python environment...
python --version
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH. Please install Python 3.10+.
    pause
    exit /b 1
)

echo.
echo Launching Streamlit Dashboard...
echo Local URL: http://localhost:8501
echo.
python -m streamlit run app.py --server.headless false
pause
