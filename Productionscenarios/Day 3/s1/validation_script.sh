#!/usr/bin/env bash
# TEL-D3-301 — local Docker scenario. Learners run:  ./validation_script.sh start | check | reset
# start : builds the local Splunk container, generates the logs and loads them (about 5 minutes)
# check : self-check of starter/evidence/evidence_D3_1.md (5 keyword rules)
# reset : removes the container and the generated data
ACTION="${1:-check}"
LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SETUP="$LAB_DIR/starter/setup"
EVIDENCE="${2:-$LAB_DIR/starter/evidence/evidence_D3_1.md}"
PASS="${SPLUNK_PASSWORD:-Lab-Pass-301!}"
C=tel-d3-301-splunk
export SPLUNK_PASSWORD="$PASS"

need() { command -v "$1" >/dev/null 2>&1 || { echo "[ERROR] '$1' not found. Install it first (see Participant Guide, S1 Setup)."; exit 1; }; }

invoke_start() {
  need docker; docker compose version >/dev/null 2>&1 || { echo "[ERROR] Docker Compose v2 is required."; exit 1; }
  if (command -v ss >/dev/null && ss -ltn 2>/dev/null | grep -q ':8000 ') && ! docker ps --format '{{.Names}}' | grep -q "^$C$"; then
    echo "[ERROR] Port 8000 is already in use. Stop the other program, then run start again."; exit 1; fi
  echo "== 1/4 Generating logs (last 4 hours, UTC)"
  rm -rf "$SETUP/data"
  if command -v python3 >/dev/null 2>&1; then python3 "$SETUP/gen_retail_logs.py" "$SETUP/data"
  else docker run --rm -v "$SETUP:/s" python:3.12-slim python /s/gen_retail_logs.py /s/data; fi
  echo "== 2/4 Starting Splunk container (first start downloads the image and takes a few minutes)"
  ( cd "$SETUP" && docker compose up -d )
  echo "== 3/4 Waiting for Splunk to become healthy"
  for i in $(seq 1 60); do
    st=$(docker inspect -f '{{.State.Health.Status}}' "$C" 2>/dev/null)
    [ "$st" = "healthy" ] && break; printf '.'; sleep 10
  done; echo
  [ "$st" = "healthy" ] || { echo "[ERROR] Splunk did not become healthy. Run: docker logs $C | tail -30"; exit 1; }
  echo "== 4/4 Creating indexes and loading the logs"
  S="docker exec -u splunk $C /opt/splunk/bin/splunk"
  for idx in retail_web retail_checkout; do $S add index "$idx" -auth "admin:$PASS" >/dev/null 2>&1 || true; done
  for f in "$SETUP"/data/web-*.log; do h=$(basename "$f" .log); h=${h#web-}
    $S add oneshot "/lab-data/$(basename "$f")" -index retail_web -sourcetype retail_web -host "$h" -auth "admin:$PASS" >/dev/null; done
  for f in "$SETUP"/data/checkout-*.log; do h=$(basename "$f" .log); h=${h#checkout-}
    $S add oneshot "/lab-data/$(basename "$f")" -index retail_checkout -sourcetype retail_checkout -host "$h" -auth "admin:$PASS" >/dev/null; done
  echo ""
  echo "Incident TEL-D3-301 is ready."
  echo "  Open     : http://localhost:8000   (user admin / password: $PASS)"
  echo "  Wait     : about 1 minute, then search  index=retail_* earliest=-4h | stats count by index"
  echo "  Expected : retail_checkout 3000, retail_web 2400"
  echo "  Ticket   : Post-deployment error rate surges to 8.4 %. Follow starter/README_START_HERE.txt"
}

invoke_reset() {
  need docker
  ( cd "$SETUP" && docker compose down -v ) 2>/dev/null
  rm -rf "$SETUP/data"
  echo "Scenario removed. Your evidence file was not touched."
}

invoke_check() {
  echo "==================================================="
  echo " Validating Solution for TEL-D3-301"
  echo "==================================================="
  [ -f "$EVIDENCE" ] || { echo " [ERROR] Evidence file not found: $EVIDENCE"; echo " Total Score: 0/5 (0%)"; return 1; }
  grep -q "<<FILL_" "$EVIDENCE" && echo " [WARNING] Detected unfilled placeholder tokens (<<FILL_...>>) in evidence!"
  P=0; T=5; n=0
  while IFS='|' read -r pat label; do
    n=$((n+1))
    if grep -q -i -F -- "$pat" "$EVIDENCE"; then echo "  [PASS] Rule $n: $label"; P=$((P+1)); else echo "  [FAIL] Rule $n: $label (missing: $pat)"; fi
  done <<'RULES'
web-prod-04|Culprit host isolated
rex field=_raw|Regex extraction command used
ERR-[0-9]{4}|Error code pattern matched
timechart|Error codes charted over time
transaction session_id|Sessions grouped with transaction
RULES
  echo "---------------------------------------------------"
  echo " Test Summary: $P / $T checks passed ($((P*100/T))%)"
  echo "---------------------------------------------------"
  [ "$P" -eq "$T" ] && echo " [SUCCESS] All validation checks passed successfully!" || echo " [RETRY] Fix the missing items and run check again."
}

case "$ACTION" in
  start) invoke_start;; reset) invoke_reset;; check) invoke_check;;
  *) echo "Usage: $0 start|check|reset [evidence.md]";;
esac
