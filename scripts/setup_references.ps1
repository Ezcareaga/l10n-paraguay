# scripts/setup_references.ps1 — Clona los repos de referencia para codegraph.
#
# Tras correr este script, ejecutar:
#   python scripts\build_index.py
# para construir el índice consultable vía bin\codegraph.ps1.

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
$RefDir = Join-Path $RepoRoot "references"

New-Item -ItemType Directory -Force -Path $RefDir | Out-Null
Set-Location $RefDir

function CloneIfMissing {
    param([string]$Dir, [string]$Url, [string]$Branch = "18.0")
    $Path = Join-Path $RefDir $Dir
    if (Test-Path $Path) {
        Write-Host "[skip] $Dir already exists" -ForegroundColor Yellow
        return
    }
    Write-Host "[clone] $Dir (branch $Branch)" -ForegroundColor Cyan
    if ($Branch) {
        git clone --depth 1 --branch $Branch $Url $Dir
    } else {
        git clone --depth 1 $Url $Dir
    }
}

# Odoo 18 (sparse) — el más pesado, ~150 MB después de sparse
$OdooDir = Join-Path $RefDir "odoo-18.0"
if (-not (Test-Path $OdooDir)) {
    Write-Host "[clone] odoo-18.0 (sparse — solo addons clave)" -ForegroundColor Cyan
    git clone --depth 1 --branch 18.0 --filter=blob:none --sparse https://github.com/odoo/odoo $OdooDir
    Push-Location $OdooDir
    git sparse-checkout set `
        addons/account `
        addons/account_edi `
        addons/account_edi_ubl_cii `
        addons/l10n_latam_base `
        addons/l10n_latam_invoice_document `
        addons/l10n_pe `
        addons/l10n_ec `
        addons/l10n_ar `
        addons/l10n_cl `
        addons/l10n_co `
        addons/l10n_mx `
        addons/point_of_sale `
        addons/stock `
        addons/product
    Pop-Location
} else {
    Write-Host "[skip] odoo-18.0 already exists" -ForegroundColor Yellow
}

# OCA repos (todos depth=1)
CloneIfMissing "nandefact"                "https://github.com/Ezcareaga/nandefact"            ""
CloneIfMissing "l10n-peru"                "https://github.com/OCA/l10n-peru"                  "18.0"
CloneIfMissing "l10n-ecuador"             "https://github.com/OCA/l10n-ecuador"               "18.0"
CloneIfMissing "l10n-argentina"           "https://github.com/OCA/l10n-argentina"             "18.0"
CloneIfMissing "l10n-brazil"              "https://github.com/OCA/l10n-brazil"                "18.0"
CloneIfMissing "oca-addons-repo-template" "https://github.com/OCA/oca-addons-repo-template"   ""

# Branches viejas — útiles porque OCA aún no portó muchos addons a 18.0
CloneIfMissing "l10n-ecuador-17.0"        "https://github.com/OCA/l10n-ecuador"               "17.0"
CloneIfMissing "l10n-argentina-16.0"      "https://github.com/OCA/l10n-argentina"             "16.0"

Write-Host ""
Write-Host "=== References ready. Run next: ===" -ForegroundColor Green
Write-Host "  python scripts\build_index.py" -ForegroundColor White
