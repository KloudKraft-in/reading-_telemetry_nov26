#!/usr/bin/env bash
set -euo pipefail

CMD="${1:-status}"
FLAG_DIR="$HOME/obs-lab/control"
FLAG_FILE="$FLAG_DIR/fault.flag"
mkdir -p "$FLAG_DIR"

case "$CMD" in
  on)
    echo "on" > "$FLAG_FILE"
    if docker ps --format '{{.Names}}' | grep -qx 'easytravel-mock'; then
      docker exec easytravel-mock sh -c "echo on > /tmp/creditcard_fault_on"
    fi
    echo "[Cue C1] CreditCardCheckError500 is now ON (metrics + Loki logs)."
    ;;
  off)
    echo "off" > "$FLAG_FILE"
    if docker ps --format '{{.Names}}' | grep -qx 'easytravel-mock'; then
      docker exec easytravel-mock sh -c "echo off > /tmp/creditcard_fault_on"
    fi
    echo "[Cue C2] CreditCardCheckError500 is now OFF (metrics + Loki logs)."
    ;;
  status)
    STATE=$([ -f "$FLAG_FILE" ] && cat "$FLAG_FILE" || echo "off")
    echo "Current CreditCardCheckError500 state: $STATE"
    ;;
  *)
    echo "Usage: $0 {on|off|status}"
    exit 1
    ;;
esac
