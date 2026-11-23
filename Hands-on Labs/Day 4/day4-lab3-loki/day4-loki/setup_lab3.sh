#!/usr/bin/env bash
set -euo pipefail

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$LAB_DIR"

echo "=== 1. Ensuring obs-net Docker network exists ==="
docker network inspect obs-net >/dev/null 2>&1 || docker network create obs-net

echo "=== 2. Starting Loki via docker compose ==="
docker compose -f "$LAB_DIR/loki/docker-compose.yml" up -d

echo "=== 3. Wiring Loki datasource into Grafana ==="
if [ -d "$HOME/day4-grafana/provisioning/datasources" ]; then
  cp "$LAB_DIR/provisioning/datasources/loki.yml" "$HOME/day4-grafana/provisioning/datasources/loki.yml"
  docker restart grafana
elif docker ps --format '{{.Names}}' | grep -qx 'grafana'; then
  docker cp "$LAB_DIR/provisioning/datasources/loki.yml" grafana:/etc/grafana/provisioning/datasources/loki.yml
  docker restart grafana
else
  echo "[WARN] Grafana container not found running. Start Lab 2 Grafana first, then re-run this script."
fi

echo "=== 4. Initializing fault control flag (OFF) ==="
chmod +x "$LAB_DIR/faultctl.sh" "$LAB_DIR/loki/et_json_log_feed.py"
"$LAB_DIR/faultctl.sh" off

echo "=== 5. Starting easyTravel JSON log shipper ==="
pkill -f "et_json_log_feed.py" 2>/dev/null || true
nohup python3 "$LAB_DIR/loki/et_json_log_feed.py"   --loki http://localhost:3100   --flag "$HOME/obs-lab/control/fault.flag" >/tmp/et_json_log_feed.log 2>&1 &

echo "=== 6. Waiting for Loki readiness and stream ingestion ==="
for i in $(seq 1 20); do
  if curl -s http://localhost:3100/ready | grep -q "ready"; then
    break
  fi
  sleep 1
done
sleep 3

echo "Loki ready check:"
curl -s http://localhost:3100/ready && echo ""
echo "Loki service_name labels:"
curl -s http://localhost:3100/loki/api/v1/label/service_name/values && echo ""
