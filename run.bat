@echo off
title Finance Data Analysis & AI Automation Dashboard
cd /d "%~dp0"

echo =====================================================================
echo  Finance Data Analysis & AI Automation Dashboard
echo =====================================================================
echo Working Directory: %CD%

:: Clean up any lingering process on port 8501 if present
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8501 ^| findstr LISTENING') do (
    echo Freeing port 8501 (PID %%a)...
    taskkill /f /pid %%a >nul 2>nul
)

:: Auto-open browser
start "" http://localhost:8501

echo.
echo Launching Streamlit Server on http://localhost:8501 ...
echo Keep this command window open while using the dashboard.
echo.

python -m streamlit run app.py --server.port 8501 --server.headless true --server.showEmailPrompt false --browser.gatherUsageStats false

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Streamlit encountered an issue (Exit Code %errorlevel%).
    pause
)
