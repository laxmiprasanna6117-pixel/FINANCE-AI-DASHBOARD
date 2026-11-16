# PowerShell Launcher for Finance Data Analysis & AI Automation Dashboard
Set-Location -Path $PSScriptRoot

Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host " Finance Data Analysis & AI Automation Dashboard " -ForegroundColor Green
Write-Host "=====================================================================" -ForegroundColor Cyan

$pyPath = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $pyPath) {
    $alt = "$env:LOCALAPPDATA\Programs\Python\Python314\python.exe"
    if (Test-Path $alt) { $pyPath = $alt }
}

if (-not $pyPath) {
    Write-Host "[ERROR] Python was not found in system PATH." -ForegroundColor Red
    pause
    exit 1
}

Write-Host "Python Path: $pyPath" -ForegroundColor Gray
Write-Host "`nLaunching Dashboard and opening browser at http://localhost:8501...`n" -ForegroundColor Yellow

& $pyPath launcher.py
