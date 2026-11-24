<#
.SYNOPSIS
  TEL-D5-503 - Pager Fatigue: Tune the Alarms and Rebuild the Dashboard (Windows)
.DESCRIPTION
  .\validation_script.ps1 start            initialize the incident
  .\validation_script.ps1 check            run the validation checks on your evidence
  .\validation_script.ps1 reset -Yes       restore the baseline (your work is lost)
#>
param([Parameter(Position = 0)][ValidateSet('start', 'check', 'reset', 'help')][string]$Action = 'check', [switch]$Yes)

$LabDir  = $PSScriptRoot
$Starter = Join-Path $LabDir 'starter'
$EvDir   = Join-Path $Starter 'evidence'
$Evidence = Join-Path $EvDir 'evidence_D5_3.md'
$Template = Join-Path $EvDir 'evidence_D5_3.template.md'
$Py = if (Get-Command python -ErrorAction SilentlyContinue) { 'python' } elseif (Get-Command py -ErrorAction SilentlyContinue) { 'py' } else { $null }
if (-not $Py) { Write-Host 'Python 3 is required (python --version)' -ForegroundColor Red; exit 1 }
if (-not (Test-Path $Template)) { Copy-Item $Evidence $Template }

function Invoke-Start {
    Write-Host '===================================================' -ForegroundColor Yellow
    Write-Host ' Initializing Incident: TEL-D5-503' -ForegroundColor Yellow
    Write-Host ' Pager Fatigue: Tune the Alarms and Rebuild the Dashboard' -ForegroundColor Yellow
    Write-Host '===================================================' -ForegroundColor Yellow
    Write-Host 'Observed Failure: On-call engineers receive 80+ alarm notifications per week caused by one-minute CPU spikes and any single failed request. Critical incidents get ignored and the only dashboard is a flat page of 16 widgets.'
    Write-Host ''
    Write-Host 'Step 1: AWS console -> CloudFormation -> create the stack pager-s3-<seat> from starter/aws/pager-stack.yaml (see starter/README_START_HERE.txt)'
    Write-Host 'Step 2: CloudWatch alarms and dashboards in the console - no CLI, no Docker'
    Write-Host 'Your Mission: follow starter\README_START_HERE.txt'
    Write-Host 'Fill the evidence template: starter\evidence\evidence_D5_3.md'
    Write-Host 'Then validate with: .\validation_script.ps1 check'
}

function Invoke-Check { & $Py (Join-Path $LabDir 'validate.py'); exit $LASTEXITCODE }

function Invoke-Reset {
    Write-Host '===================================================' -ForegroundColor Cyan
    Write-Host ' Resetting Scenario TEL-D5-503...' -ForegroundColor Cyan
    Write-Host '===================================================' -ForegroundColor Cyan
    if (-not $Yes) { Write-Host 'This restores the evidence template - YOUR WORK WILL BE LOST. Re-run with -Yes' -ForegroundColor Yellow; return }
    Copy-Item $Template $Evidence -Force
    Remove-Item (Join-Path $EvDir 'tier1.json'), (Join-Path $EvDir 'tier2.json') -ErrorAction SilentlyContinue
    Write-Host 'Baseline state restored. Run .\validation_script.ps1 start'
}

switch ($Action) {
    'start' { Invoke-Start }
    'check' { Invoke-Check }
    'reset' { Invoke-Reset }
    default { Write-Host 'Usage: .\validation_script.ps1 {start|check|reset -Yes}' }
}
