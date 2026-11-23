#!/usr/bin/env bash
set -euo pipefail

GRAFANA_URL="${1:-http://localhost:3000}"
AUTH="${2:-admin:admin}"
SEAT_COUNT="${3:-1}"

echo "Waiting for Grafana API at $GRAFANA_URL..."
for i in $(seq 1 30); do
  if curl -s -o /dev/null "$GRAFANA_URL/api/health"; then
    break
  fi
  sleep 1
done

for i in $(seq 1 "$SEAT_COUNT"); do
  FOLDER=$(printf "u%02d" "$i")
  RESP=$(curl -s -u "$AUTH" -H "Content-Type: application/json"     -X POST "$GRAFANA_URL/api/folders"     -d "{"uid":"$FOLDER","title":"$FOLDER"}")
  echo "Provisioned folder $FOLDER -> $RESP"
done
