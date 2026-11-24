<#
.SYNOPSIS
  TEL-D5-502 - Lambda Timeouts: Logs Insights Meets X-Ray (Windows)
.DESCRIPTION
  .\validation_script.ps1 start            initialize the incident
  .\validation_script.ps1 check            run the validation checks on your evidence
  .\validation_script.ps1 reset -Yes       restore the baseline (your work is lost)
#>
param([Parameter(Position = 0)][ValidateSet('start', 'check', 'reset', 'help')][string]$Action = 'check', [switch]$Yes)

$LabDir  = $PSScriptRoot
$Starter = Join-Path $LabDir 'starter'
$EvDir   = Join-Path $Starter 'evidence'
$Evidence = Join-Path $EvDir 'evidence_D5_2.md'
$Template = Join-Path $EvDir 'evidence_D5_2.template.md'
$Py = if (Get-Command python -ErrorAction SilentlyContinue) { 'python' } elseif (Get-Command py -ErrorAction SilentlyContinue) { 'py' } else { $null }
if (-not $Py) { Write-Host 'Python 3 is required (python --version)' -ForegroundColor Red; exit 1 }
if (-not (Test-Path $Template)) { Copy-Item $Evidence $Template }

function Invoke-Start {
    Write-Host '===================================================' -ForegroundColor Yellow
    Write-Host ' Initializing Incident: TEL-D5-502' -ForegroundColor Yellow
    Write-Host ' Lambda Timeouts: Logs Insights Meets X-Ray' -ForegroundColor Yellow
    Write-Host '===================================================' -ForegroundColor Yellow
    Write-Host 'Observed Failure: Order invoice generation Lambdas terminate abruptly with 'Task timed out after 30.00 seconds'. CloudWatch logs show timeouts but do not reveal the stalled downstream call.'
    Write-Host ''
    Write-Host 'Step 1: AWS console -> CloudFormation -> create the stack from starter/aws/invoice-stack.yaml (see starter/README_START_HERE.txt)'
    Write-Host 'Step 2: CloudWatch Logs Insights and X-Ray traces in the console - no CLI needed'
    Write-Host 'Your Mission: follow starter\README_START_HERE.txt'
    Write-Host 'Fill the evidence template: starter\evidence\evidence_D5_2.md'
    Write-Host 'Then validate with: .\validation_script.ps1 check'
}

function Invoke-Check { & $Py (Join-Path $LabDir 'validate.py'); exit $LASTEXITCODE }

function Invoke-Reset {
    Write-Host '===================================================' -ForegroundColor Cyan
    Write-Host ' Resetting Scenario TEL-D5-502...' -ForegroundColor Cyan
    Write-Host '===================================================' -ForegroundColor Cyan
    if (-not $Yes) { Write-Host 'This restores the evidence template - YOUR WORK WILL BE LOST. Re-run with -Yes' -ForegroundColor Yellow; return }
    Copy-Item $Template $Evidence -Force
    Write-Host 'Baseline state restored. Run .\validation_script.ps1 start'
}

switch ($Action) {
    'start' { Invoke-Start }
    'check' { Invoke-Check }
    'reset' { Invoke-Reset }
    default { Write-Host 'Usage: .\validation_script.ps1 {start|check|reset -Yes}' }
}
