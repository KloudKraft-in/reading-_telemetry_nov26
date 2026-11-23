<#
.SYNOPSIS
  TEL-D4-403 - Latency Percentile and Service Variable Are Wrong (Windows)
.DESCRIPTION
  .\validation_script.ps1 start            start the Docker kit and the incident
  .\validation_script.ps1 check            run the validation checks
  .\validation_script.ps1 reset -Yes       remove containers and restore the evidence template (your work is lost)
#>
param([Parameter(Position = 0)][ValidateSet('start', 'check', 'reset', 'help')][string]$Action = 'check', [switch]$Yes)

$LabDir = $PSScriptRoot
$Kit    = Join-Path $LabDir 'starter\kit'
$EvDir  = Join-Path $LabDir 'starter\evidence'
$Py = if (Get-Command python -ErrorAction SilentlyContinue) { 'python' } elseif (Get-Command py -ErrorAction SilentlyContinue) { 'py' } else { $null }
if (-not $Py) { Write-Host 'Python 3 is required (python --version)' -ForegroundColor Red; exit 1 }
function Wait-Http($url) {
    Write-Host -NoNewline "Waiting for $url "
    for ($i = 0; $i -lt 90; $i++) {
        try { if ((Invoke-WebRequest -UseBasicParsing $url -TimeoutSec 2).StatusCode -eq 200) { Write-Host ' ok'; return } } catch {}
        Write-Host -NoNewline '.'; Start-Sleep 2
    }
    Write-Host ' (not ready - continue anyway)'
}

function Invoke-Start {
    Write-Host '===================================================' -ForegroundColor Yellow
    Write-Host ' Initializing Incident: TEL-D4-403' -ForegroundColor Yellow
    Write-Host ' Latency Percentile and Service Variable Are Wrong' -ForegroundColor Yellow
    Write-Host '===================================================' -ForegroundColor Yellow
    Write-Host 'Observed Failure: SRE dashboard latency percentiles show flat lines measuring cumulative stats since server reboot, and selecting a service in the variable dropdown causes panels to show 'No Data'.'
    Write-Host ''
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) { Write-Host 'Docker is required (docker compose version)' -ForegroundColor Red; exit 1 }
    Push-Location $Kit; docker compose up -d; Pop-Location
    Wait-Http 'http://localhost:3000/api/health'; Wait-Http 'http://localhost:9090/-/ready'
    & $Py (Join-Path $LabDir 'validate.py') import
    Write-Host 'Let it run 5-10 minutes so that Prometheus has data for rate().'
    Write-Host 'Grafana: http://localhost:3000 (user admin, password = GRAFANA_PASSWORD in starter\kit\.env) -> Dashboards -> ShopNow SRE Dashboard'
    Write-Host 'Prometheus: http://localhost:9090'
    Write-Host 'Your Mission: follow starter\README_START_HERE.txt'
    Write-Host 'Fill the evidence template: starter\evidence\evidence_D4_3.json'
    Write-Host 'Then validate with: .\validation_script.ps1 check'
}

function Invoke-Check { & $Py (Join-Path $LabDir 'validate.py'); exit $LASTEXITCODE }

function Invoke-Reset {
    Write-Host '===================================================' -ForegroundColor Cyan
    Write-Host ' Resetting Scenario TEL-D4-403...' -ForegroundColor Cyan
    Write-Host '===================================================' -ForegroundColor Cyan
    if (-not $Yes) { Write-Host 'This deletes the containers, your Grafana/Prometheus changes and your evidence - YOUR WORK WILL BE LOST. Re-run with -Yes' -ForegroundColor Yellow; return }
    Push-Location $Kit; docker compose down -v; Pop-Location
    Remove-Item (Join-Path $Kit 'control\fault') -ErrorAction SilentlyContinue
    Copy-Item (Join-Path $EvDir 'evidence_D4_3.template.json') (Join-Path $EvDir 'evidence_D4_3.json') -Force
    Write-Host 'Baseline state restored. Run .\validation_script.ps1 start'
}

switch ($Action) {
    'start' { Invoke-Start }
    'check' { Invoke-Check }
    'reset' { Invoke-Reset }
    default { Write-Host 'Usage: .\validation_script.ps1 {start|check|reset -Yes}' }
}
