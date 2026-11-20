TEL-D1-102 — Orders Fail for One Product: Follow the Trace

RUN FROM: ~/day1/s2 (the scenario folder, not starter/)

1. Start/reset the scenario:
   ./validation_script.sh start
   Windows PowerShell: .\validation_script.ps1 start
2. Wait until frontend, checkout, payment, inventory, Jaeger, Loki and Grafana are ready.
3. Wait 30–60 seconds for load-generator traffic if required.
4. Open Jaeger: http://localhost:16686 → Search.
5. Service: frontend. Operation: POST /api/checkout (if listed). Lookback: Last Hour. Click Find Traces.
6. Open a trace with a red error marker. Expand frontend → checkout-service → inventory-service.
7. Select inventory.reserveStock. Inspect error=true, error.type=StockReservationException, SKU PROD-7729, HTTP 409.
8. Copy the 32-character Trace ID from the browser URL after /trace/.
9. Open Grafana Explore: http://localhost:3000/explore. Select Loki.
10. Run this LogQL after replacing the placeholder with the SAME Trace ID:
    {app="inventory-service"} |= "PASTE_THE_32_CHARACTER_TRACE_ID_HERE"
11. Confirm the log contains StockReservationException and the cycle-count audit lock.
12. Complete starter/evidence/evidence_D1_2.md. Record the actual Trace ID, full Jaeger URL and exact LogQL query.
13. Validate: ./validation_script.sh check
14. Reset before the next scenario: ./validation_script.sh reset

RECOVERY — only if the S2 build or containers fail. Run one command at a time from ~/day1/s2:
   docker compose -p telemetry-d1-s2 -f lab/docker-compose.yml build --no-cache
   docker compose -p telemetry-d1-s2 -f lab/docker-compose.yml up -d --force-recreate
   docker compose -p telemetry-d1-s2 -f lab/docker-compose.yml ps

If any container is not Up:
   docker compose -p telemetry-d1-s2 -f lab/docker-compose.yml logs --tail=150

Do not use a hard-coded Trace ID. Runtime traces can differ. The validator requires the same 32-hex ID in the Jaeger URL and Loki query.
