#!/usr/bin/env bash
# traffic.sh — optional light traffic against the easyTravel Customer Frontend so logs, spans and metrics keep flowing.
# easyTravel normally ships its own load generator; use this only if traffic is thin. Default port 8079 — adjust to your install.
BASE="${EASYTRAVEL_URL:-http://localhost:8079}"; N="${1:-600}"; DELAY="${DELAY:-1}"
for i in $(seq 1 "$N"); do
  curl -s -o /dev/null -w "%{http_code} " "$BASE/" ; curl -s -o /dev/null "$BASE/orange.jsf" ; sleep "$DELAY"
done; echo
