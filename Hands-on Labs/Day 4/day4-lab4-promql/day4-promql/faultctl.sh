#!/usr/bin/env bash
set -euo pipefail

CMD="${1:-status}"
CONTAINER="easytravel-mock"
FLAG_PATH="/tmp/creditcard_fault_on"
HOST_FLAG_DIR="$HOME/obs-lab/control"
HOST_FLAG_FILE="$HOST_FLAG_DIR/fault.flag"
mkdir -p "$HOST_FLAG_DIR"

case "$CMD" in
  on)
    echo "on" > "$HOST_FLAG_FILE"
    if docker ps --format '{{.Names}}' | grep -qx "$CONTAINER"; then
      docker exec "$CONTAINER" sh -c "echo on > $FLAG_PATH"
    fi
    echo "[Cue C1] CreditCardCheckError500 is now ON ($(date +%T))."
    ;;
  off)
    echo "off" > "$HOST_FLAG_FILE"
    if docker ps --format '{{.Names}}' | grep -qx "$CONTAINER"; then
      docker exec "$CONTAINER" sh -c "echo off > $FLAG_PATH"
    fi
    echo "[Cue C2] CreditCardCheckError500 is now OFF ($(date +%T))."
    ;;
  reset)
    docker restart "$CONTAINER" >/dev/null
    echo "[Cue R1] Restarted $CONTAINER — counters reset to 0 ($(date +%T))."
    ;;
  status)
    if docker ps --format '{{.Names}}' | grep -qx "$CONTAINER"; then
      STATE=$(docker exec "$CONTAINER" sh -c "[ -f $FLAG_PATH ] && cat $FLAG_PATH || echo off")
    else
      STATE=$([ -f "$HOST_FLAG_FILE" ] && cat "$HOST_FLAG_FILE" || echo "off")
    fi
    echo "Current CreditCardCheckError500 state: $STATE"
    ;;
  *)
    echo "Usage: $0 {on|off|reset|status}"
    exit 1
    ;;
esac
