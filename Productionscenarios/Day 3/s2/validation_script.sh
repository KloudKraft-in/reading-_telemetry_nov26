#!/usr/bin/env bash
# INSTRUCTOR-ONLY helper for TEL-D3-302 (Dynatrace, easyTravel). Learners do not run this.
# Run start/reset ON the easyTravel EC2 host ip-172-30-0-220.  check can run anywhere.
# Usage: ./validation_script.sh start|check|reset [path-to-submitted-evidence.md]
ACTION="${1:-check}"
LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EVIDENCE="${2:-$LAB_DIR/starter/evidence/evidence_D3_2.md}"
CFG="${EASYTRAVEL_CONFIG_URL:-http://localhost:8091/services/ConfigurationService}"
fault() { curl -s "$CFG/setPluginEnabled?name=CreditCardCheckError500&enabled=$1" >/dev/null && echo "$(date -u '+%H:%M:%S UTC')  CreditCardCheckError500 -> $1"; }
case "$ACTION" in
 start)
  fault true
  if [ -n "$DT_ENV_URL" ] && [ -n "$DT_API_TOKEN" ]; then
    curl -sS -X POST "$DT_ENV_URL/api/v2/events/ingest" -H "Authorization: Api-Token $DT_API_TOKEN" -H "Content-Type: application/json; charset=utf-8" \
      -d '{"eventType":"CUSTOM_DEPLOYMENT","title":"easyTravel Checkout Service v2.4.1 Rollout","entitySelector":"type(HOST),entityName.equals(\"ip-172-30-0-220\")","properties":{"deployment.name":"easyTravel Checkout Service v2.4.1 Rollout","deployment.version":"v2.4.1","source":"instructor-runbook"}}'; echo
  else echo "(DT_ENV_URL / DT_API_TOKEN not set: deployment event skipped)"; fi
  echo "Announce the start time to the class.";;
 reset) fault false; echo "Fault OFF. Confirm in the Logs app that no new CreditCardCheckError500 lines appear.";;
 check)
  score=0
  for k in "fetch logs" "dt.process.name" "ErrorCount" "CreditCardCheckError500"; do
    if grep -q -i -F -- "$k" "$EVIDENCE"; then echo "[PASS] mentions $k"; score=$((score+1)); else echo "[FAIL] missing $k"; fi
  done
  if grep -q "<<FILL" "$EVIDENCE"; then echo "[FAIL] placeholders remain"; else echo "[PASS] no placeholders"; score=$((score+1)); fi
  echo "Score: $score/5"; [ "$score" -ge 5 ] && echo "SIGN-OFF OK" || echo "RETRY";;
 *) echo "Usage: $0 start|check|reset [evidence.md]";;
esac
