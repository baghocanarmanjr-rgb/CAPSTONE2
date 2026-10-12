$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

# Default to the local Supabase PostgreSQL instance. Override SUPABASE_DB_URL
# before launching if you are intentionally using a hosted/self-hosted server.
if (-not $env:SUPABASE_DB_URL) {
    $env:SUPABASE_DB_URL = "postgresql://postgres:postgres@127.0.0.1:54322/postgres"
}
if (-not $env:PSMS_SECRET_KEY) {
    Write-Host "WARNING: PSMS_SECRET_KEY is not set; using the development fallback." -ForegroundColor Yellow
}

Write-Host "Checking Supabase database..." -ForegroundColor Cyan
python -c "from db import ping; import sys; sys.exit(0 if ping() else 1)"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Local Supabase is not reachable. Run SETUP_LOCAL_SUPABASE.ps1 or 'npx supabase start' first." -ForegroundColor Red
    exit 1
}

Write-Host "Checking offline AI/OCR components..." -ForegroundColor Cyan
python -c "from offline_ocr_mapper import model_status; s=model_status(); print('OCR semantic mapper:', s); raise SystemExit(0 if s.get('active') else 1)"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Offline semantic OCR model is missing or failed to load. Run INSTALL_OFFLINE_OCR_AI.ps1." -ForegroundColor Red
    exit 1
}
python -c "import shutil, os, sys; candidates=[shutil.which('tesseract'), r'C:\Program Files\Tesseract-OCR\tesseract.exe', r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe']; p=next((x for x in candidates if x and os.path.exists(x)), None); print('Tesseract:', p or 'missing'); sys.exit(0 if p else 1)"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Tesseract OCR is missing. Install Tesseract for Windows before starting the system." -ForegroundColor Red
    exit 1
}
python -c "from fasttext_nlp_runtime import model_status; import os; s=model_status(os.path.join(os.getcwd(),'model','fasttext_nlp')); print('FastText runtime:', s); raise SystemExit(0 if s.get('active') else 1)"
if ($LASTEXITCODE -ne 0) {
    Write-Host "FastText PR-PO model is missing or inactive. Install the exported model before starting the system." -ForegroundColor Red
    exit 1
}

Write-Host "Starting Municipality of Asuncion Supply and Property Management System..." -ForegroundColor Green
Write-Host "Open http://127.0.0.1:5000 in the browser." -ForegroundColor Cyan
python .\app.py
