@echo off
setlocal enabledelayedexpansion
title Finance Data Analysis & AI Automation Dashboard

:: Always ensure current directory is the project directory
cd /d "%~dp0"

echo =====================================================================
echo  Finance Data Analysis & AI Automation Dashboard
echo =====================================================================
echo Working Directory: %CD%

:: Locate Python executable
set "PY_BIN="
where python >nul 2>nul
if %errorlevel% equ 0 (
    set "PY_BIN=python"
) else if exist "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" (
    set "PY_BIN=%LOCALAPPDATA%\Programs\Python\Python314\python.exe"
) else if exist "%ProgramFiles%\Python314\python.exe" (
    set "PY_BIN=%ProgramFiles%\Python314\python.exe"
)

if "%PY_BIN%"=="" (
    echo [ERROR] Python was not found in your system PATH or standard folders.
    echo Please ensure Python 3.10+ is installed.
    echo.
    pause
    exit /b 1
)

echo Using Python: %PY_BIN%
"%PY_BIN%" --version
echo.
echo Launching Dashboard (will open http://localhost:8501 automatically)...
echo.

"%PY_BIN%" launcher.py

if %errorlevel% neq 0 (
    echo.
    echo [NOTICE] Dashboard process ended with code %errorlevel%.
    pause
)
