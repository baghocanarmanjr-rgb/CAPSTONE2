$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=== Asuncion PSMS: Local Supabase setup ===" -ForegroundColor Cyan

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "Docker was not found. Install Docker Desktop for Windows, start it, then run this script again."
}
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    throw "Node.js was not found. Install Node.js 20 or later, then run this script again."
}
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python was not found. Install Python 3.11+ and enable Add Python to PATH."
}

Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
python -m pip install -r .\requirements.txt

if (-not (Test-Path .\node_modules\supabase)) {
    Write-Host "Installing Supabase CLI as a project dependency..." -ForegroundColor Yellow
    npm install supabase --save-dev
}

if (-not (Test-Path .\supabase\config.toml)) {
    Write-Host "Initializing the Supabase local project..." -ForegroundColor Yellow
    npx supabase init
}

Write-Host "Starting the local Supabase stack..." -ForegroundColor Yellow
# Keep the stack local to this PC. Docker Desktop must already be running.
npx supabase start

$env:SUPABASE_DB_URL = "postgresql://postgres:postgres@127.0.0.1:54322/postgres"
Write-Host "Applying the PSMS PostgreSQL schema..." -ForegroundColor Yellow
python -c "from db import apply_schema; apply_schema(); print('Schema ready.')"

Write-Host "Checking offline OCR semantic model..." -ForegroundColor Yellow
python -c "from offline_ocr_mapper import model_status; s=model_status(); print(s); raise SystemExit(0 if s.get('active') else 1)"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing the offline OCR semantic model (one-time download)..." -ForegroundColor Yellow
    powershell -ExecutionPolicy Bypass -File .\INSTALL_OFFLINE_OCR_AI.ps1
    if ($LASTEXITCODE -ne 0) { throw "Offline OCR semantic model installation failed." }
}

Write-Host "" 
Write-Host "Local Supabase is ready." -ForegroundColor Green
Write-Host "Database: 127.0.0.1:54322/postgres"
Write-Host "Studio:   http://127.0.0.1:54323"
Write-Host "Then start: powershell -ExecutionPolicy Bypass -File .\START_SYSTEM.ps1" -ForegroundColor Cyan
