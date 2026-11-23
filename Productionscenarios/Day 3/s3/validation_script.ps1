# INSTRUCTOR-ONLY helper for TEL-D3-303 (Datadog, easyTravel). Learners do not run this.
# Run start/reset on a machine that can reach the easyTravel config service (normally the EC2 host).
param([string]$Action = "check", [string]$Evidence = "")
$Lab = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $Evidence) { $Evidence = Join-Path $Lab "starter\evidence\evidence_D3_3.json" }
$Cfg = if ($env:EASYTRAVEL_CONFIG_URL) { $env:EASYTRAVEL_CONFIG_URL } else { "http://localhost:8091/services/ConfigurationService" }
function Set-Fault($v) { Invoke-WebRequest -UseBasicParsing "$Cfg/setPluginEnabled?name=CreditCardCheckError500&enabled=$v" | Out-Null; Write-Host "$((Get-Date).ToUniversalTime().ToString('HH:mm:ss')) UTC  CreditCardCheckError500 -> $v" }
switch ($Action) {
 "start" {
   Set-Fault "true"
   Write-Host "Announce the start time to the class." }
 "reset" { Set-Fault "false" }
 "check" {
   $t = (Get-Content $Evidence -Raw).ToLower(); $s = 0
   foreach ($k in "env:cohort","sum(last_5m)","trace.servlet.request.errors","composite") { if ($t.Contains($k.ToLower())) { Write-Host "[PASS] mentions $k"; $s++ } else { Write-Host "[FAIL] missing $k" } }
   if ($t -match "<<fill") { Write-Host "[FAIL] placeholders remain" } else { Write-Host "[PASS] no placeholders"; $s++ }
   Write-Host "Score: $s/5"; if ($s -ge 5) { Write-Host "SIGN-OFF OK" } else { Write-Host "RETRY" } }
 default { Write-Host "Usage: .\validation_script.ps1 start|check|reset [evidence.md]" }
}
