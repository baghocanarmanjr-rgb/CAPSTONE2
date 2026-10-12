$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
Write-Host "=== Install Offline OCR Semantic Mapper ===" -ForegroundColor Cyan
if (-not (Get-Command python -ErrorAction SilentlyContinue)) { throw "Python was not found in PATH." }
python -m pip --version
if ($LASTEXITCODE -ne 0) { throw "pip is unavailable for this Python installation." }
Write-Host "Installing local semantic dependencies..." -ForegroundColor Yellow
python -m pip install "rapidfuzz>=3.9,<4" "sentence-transformers>=3.0,<6" "torch"
if ($LASTEXITCODE -ne 0) { throw "Python dependency installation failed." }
Write-Host "Downloading the model once and saving it locally..." -ForegroundColor Yellow
python .\download_ocr_mapper_model.py
if ($LASTEXITCODE -ne 0) { throw "Model download/save failed." }
Write-Host "Verifying strict local-only loading..." -ForegroundColor Cyan
$env:HF_HUB_OFFLINE = "1"
$env:TRANSFORMERS_OFFLINE = "1"
python -c "from offline_ocr_mapper import model_status; s=model_status(); print(s); raise SystemExit(0 if s.get('active') else 1)"
if ($LASTEXITCODE -ne 0) { throw "Local semantic mapper verification failed." }
Write-Host "PASS: Offline OCR semantic mapper installed and loads from disk." -ForegroundColor Green
