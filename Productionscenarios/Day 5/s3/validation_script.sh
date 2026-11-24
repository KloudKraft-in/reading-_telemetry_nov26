#!/usr/bin/env bash
# TEL-D5-503 - Pager Fatigue: Tune the Alarms and Rebuild the Dashboard
# Usage: ./validation_script.sh start | check | reset [--yes]
ACTION="${1:-check}"
LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STARTER="$LAB_DIR/starter"; EVDIR="$STARTER/evidence"
PY="$(command -v python3 || command -v python)"
[ -n "$PY" ] || { echo "Python 3 is required (python3 --version)"; exit 1; }
TEMPLATE_NOTE="evidence_D5_3.template.md"

restore_evidence() { cp "$EVDIR/$TEMPLATE_NOTE" "$EVDIR/evidence_D5_3.md"; }
[ -f "$EVDIR/$TEMPLATE_NOTE" ] || cp "$EVDIR/evidence_D5_3.md" "$EVDIR/$TEMPLATE_NOTE"

invoke_start() {
    echo "==================================================="
    echo " Initializing Incident: TEL-D5-503"
    echo " Pager Fatigue: Tune the Alarms and Rebuild the Dashboard"
    echo "==================================================="
    echo "Observed Failure: On-call engineers receive 80+ alarm notifications per week caused by one-minute CPU spikes and any single failed request. Critical incidents get ignored and the only dashboard is a flat page of 16 widgets."
    echo ""
    echo "Step 1: AWS console -> CloudFormation -> create the stack pager-s3-<seat> from starter/aws/pager-stack.yaml (see starter/README_START_HERE.txt)"
    echo "Step 2: CloudWatch alarms and dashboards in the console - no CLI, no Docker"
    echo "Your Mission: follow starter/README_START_HERE.txt"
    echo "Fill the evidence template: starter/evidence/evidence_D5_3.md"
    echo "Then validate with: ./validation_script.sh check"
}

invoke_check() { "$PY" "$LAB_DIR/validate.py"; }

invoke_reset() {
    echo "==================================================="
    echo " Resetting Scenario TEL-D5-503..."
    echo "==================================================="
    if [ "${2:-}" != "--yes" ]; then echo "This restores the evidence template - YOUR WORK WILL BE LOST. Re-run: ./validation_script.sh reset --yes"; exit 1; fi
    restore_evidence
    rm -f "$EVDIR/tier1.json" "$EVDIR/tier2.json"
    echo "Baseline state restored. Run ./validation_script.sh start"
}

case "$ACTION" in
    start) invoke_start ;;
    check) invoke_check ;;
    reset) invoke_reset "$@" ;;
    *) echo "Usage: ./validation_script.sh {start|check|reset [--yes]}" ;;
esac
