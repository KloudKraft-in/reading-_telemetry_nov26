#!/usr/bin/env bash
set -euo pipefail
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FLAG_FILE="$BASE_DIR/fault.flag"

case "${1:-status}" in
  on)
    echo "on" > "$FLAG_FILE"
    echo "[Cue C1] CreditCardCheckError500 is now ON ($(date +%T))."
    ;;
  off)
    echo "off" > "$FLAG_FILE"
    echo "[Cue C2] CreditCardCheckError500 is now OFF ($(date +%T))."
    ;;
  status)
    STATE="off"
    [ -f "$FLAG_FILE" ] && STATE="$(cat "$FLAG_FILE")"
    echo "Current CreditCardCheckError500 state: $STATE"
    ;;
  *)
    echo "Usage: $0 {on|off|status}"
    exit 1
    ;;
esac
