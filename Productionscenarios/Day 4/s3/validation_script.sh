#!/usr/bin/env bash
# TEL-D4-403 - Latency Percentile and Service Variable Are Wrong
# Usage: ./validation_script.sh start | check | reset [--yes]
ACTION="${1:-check}"
LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KIT="$LAB_DIR/starter/kit"; EVDIR="$LAB_DIR/starter/evidence"
PY="$(command -v python3 || command -v python)"
[ -n "$PY" ] || { echo "Python 3 is required (python3 --version)"; exit 1; }
wait_http() { echo -n "Waiting for $1 "; for i in $(seq 1 90); do [ "$(curl -s -o /dev/null -w '%{http_code}' "$1")" = 200 ] && { echo " ok"; return; }; echo -n .; sleep 2; done; echo " (not ready - continue anyway)"; }

invoke_start() {
    echo "==================================================="
    echo " Initializing Incident: TEL-D4-403"
    echo " Latency Percentile and Service Variable Are Wrong"
    echo "==================================================="
    echo "Observed Failure: SRE dashboard latency percentiles show flat lines measuring cumulative stats since server reboot, and selecting a service in the variable dropdown causes panels to show 'No Data'."
    echo ""
    command -v docker >/dev/null || { echo "Docker is required (docker compose version)"; exit 1; }
    (cd "$KIT" && docker compose up -d) || exit 1
    wait_http http://localhost:3000/api/health; wait_http http://localhost:9090/-/ready
    "$PY" "$LAB_DIR/validate.py" import
    echo "Let it run 5-10 minutes so that Prometheus has data for rate()."
    echo "Grafana: http://localhost:3000 (user admin, password = GRAFANA_PASSWORD in starter/kit/.env) -> Dashboards -> ShopNow SRE Dashboard"
    echo "Prometheus: http://localhost:9090"
    echo "Your Mission: follow starter/README_START_HERE.txt"
    echo "Fill the evidence template: starter/evidence/evidence_D4_3.json"
    echo "Then validate with: ./validation_script.sh check"
}

invoke_check() { "$PY" "$LAB_DIR/validate.py"; }

invoke_reset() {
    echo "==================================================="
    echo " Resetting Scenario TEL-D4-403..."
    echo "==================================================="
    if [ "${2:-}" != "--yes" ]; then echo "This deletes the containers, your Grafana/Prometheus changes and your evidence - YOUR WORK WILL BE LOST. Re-run: ./validation_script.sh reset --yes"; exit 1; fi
    (cd "$KIT" && docker compose down -v)
    rm -f "$KIT/control/fault"
    cp "$EVDIR/evidence_D4_3.template.json" "$EVDIR/evidence_D4_3.json"
    echo "Baseline state restored. Run ./validation_script.sh start"
}

case "$ACTION" in
    start) invoke_start ;;
    check) invoke_check ;;
    reset) invoke_reset "$@" ;;
    *) echo "Usage: ./validation_script.sh {start|check|reset [--yes]}" ;;
esac
