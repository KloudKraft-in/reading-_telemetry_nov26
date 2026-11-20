# s1 lab controller wrapper:  .\validation_script.ps1 {start|check|reset}
param([string]$Action = "")
$ctl = Join-Path (Split-Path -Parent $PSScriptRoot) "shared\labctl.py"
if (@("start","check","reset") -notcontains $Action) {
    Write-Host "Usage: .\validation_script.ps1 {start|check|reset}"; exit 2
}
$py = $null
foreach ($c in @("python3","python","py")) { if (Get-Command $c -ErrorAction SilentlyContinue) { $py = $c; break } }
if (-not $py) { Write-Host "[ERROR] Python 3 is required."; exit 1 }
if ($py -eq "py") { & py -3 $ctl s1 $Action } else { & $py $ctl s1 $Action }
exit $LASTEXITCODE
