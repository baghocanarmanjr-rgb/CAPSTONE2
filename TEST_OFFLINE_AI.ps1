$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$env:HF_HUB_OFFLINE = "1"
$env:TRANSFORMERS_OFFLINE = "1"
Write-Host "Testing semantic mapper with network-independent local loading..." -ForegroundColor Cyan
python -c "from offline_ocr_mapper import model_status; s=model_status(); print(s); raise SystemExit(0 if s.get('active') else 1)"
if ($LASTEXITCODE -ne 0) { throw "Semantic mapper offline test failed." }
python -c "from offline_ocr_mapper import classify_field; print('Financial Requirement =>', classify_field('Financial Requirement','PHP 96000')[0:2]); print('Required Units =>', classify_field('Required Units','4 units managed switch')[0:2])"
Write-Host "PASS: local semantic mapping works without runtime downloads." -ForegroundColor Green
