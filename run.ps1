# PowerShell Launcher for Finance Data Analysis & AI Automation Dashboard
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host " Finance Data Analysis & AI Automation Dashboard " -ForegroundColor Green
Write-Host "=====================================================================" -ForegroundColor Cyan

Write-Host "Checking Python environment..." -ForegroundColor Yellow
$pyVersion = python --version 2>&1
Write-Host "Detected: $pyVersion" -ForegroundColor Gray

Write-Host "`nLaunching Dashboard..." -ForegroundColor Green
Write-Host "Opening at http://localhost:8501 `n" -ForegroundColor Yellow

python -m streamlit run app.py --browser.gatherUsageStats false
