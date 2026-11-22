# INSTRUCTOR-ONLY sign-off helper for TEL-D2-201. Learners do not run this.
param([string]$Action = "check", [string]$Evidence = "$PSScriptRoot\starter\evidence\evidence_D2_1.md")
switch ($Action) {
  "start" { "Instructor: enable fault CreditCardCheckError500, note UTC start time, announce to class." }
  "reset" { "Instructor: disable fault; confirm problems/monitors recover." }
  "check" {
    $score = 0
    if (Select-String -Path $Evidence -SimpleMatch -Pattern "CreditCardCheckError500" -Quiet) { "[PASS] mentions CreditCardCheckError500"; $score++ } else { "[FAIL] missing CreditCardCheckError500" }
    if (Select-String -Path $Evidence -SimpleMatch -Pattern "PurePath" -Quiet) { "[PASS] mentions PurePath"; $score++ } else { "[FAIL] missing PurePath" }
    if (Select-String -Path $Evidence -SimpleMatch -Pattern "root cause" -Quiet) { "[PASS] mentions root cause"; $score++ } else { "[FAIL] missing root cause" }
    if (Select-String -Path $Evidence -SimpleMatch -Pattern "Davis" -Quiet) { "[PASS] mentions Davis"; $score++ } else { "[FAIL] missing Davis" }
    if (Select-String -Path $Evidence -SimpleMatch -Pattern "<<FILL" -Quiet) { "[FAIL] placeholders remain" } else { "[PASS] no placeholders"; $score++ }
    "Score: $score/5"
    if ($score -ge 5) { "SIGN-OFF OK" } else { "RETRY" }
  }
  default { "Usage: validation_script.ps1 start|check|reset [evidence.md]" }
}
