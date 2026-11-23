#!/usr/bin/env bash
# INSTRUCTOR-ONLY helper for TEL-D3-303 (Datadog, easyTravel). Learners do not run this.
# Run start/reset ON the easyTravel EC2 host ip-172-30-0-220.  check can run anywhere.
# Usage: ./validation_script.sh start|check|reset [path-to-submitted-evidence.md]
ACTION="${1:-check}"
LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EVIDENCE="${2:-$LAB_DIR/starter/evidence/evidence_D3_3.json}"
CFG="${EASYTRAVEL_CONFIG_URL:-http://localhost:8091/services/ConfigurationService}"
fault() { curl -s "$CFG/setPluginEnabled?name=CreditCardCheckError500&enabled=$1" >/dev/null && echo "$(date -u '+%H:%M:%S UTC')  CreditCardCheckError500 -> $1"; }
case "$ACTION" in
 start)
  fault true
  echo "Announce the start time to the class.";;
 reset) fault false; echo "Fault OFF. Remove leftover [u..] monitors (tag lab:d3-303), composites first.";;
 check)
  score=0
  for k in "env:cohort" "sum(last_5m)" "trace.servlet.request.errors" "composite"; do
    if grep -q -i -F -- "$k" "$EVIDENCE"; then echo "[PASS] mentions $k"; score=$((score+1)); else echo "[FAIL] missing $k"; fi
  done
  if grep -q "<<FILL" "$EVIDENCE"; then echo "[FAIL] placeholders remain"; else echo "[PASS] no placeholders"; score=$((score+1)); fi
  echo "Score: $score/5"; [ "$score" -ge 5 ] && echo "SIGN-OFF OK" || echo "RETRY";;
 *) echo "Usage: $0 start|check|reset [evidence.md]";;
esac
