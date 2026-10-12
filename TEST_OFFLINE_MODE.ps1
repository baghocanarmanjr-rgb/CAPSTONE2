$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$env:HF_HUB_OFFLINE = "1"
$env:TRANSFORMERS_OFFLINE = "1"
Write-Host "Testing local semantic model without network downloads..." -ForegroundColor Cyan
python -c "from offline_ocr_mapper import model_status; s=model_status(); print(s); raise SystemExit(0 if s.get('active') else 1)"
Write-Host "Testing database..." -ForegroundColor Cyan
python -c "from db import ping; print('Database connected:', ping()); raise SystemExit(0 if ping() else 1)"
Write-Host "Offline prerequisites verified." -ForegroundColor Green
