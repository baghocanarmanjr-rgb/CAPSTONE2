param([switch]$ConfirmReset)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not $ConfirmReset) {
    Write-Host "This one-time migration RESETS the local Supabase database, reapplies the schema, and imports data extracted from the old psms.db." -ForegroundColor Yellow
    Write-Host "Run again as: .\MIGRATE_LEGACY_DATA.ps1 -ConfirmReset" -ForegroundColor Cyan
    exit 1
}
if (-not (Test-Path .\supabase\config.toml)) { throw "Run SETUP_LOCAL_SUPABASE.ps1 first." }
if (-not (Test-Path .\supabase\legacy_seed.sql)) { throw "supabase\legacy_seed.sql was not found." }

$seedPath = ".\supabase\seed.sql"
$hadSeed = Test-Path $seedPath
if ($hadSeed) { Copy-Item $seedPath "$seedPath.backup" -Force }
try {
    Copy-Item .\supabase\legacy_seed.sql $seedPath -Force
    Write-Host "Resetting local Supabase and importing legacy data..." -ForegroundColor Yellow
    npx supabase db reset --local
    Write-Host "Legacy data imported successfully." -ForegroundColor Green
}
finally {
    Remove-Item $seedPath -Force -ErrorAction SilentlyContinue
    if ($hadSeed -and (Test-Path "$seedPath.backup")) {
        Move-Item "$seedPath.backup" $seedPath -Force
    }
}
