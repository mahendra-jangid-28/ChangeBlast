# ChangeBlast — Run Script (PowerShell)
Write-Host "💥 Starting ChangeBlast..." -ForegroundColor Cyan

Write-Host "[1/2] Starting backend on http://localhost:8000" -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$PSScriptRoot\backend'; python -m uvicorn main:app --port 8000 --reload" -WindowStyle Normal

Start-Sleep 2

Write-Host "[2/2] Starting frontend on http://localhost:5173" -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$PSScriptRoot\frontend'; npm run dev" -WindowStyle Normal

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host " ChangeBlast is running!" -ForegroundColor Cyan
Write-Host " Backend:  http://localhost:8000" -ForegroundColor White
Write-Host " Frontend: http://localhost:5173" -ForegroundColor White
Write-Host " API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "============================================" -ForegroundColor Cyan
