# ==============================================================================
# SetuAI - Stack Runner (Frontend + Backend + AI Research)
# ==============================================================================

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  Starting SetuAI Linked Stack" -ForegroundColor Cyan
Write-Host "  - Backend API: http://localhost:8000" -ForegroundColor Green
Write-Host "  - Frontend App: http://localhost:3000" -ForegroundColor Green
Write-Host "  - AI Research Engine: Connected via Backend Services" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# 1. Start Backend in a separate window
$backendCmd = "cd '$scriptDir\backend'; if (Test-Path '.venv\Scripts\Activate.ps1') { . '.venv\Scripts\Activate.ps1' }; uvicorn main:app --reload --port 8000"
Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit", "-Command", $backendCmd

# 2. Start Frontend in current window
cd "$scriptDir\frontend\gamifiedsetu"
npm run dev
