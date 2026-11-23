#!/usr/bin/env bash
set -euo pipefail

CMD="${1:-status}"
CONTAINER="easytravel-mock"
FLAG_PATH="/tmp/creditcard_fault_on"

case "$CMD" in
  on)
    docker exec "$CONTAINER" sh -c "echo on > $FLAG_PATH"
    echo "[Cue C1] CreditCardCheckError500 is now ON inside $CONTAINER."
    ;;
  off)
    docker exec "$CONTAINER" sh -c "echo off > $FLAG_PATH"
    echo "[Cue C2] CreditCardCheckError500 is now OFF inside $CONTAINER."
    ;;
  auto)
    docker exec "$CONTAINER" rm -f "$FLAG_PATH"
    echo "CreditCardCheckError500 reverted to automatic 3-minute cycle."
    ;;
  status)
    STATE=$(docker exec "$CONTAINER" sh -c "[ -f $FLAG_PATH ] && cat $FLAG_PATH || echo auto")
    echo "Current CreditCardCheckError500 mode: $STATE"
    ;;
  *)
    echo "Usage: $0 {on|off|auto|status}"
    exit 1
    ;;
esac
