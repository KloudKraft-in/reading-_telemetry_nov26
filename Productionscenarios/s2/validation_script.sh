#!/usr/bin/env bash
# INSTRUCTOR-ONLY sign-off helper for TEL-D2-202. Learners do not run this.
# Usage: ./validation_script.sh check [path-to-submitted-evidence.md]
ACTION="${1:-check}"
LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EVIDENCE="${2:-$LAB_DIR/starter/evidence/evidence_D2_2.md}"
case "$ACTION" in
 start) echo "Instructor: enable fault CreditCardCheckError500, note UTC start time, announce to class.";;
 reset) echo "Instructor: disable fault; confirm problems/monitors recover.";;
 check)
  score=0
  for k in "CreditCardCheckError500" "trace" "monitor" "Datadog"; do
    if grep -q -i -F -- "$k" "$EVIDENCE"; then echo "[PASS] mentions $k"; score=$((score+1)); else echo "[FAIL] missing $k"; fi
  done
  if grep -q "<<FILL" "$EVIDENCE"; then echo "[FAIL] placeholders remain"; else echo "[PASS] no placeholders"; score=$((score+1)); fi
  echo "Score: $score/5"; [ "$score" -ge 5 ] && echo "SIGN-OFF OK" || echo "RETRY";;
 *) echo "Usage: $0 start|check|reset [evidence.md]";;
esac
