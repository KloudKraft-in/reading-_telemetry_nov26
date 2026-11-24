#!/usr/bin/env bash
# TEL-D5-502 - Lambda Timeouts: Logs Insights Meets X-Ray
# Usage: ./validation_script.sh start | check | reset [--yes]
ACTION="${1:-check}"
LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STARTER="$LAB_DIR/starter"; EVDIR="$STARTER/evidence"
PY="$(command -v python3 || command -v python)"
[ -n "$PY" ] || { echo "Python 3 is required (python3 --version)"; exit 1; }
TEMPLATE_NOTE="evidence_D5_2.template.md"

restore_evidence() { cp "$EVDIR/$TEMPLATE_NOTE" "$EVDIR/evidence_D5_2.md"; }
[ -f "$EVDIR/$TEMPLATE_NOTE" ] || cp "$EVDIR/evidence_D5_2.md" "$EVDIR/$TEMPLATE_NOTE"

invoke_start() {
    echo "==================================================="
    echo " Initializing Incident: TEL-D5-502"
    echo " Lambda Timeouts: Logs Insights Meets X-Ray"
    echo "==================================================="
    echo "Observed Failure: Order invoice generation Lambdas terminate abruptly with 'Task timed out after 30.00 seconds'. CloudWatch logs show timeouts but do not reveal the stalled downstream call."
    echo ""
    echo "Step 1: AWS console -> CloudFormation -> create the stack from starter/aws/invoice-stack.yaml (see starter/README_START_HERE.txt)"
    echo "Step 2: CloudWatch Logs Insights and X-Ray traces in the console - no CLI needed"
    echo "Your Mission: follow starter/README_START_HERE.txt"
    echo "Fill the evidence template: starter/evidence/evidence_D5_2.md"
    echo "Then validate with: ./validation_script.sh check"
}

invoke_check() { "$PY" "$LAB_DIR/validate.py"; }

invoke_reset() {
    echo "==================================================="
    echo " Resetting Scenario TEL-D5-502..."
    echo "==================================================="
    if [ "${2:-}" != "--yes" ]; then echo "This restores the evidence template - YOUR WORK WILL BE LOST. Re-run: ./validation_script.sh reset --yes"; exit 1; fi
    restore_evidence
    echo "Baseline state restored. Run ./validation_script.sh start"
}

case "$ACTION" in
    start) invoke_start ;;
    check) invoke_check ;;
    reset) invoke_reset "$@" ;;
    *) echo "Usage: ./validation_script.sh {start|check|reset [--yes]}" ;;
esac
