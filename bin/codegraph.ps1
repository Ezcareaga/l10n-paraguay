# bin/codegraph.ps1 — wrapper PowerShell para el CLI codegraph
#
# Uso:
#   .\bin\codegraph.ps1 search "account.edi.format inheritance"
#   .\bin\codegraph.ps1 symbol "L10nLatamDocumentType"
#   .\bin\codegraph.ps1 file "references/odoo-18.0/addons/l10n_pe/__manifest__.py"
#   .\bin\codegraph.ps1 stats

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
$Cli = Join-Path $RepoRoot "scripts\codegraph_cli.py"

# Detectar python disponible
$Python = if (Get-Command python -ErrorAction SilentlyContinue) { "python" }
          elseif (Get-Command py -ErrorAction SilentlyContinue) { "py" }
          else { throw "Python not found. Install Python 3.11+ and ensure it's on PATH." }

& $Python $Cli @args
exit $LASTEXITCODE
