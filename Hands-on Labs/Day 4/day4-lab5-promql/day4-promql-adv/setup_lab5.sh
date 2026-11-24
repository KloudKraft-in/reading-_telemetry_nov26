#!/usr/bin/env bash
set -euo pipefail
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== 1. Ensuring obs-net Docker network exists ==="
docker network inspect obs-net >/dev/null 2>&1 || docker network create obs-net

echo "=== 2. Removing stale Prometheus lab containers ==="
docker rm -f easytravel-mock node-exporter prometheus >/dev/null 2>&1 || true

echo "=== 3. Initializing fault state to OFF ==="
"$BASE_DIR/faultctl.sh" off

echo "=== 4. Starting easytravel-mock (counters + duration histograms) ==="
docker run -d --name easytravel-mock --network obs-net \
  -v "$BASE_DIR/mock_easytravel.py:/app/mock_easytravel.py:ro" \
  -v "$BASE_DIR/fault.flag:/app/fault.flag:ro" \
  python:3.11-slim python3 /app/mock_easytravel.py

echo "=== 5. Starting node-exporter with textfile collector (easytravel_service_info) ==="
docker run -d --name node-exporter --network obs-net \
  -v "$BASE_DIR/textfile:/textfile:ro" \
  prom/node-exporter:latest \
  --collector.textfile.directory=/textfile

echo "=== 6. Starting read-only Prometheus with recording rules ==="
docker run -d --name prometheus --network obs-net -p 9090:9090 \
  -v "$BASE_DIR/prometheus.yml:/etc/prometheus/prometheus.yml:ro" \
  -v "$BASE_DIR/rules:/etc/prometheus/rules:ro" \
  prom/prometheus:latest \
  --config.file=/etc/prometheus/prometheus.yml \
  --storage.tsdb.path=/prometheus

echo "=== 7. Waiting 7s for initial scrape and rule evaluation ==="
sleep 7
curl -s http://localhost:9090/api/v1/targets | python3 -c '
import sys, json
for t in json.load(sys.stdin)["data"]["activeTargets"]:
    job, health, interval = t["labels"].get("job", ""), t["health"], t["scrapeInterval"]
    print(f"  job={job:12s} health={health:6s} scrapeInterval={interval}")
'
curl -s http://localhost:9090/api/v1/rules | python3 -c '
import sys, json
for g in json.load(sys.stdin)["data"]["groups"]:
    print(f"  rule_group={g[\"name\"]} rules={len(g[\"rules\"])}")
'
