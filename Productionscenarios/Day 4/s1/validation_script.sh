#!/usr/bin/env bash
# TEL-D4-401 - Slow-Transaction Report for the Ops Review
# Usage: ./validation_script.sh start | check | reset [--yes]
ACTION="${1:-check}"
LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KIT="$LAB_DIR/starter/kit"; EVDIR="$LAB_DIR/starter/evidence"
PY="$(command -v python3 || command -v python)"
[ -n "$PY" ] || { echo "Python 3 is required (python3 --version)"; exit 1; }
wait_http() { echo -n "Waiting for $1 "; for i in $(seq 1 90); do [ "$(curl -s -o /dev/null -w '%{http_code}' "$1")" = 200 ] && { echo " ok"; return; }; echo -n .; sleep 2; done; echo " (not ready - continue anyway)"; }

invoke_start() {
    echo "==================================================="
    echo " Initializing Incident: TEL-D4-401"
    echo " Slow-Transaction Report for the Ops Review"
    echo "==================================================="
    echo "Observed Failure: Operations review requires a p95 transaction latency ranking for ShopNow-Production. Default APM overviews do not isolate top-5 slowest transactions."
    echo ""
    command -v docker >/dev/null || { echo "Docker is required (docker compose version)"; exit 1; }
    (cd "$KIT" && docker compose up -d) || exit 1
    wait_http http://localhost:9090/-/ready
    echo "Prometheus: http://localhost:9090  |  New Relic: your instructor's shared account (NRQL Query builder, app ShopNow-Production)"
    echo "Your Mission: follow starter/README_START_HERE.txt"
    echo "Fill the evidence template: starter/evidence/evidence_D4_1.md"
    echo "Then validate with: ./validation_script.sh check"
}

invoke_check() { "$PY" "$LAB_DIR/validate.py"; }

invoke_reset() {
    echo "==================================================="
    echo " Resetting Scenario TEL-D4-401..."
    echo "==================================================="
    if [ "${2:-}" != "--yes" ]; then echo "This deletes the containers, your Grafana/Prometheus changes and your evidence - YOUR WORK WILL BE LOST. Re-run: ./validation_script.sh reset --yes"; exit 1; fi
    (cd "$KIT" && docker compose down -v)
    rm -f "$KIT/control/fault"
    cp "$EVDIR/evidence_D4_1.template.md" "$EVDIR/evidence_D4_1.md"
    echo "Baseline state restored. Run ./validation_script.sh start"
}

case "$ACTION" in
    start) invoke_start ;;
    check) invoke_check ;;
    reset) invoke_reset "$@" ;;
    *) echo "Usage: ./validation_script.sh {start|check|reset [--yes]}" ;;
esac
