#!/usr/bin/env bash
set -euo pipefail

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$LAB_DIR"

echo "=== 1. Creating Docker bridge network obs-net ==="
docker network inspect obs-net >/dev/null 2>&1 || docker network create obs-net

echo "=== 2. Removing any stale lab containers ==="
docker rm -f easytravel-mock prometheus grafana 2>/dev/null || true

echo "=== 3. Starting easytravel-mock exporter on obs-net ==="
docker run -d --name easytravel-mock --network obs-net   -v "$LAB_DIR/mock_easytravel.py:/app/mock_easytravel.py:ro"   python:3.11-slim python /app/mock_easytravel.py

echo "=== 4. Starting Prometheus on obs-net (port 9090) ==="
docker run -d --name prometheus --network obs-net -p 9090:9090   -v "$LAB_DIR/prometheus.yml:/etc/prometheus/prometheus.yml:ro"   prom/prometheus:latest

echo "=== 5. Starting Grafana on obs-net (port 3000) ==="
docker run -d --name grafana --network obs-net -p 3000:3000   -e GF_SECURITY_ADMIN_USER=admin   -e GF_SECURITY_ADMIN_PASSWORD=admin   -v "$LAB_DIR/provisioning/datasources:/etc/grafana/provisioning/datasources:ro"   -v "$LAB_DIR/provisioning/dashboards:/etc/grafana/provisioning/dashboards:ro"   -v "$LAB_DIR/dashboards:/var/lib/grafana/dashboards:ro"   grafana/grafana:latest

echo "=== 6. Provisioning candidate folder u01 ==="
chmod +x "$LAB_DIR/create_grafana_seats.sh" "$LAB_DIR/faultctl.sh"
"$LAB_DIR/create_grafana_seats.sh" http://localhost:3000 admin:admin 1

echo "=== 7. Verification ==="
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo "Grafana URL : http://localhost:3000  (admin / admin)"
echo "Prometheus  : http://localhost:9090"
