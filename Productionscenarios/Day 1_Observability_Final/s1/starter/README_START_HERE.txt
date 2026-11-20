TEL-D1-101 — Checkout Is Slow but the Dashboard Looks Green

RUN FROM: ~/day1/s1 (the scenario folder, not starter/)

1. Start/reset the scenario:
   ./validation_script.sh start
   Windows PowerShell: .\validation_script.ps1 start
2. Wait for checkout-service, Prometheus and Grafana to report ready.
3. Open Grafana: http://localhost:3000 (lab default admin/admin).
4. Dashboards → RED Checkout Dashboard → Payment Duration panel → Edit.
5. Replace the mean query with:
   histogram_quantile(0.95, sum by (le) (rate(payment_duration_seconds_bucket[5m])))
6. Add a 5xx Error Rate (%) panel with:
   100 * sum(rate(http_requests_total{service="checkout-service",status=~"5.."}[5m])) / sum(rate(http_requests_total{service="checkout-service"}[5m]))
7. Apply and SAVE the dashboard. Panel unit for latency remains seconds (s).
8. Verify Prometheus target at http://localhost:9090/targets (shopnow-checkout must be UP).
9. Complete starter/evidence/evidence_D1_1.json with valid JSON.
10. Validate: ./validation_script.sh check
11. Reset before the next scenario: ./validation_script.sh reset

If Prometheus is not ready, run from ~/day1/s1:
   docker compose -p telemetry-d1-s1 -f lab/docker-compose.yml ps
   docker compose -p telemetry-d1-s1 -f lab/docker-compose.yml logs --tail=150 prometheus
   curl -fsS http://localhost:9090/-/ready

Prometheus mounts starter/conf as /etc/prometheus. Keep prometheus.yml and legacy_rules.yml together. The scrape target must use Docker service DNS checkout:8081, not localhost:8081.
