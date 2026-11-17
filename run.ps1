Write-Host "=========================================================================" -ForegroundColor Cyan
Write-Host "  Finance Data Analysis & AI Automation Dashboard" -ForegroundColor White
Write-Host "=========================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting Production WSGI Server (Waitress)..." -ForegroundColor Green
Write-Host "Access dashboard at: http://127.0.0.1:5000" -ForegroundColor Yellow
Write-Host ""
Start-Process "http://127.0.0.1:5000"
python "c:\Users\prasa\OneDrive\Documents\FDA AI Project\app.py"
