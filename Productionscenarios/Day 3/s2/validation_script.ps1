# INSTRUCTOR-ONLY helper for TEL-D3-302 (Dynatrace, easyTravel). Learners do not run this.
# Run start/reset on a machine that can reach the easyTravel config service (normally the EC2 host).
param([string]$Action = "check", [string]$Evidence = "")
$Lab = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $Evidence) { $Evidence = Join-Path $Lab "starter\evidence\evidence_D3_2.md" }
$Cfg = if ($env:EASYTRAVEL_CONFIG_URL) { $env:EASYTRAVEL_CONFIG_URL } else { "http://localhost:8091/services/ConfigurationService" }
function Set-Fault($v) { Invoke-WebRequest -UseBasicParsing "$Cfg/setPluginEnabled?name=CreditCardCheckError500&enabled=$v" | Out-Null; Write-Host "$((Get-Date).ToUniversalTime().ToString('HH:mm:ss')) UTC  CreditCardCheckError500 -> $v" }
switch ($Action) {
 "start" {
   Set-Fault "true"
   if ($env:DT_ENV_URL -and $env:DT_API_TOKEN) {
     $body = '{"eventType":"CUSTOM_DEPLOYMENT","title":"easyTravel Checkout Service v2.4.1 Rollout","entitySelector":"type(HOST),entityName.equals(\"ip-172-30-0-220\")","properties":{"deployment.name":"easyTravel Checkout Service v2.4.1 Rollout","deployment.version":"v2.4.1","source":"instructor-runbook"}}'
     Invoke-RestMethod -Method Post -Uri "$($env:DT_ENV_URL)/api/v2/events/ingest" -Headers @{Authorization="Api-Token $($env:DT_API_TOKEN)"} -ContentType "application/json; charset=utf-8" -Body $body
   } else { Write-Host "(DT_ENV_URL / DT_API_TOKEN not set: deployment event skipped)" }
   Write-Host "Announce the start time to the class." }
 "reset" { Set-Fault "false" }
 "check" {
   $t = (Get-Content $Evidence -Raw).ToLower(); $s = 0
   foreach ($k in "fetch logs","dt.process.name","ErrorCount","CreditCardCheckError500") { if ($t.Contains($k.ToLower())) { Write-Host "[PASS] mentions $k"; $s++ } else { Write-Host "[FAIL] missing $k" } }
   if ($t -match "<<fill") { Write-Host "[FAIL] placeholders remain" } else { Write-Host "[PASS] no placeholders"; $s++ }
   Write-Host "Score: $s/5"; if ($s -ge 5) { Write-Host "SIGN-OFF OK" } else { Write-Host "RETRY" } }
 default { Write-Host "Usage: .\validation_script.ps1 start|check|reset [evidence.md]" }
}
