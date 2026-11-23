#!/usr/bin/env bash
# TEL-D4-402 - Error Panel Shows Zero During an Outage
# Usage: ./validation_script.sh start | check | reset [--yes]
ACTION="${1:-check}"
LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KIT="$LAB_DIR/starter/kit"; EVDIR="$LAB_DIR/starter/evidence"
PY="$(command -v python3 || command -v python)"
[ -n "$PY" ] || { echo "Python 3 is required (python3 --version)"; exit 1; }
wait_http() { echo -n "Waiting for $1 "; for i in $(seq 1 90); do [ "$(curl -s -o /dev/null -w '%{http_code}' "$1")" = 200 ] && { echo " ok"; return; }; echo -n .; sleep 2; done; echo " (not ready - continue anyway)"; }

invoke_start() {
    echo "==================================================="
    echo " Initializing Incident: TEL-D4-402"
    echo " Error Panel Shows Zero During an Outage"
    echo "==================================================="
    echo "Observed Failure: During an ongoing payment outage, the Grafana Error Rate panel displays 0 errors. SREs have zero visibility into failure rates."
    echo ""
    command -v docker >/dev/null || { echo "Docker is required (docker compose version)"; exit 1; }
    (cd "$KIT" && docker compose up -d) || exit 1
    wait_http http://localhost:3000/api/health; wait_http http://localhost:3100/ready
    mkdir -p "$KIT/control"; touch "$KIT/control/fault"
    "$PY" "$LAB_DIR/validate.py" import
    echo "OUTAGE STARTED $(date -u +%H:%M:%S) UTC: payment-service emits about 90 ERROR logs per minute ('Gateway timeout'). Wait 5 minutes for a full rate window."
    echo "Grafana: http://localhost:3000 (user admin, password = GRAFANA_PASSWORD in starter/kit/.env) -> Dashboards -> Payment Dashboard"
    echo "Your Mission: follow starter/README_START_HERE.txt"
    echo "Fill the evidence template: starter/evidence/evidence_D4_2.json"
    echo "Then validate with: ./validation_script.sh check"
}

invoke_check() { "$PY" "$LAB_DIR/validate.py"; }

invoke_reset() {
    echo "==================================================="
    echo " Resetting Scenario TEL-D4-402..."
    echo "==================================================="
    if [ "${2:-}" != "--yes" ]; then echo "This deletes the containers, your Grafana/Prometheus changes and your evidence - YOUR WORK WILL BE LOST. Re-run: ./validation_script.sh reset --yes"; exit 1; fi
    (cd "$KIT" && docker compose down -v)
    rm -f "$KIT/control/fault"
    cp "$EVDIR/evidence_D4_2.template.json" "$EVDIR/evidence_D4_2.json"
    echo "Baseline state restored. Run ./validation_script.sh start"
}

case "$ACTION" in
    start) invoke_start ;;
    check) invoke_check ;;
    reset) invoke_reset "$@" ;;
    *) echo "Usage: ./validation_script.sh {start|check|reset [--yes]}" ;;
esac
