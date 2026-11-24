#!/usr/bin/env bash
# Day 5 Lab 5 — start the stack and wait until everything is healthy. Run from the kit folder: ./scripts/setup.sh
set -euo pipefail
cd "$(dirname "$0")/.."
command -v docker >/dev/null || { echo "Docker is not installed"; exit 1; }
docker compose version >/dev/null || { echo "Docker Compose v2 is required"; exit 1; }
[ -f control/fault ] || echo none > control/fault
docker compose up -d
echo -n "Waiting for Prometheus and Alertmanager "
for i in $(seq 1 60); do
  p=$(curl -s -o /dev/null -w '%{http_code}' localhost:9090/-/ready || true); a=$(curl -s -o /dev/null -w '%{http_code}' localhost:9093/-/ready || true)
  [ "$p" = 200 ] && [ "$a" = 200 ] && break; echo -n .; sleep 2
done; echo
sleep 20
./scripts/verify.sh
