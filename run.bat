@echo off
title Finance Data Analysis & AI Automation Dashboard
echo =========================================================================
echo   Finance Data Analysis & AI Automation Dashboard
echo =========================================================================
echo.
echo Starting Production WSGI Server (Waitress)...
echo Access dashboard at: http://127.0.0.1:5000
echo.
start "" http://127.0.0.1:5000
python app.py
pause
