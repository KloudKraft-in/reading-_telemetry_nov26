# INSTRUCTOR-ONLY sign-off helper for TEL-D2-203. Learners do not run this.
param([string]$Action = "check", [string]$Evidence = "$PSScriptRoot\starter\evidence\evidence_D2_3.md")
switch ($Action) {
  "start" { "Instructor: enable fault CreditCardCheckError500, note UTC start time, announce to class." }
  "reset" { "Instructor: disable fault; confirm problems/monitors recover." }
  "check" {
    $score = 0
    if (Select-String -Path $Evidence -SimpleMatch -Pattern "viewPanel=" -Quiet) { "[PASS] mentions viewPanel="; $score++ } else { "[FAIL] missing viewPanel=" }
    if (Select-String -Path $Evidence -SimpleMatch -Pattern "histogram_quantile" -Quiet) { "[PASS] mentions histogram_quantile"; $score++ } else { "[FAIL] missing histogram_quantile" }
    if (Select-String -Path $Evidence -SimpleMatch -Pattern "Grafana" -Quiet) { "[PASS] mentions Grafana"; $score++ } else { "[FAIL] missing Grafana" }
    if (Select-String -Path $Evidence -SimpleMatch -Pattern "escalat" -Quiet) { "[PASS] mentions escalat"; $score++ } else { "[FAIL] missing escalat" }
    if (Select-String -Path $Evidence -SimpleMatch -Pattern "<<FILL" -Quiet) { "[FAIL] placeholders remain" } else { "[PASS] no placeholders"; $score++ }
    "Score: $score/5"
    if ($score -ge 5) { "SIGN-OFF OK" } else { "RETRY" }
  }
  default { "Usage: validation_script.ps1 start|check|reset [evidence.md]" }
}
