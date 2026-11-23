# INSTRUCTOR-ONLY sign-off helper for TEL-D2-202. Learners do not run this.
param([string]$Action = "check", [string]$Evidence = "$PSScriptRoot\starter\evidence\evidence_D2_2.md")
switch ($Action) {
  "start" { "Instructor: enable fault CreditCardCheckError500, note UTC start time, announce to class." }
  "reset" { "Instructor: disable fault; confirm problems/monitors recover." }
  "check" {
    $score = 0
    if (Select-String -Path $Evidence -SimpleMatch -Pattern "CreditCardCheckError500" -Quiet) { "[PASS] mentions CreditCardCheckError500"; $score++ } else { "[FAIL] missing CreditCardCheckError500" }
    if (Select-String -Path $Evidence -SimpleMatch -Pattern "trace" -Quiet) { "[PASS] mentions trace"; $score++ } else { "[FAIL] missing trace" }
    if (Select-String -Path $Evidence -SimpleMatch -Pattern "monitor" -Quiet) { "[PASS] mentions monitor"; $score++ } else { "[FAIL] missing monitor" }
    if (Select-String -Path $Evidence -SimpleMatch -Pattern "Datadog" -Quiet) { "[PASS] mentions Datadog"; $score++ } else { "[FAIL] missing Datadog" }
    if (Select-String -Path $Evidence -SimpleMatch -Pattern "<<FILL" -Quiet) { "[FAIL] placeholders remain" } else { "[PASS] no placeholders"; $score++ }
    "Score: $score/5"
    if ($score -ge 5) { "SIGN-OFF OK" } else { "RETRY" }
  }
  default { "Usage: validation_script.ps1 start|check|reset [evidence.md]" }
}
