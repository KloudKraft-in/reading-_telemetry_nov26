# TEL-D3-301 - local Docker scenario. Learners run:  .\validation_script.ps1 start | check | reset
param([string]$Action = "check", [string]$Evidence = "")
$Lab = Split-Path -Parent $MyInvocation.MyCommand.Path
$Setup = Join-Path $Lab "starter\setup"
if (-not $Evidence) { $Evidence = Join-Path $Lab "starter\evidence\evidence_D3_1.md" }
$Pass = if ($env:SPLUNK_PASSWORD) { $env:SPLUNK_PASSWORD } else { "Lab-Pass-301!" }
$env:SPLUNK_PASSWORD = $Pass
$C = "tel-d3-301-splunk"

function Invoke-Start {
  if (-not (Get-Command docker -ErrorAction SilentlyContinue)) { Write-Host "[ERROR] docker not found. See Participant Guide, S1 Setup."; return }
  Write-Host "== 1/4 Generating logs (last 4 hours, UTC)"
  Remove-Item -Recurse -Force (Join-Path $Setup "data") -ErrorAction SilentlyContinue
  if (Get-Command python -ErrorAction SilentlyContinue) { python (Join-Path $Setup "gen_retail_logs.py") (Join-Path $Setup "data") }
  else { docker run --rm -v "${Setup}:/s" python:3.12-slim python /s/gen_retail_logs.py /s/data }
  Write-Host "== 2/4 Starting Splunk container (first start takes a few minutes)"
  Push-Location $Setup; docker compose up -d; Pop-Location
  Write-Host "== 3/4 Waiting for Splunk to become healthy"
  $st = ""
  for ($i = 0; $i -lt 60; $i++) { $st = docker inspect -f '{{.State.Health.Status}}' $C 2>$null; if ($st -eq "healthy") { break }; Write-Host -NoNewline "."; Start-Sleep 10 }
  Write-Host ""
  if ($st -ne "healthy") { Write-Host "[ERROR] Splunk did not become healthy. Run: docker logs $C"; return }
  Write-Host "== 4/4 Creating indexes and loading the logs"
  foreach ($idx in "retail_web", "retail_checkout") { docker exec -u splunk $C /opt/splunk/bin/splunk add index $idx -auth "admin:$Pass" 2>$null | Out-Null }
  foreach ($f in Get-ChildItem (Join-Path $Setup "data") -Filter "web-*.log") {
    $h = $f.BaseName -replace '^web-', ''
    docker exec -u splunk $C /opt/splunk/bin/splunk add oneshot "/lab-data/$($f.Name)" -index retail_web -sourcetype retail_web -host $h -auth "admin:$Pass" | Out-Null }
  foreach ($f in Get-ChildItem (Join-Path $Setup "data") -Filter "checkout-*.log") {
    $h = $f.BaseName -replace '^checkout-', ''
    docker exec -u splunk $C /opt/splunk/bin/splunk add oneshot "/lab-data/$($f.Name)" -index retail_checkout -sourcetype retail_checkout -host $h -auth "admin:$Pass" | Out-Null }
  Write-Host ""
  Write-Host "Incident TEL-D3-301 is ready."
  Write-Host "  Open     : http://localhost:8000   (user admin / password: $Pass)"
  Write-Host "  Expected : retail_checkout 3000, retail_web 2400 (wait about 1 minute)"
}
function Invoke-Reset {
  Push-Location $Setup; docker compose down -v 2>$null; Pop-Location
  Remove-Item -Recurse -Force (Join-Path $Setup "data") -ErrorAction SilentlyContinue
  Write-Host "Scenario removed. Your evidence file was not touched."
}
function Invoke-Check {
  Write-Host "==================================================="
  Write-Host " Validating Solution for TEL-D3-301"
  Write-Host "==================================================="
  if (-not (Test-Path $Evidence)) { Write-Host " [ERROR] Evidence file not found: $Evidence"; Write-Host " Total Score: 0/5 (0%)"; return }
  $text = Get-Content $Evidence -Raw
  if ($text -match "<<FILL_") { Write-Host " [WARNING] Detected unfilled placeholder tokens (<<FILL_...>>) in evidence!" }
  $rules = @(@("web-prod-04","Culprit host isolated"), @("rex field=_raw","Regex extraction command used"), @("ERR-[0-9]{4}","Error code pattern matched"), @("timechart","Error codes charted over time"), @("transaction session_id","Sessions grouped with transaction"))
  $p = 0; $n = 0
  foreach ($r in $rules) { $n++
    if ($text.ToLower().Contains($r[0].ToLower())) { Write-Host "  [PASS] Rule ${n}: $($r[1])"; $p++ } else { Write-Host "  [FAIL] Rule ${n}: $($r[1]) (missing: $($r[0]))" } }
  Write-Host "---------------------------------------------------"
  Write-Host " Test Summary: $p / 5 checks passed ($([int]($p*100/5))%)"
  Write-Host "---------------------------------------------------"
  if ($p -eq 5) { Write-Host " [SUCCESS] All validation checks passed successfully!" } else { Write-Host " [RETRY] Fix the missing items and run check again." }
}
switch ($Action) { "start" { Invoke-Start } "reset" { Invoke-Reset } "check" { Invoke-Check } default { Write-Host "Usage: .\validation_script.ps1 start|check|reset [evidence.md]" } }
