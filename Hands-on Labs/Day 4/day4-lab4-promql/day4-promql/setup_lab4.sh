#!/usr/bin/env bash
set -euo pipefail

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$LAB_DIR"

echo "=== 1. Ensuring obs-net Docker bridge network exists ==="
docker network inspect obs-net >/dev/null 2>&1 || docker network create obs-net

echo "=== 2. Removing stale Lab 4 containers ==="
docker rm -f easytravel-mock node-exporter prometheus 2>/dev/null || true

echo "=== 3. Starting easytravel-mock exporter on obs-net (port 8000) ==="
chmod +x "$LAB_DIR/mock_easytravel.py" "$LAB_DIR/faultctl.sh"
docker run -d --name easytravel-mock --network obs-net \
  -v "$LAB_DIR/mock_easytravel.py:/app/mock_easytravel.py:ro" \
  python:3.11-slim python /app/mock_easytravel.py

echo "=== 4. Starting node-exporter on obs-net (port 9100) ==="
docker run -d --name node-exporter --network obs-net \
  prom/node-exporter:latest

echo "=== 5. Starting read-only Prometheus on obs-net (port 9090, 5s scrape) ==="
docker run -d --name prometheus --network obs-net -p 9090:9090 \
  -v "$LAB_DIR/prometheus.yml:/etc/prometheus/prometheus.yml:ro" \
  prom/prometheus:latest \
  --config.file=/etc/prometheus/prometheus.yml \
  --storage.tsdb.path=/prometheus

echo "=== 6. Initializing fault state to OFF ==="
"$LAB_DIR/faultctl.sh" off

echo "=== 7. Waiting for Prometheus targets (easytravel, node, prometheus) ==="
for i in $(seq 1 20); do
  if curl -s http://localhost:9090/-/ready | grep -qi "ready"; then
    break
  fi
  sleep 1
done
sleep 6

echo "Active containers:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""
echo "Prometheus targets health:"
curl -s http://localhost:9090/api/v1/targets | python3 -c '
import sys, json
for t in json.load(sys.stdin)["data"]["activeTargets"]:
    job = t["labels"].get("job", "")
    health = t["health"]
    interval = t["scrapeInterval"]
    print(f"  job={job:12s} health={health:6s} scrapeInterval={interval}")
'
echo ""
echo "Prometheus UI : http://localhost:9090 (or http://<ec2-public-ip>:9090)"
