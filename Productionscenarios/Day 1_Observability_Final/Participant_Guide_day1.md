# Day 1 — Reading Telemetry & Observability
## Participant Lab Guide | Observability Foundations & Incident Triage

**Scenarios:** TEL-D1-101 (S1), TEL-D1-102 (S2), TEL-D1-103 (S3)  
**Environment:** Self-hosted Ubuntu/Linux VM with Docker Compose; Windows PowerShell is supported for controller scripts.

---

## 1. What you will do

Investigate three simulated ShopNow production incidents using live synthetic telemetry. Work only in the `starter/` folders. Do not edit `lab/baseline/`; those files are the clean reset copies.

| Scenario | Ticket | Tools | Incident |
|---|---|---|---|
| S1 | TEL-D1-101 | Prometheus, Grafana | Mean latency hides the slow checkout tail; the 5xx panel is missing. |
| S2 | TEL-D1-102 | Jaeger, Loki, Grafana Explore | A promotional SKU fails because its warehouse bin is locked during a cycle-count audit. |
| S3 | TEL-D1-103 | Prometheus, Alertmanager, Grafana | Six alerts fire; the causal issue is PostgreSQL primary disk queue saturation. |

## 2. Prerequisites

Recommended host: Ubuntu 22.04/24.04 x86_64, 4 vCPU, 8 GB RAM and 25 GB free disk. Required: Docker Engine, Docker Compose v2, Python 3 and `curl`. Internet access is required on first run for pinned image pulls and the application image build. Docker must already be installed; this lab does not install Docker.

Run before starting:

```bash
docker --version
docker compose version
docker info
python3 --version
curl --version
```

`docker info` must complete successfully. If it reports a permission error, resolve Docker daemon/group access with the VM administrator before proceeding.

Windows: use Docker Desktop with Linux containers and PowerShell. Run `docker --version`, `docker compose version`, `docker info`, and `python --version`. Use the `.ps1` controller scripts.

## 3. Extract and prepare permissions

1. Extract the ZIP into your home directory (`~`), not into an existing `~/day1` folder. The archive already contains the top-level `day1/` directory, so this creates `~/day1/`.
2. Open a terminal in the extracted `day1` folder (the folder containing `s1`, `s2`, `s3`, and `shared`).
3. On Linux, run this once after extraction:

```bash
cd ~/day1
chmod +x s1/validation_script.sh s2/validation_script.sh s3/validation_script.sh shared/labctl.py
```

4. Verify permissions:

```bash
ls -l s1/validation_script.sh s2/validation_script.sh s3/validation_script.sh shared/labctl.py
```

The scripts should show executable (`x`) permissions. Repeat chmod if the ZIP is extracted again. Windows does not require chmod.

## 4. Standard execution sequence

Run **one scenario at a time**. S1/S2/S3 reuse host ports and some container names. The updated `start` command stops other Day 1 scenario projects, restores the selected scenario's clean starter files, validates its Compose model, builds/starts the stack, and waits for readiness.

For each scenario:

1. Enter its folder (`~/day1/s1`, `~/day1/s2`, or `~/day1/s3`).
2. Start: `./validation_script.sh start` (PowerShell: `.\validation_script.ps1 start`).
3. Wait until all configured readiness endpoints report ready.
4. Follow the scenario instructions below.
5. Complete the evidence file under `starter/evidence/`. Use `EVIDENCE_PASS_EXAMPLES.md` in the package root for copy-ready examples and exact validator requirements.
6. Validate: `./validation_script.sh check` (PowerShell: `.\validation_script.ps1 check`).
7. Reset before moving on: `./validation_script.sh reset` (PowerShell equivalent).

`start` also resets the selected scenario. `reset` stops its stack, removes its named volumes, and restores starter files from `lab/baseline/`. If a starter file was changed, its previous copy is saved beside it with a `.bak-YYYYMMDD-HHMMSS` suffix. Preserve any evidence backup you need before resetting.

## 5. S1 — TEL-D1-101: Checkout Is Slow but the Dashboard Looks Green

**Time:** 75 minutes | **Category:** Dashboard troubleshooting  
**Run from:** `~/day1/s1` | **Evidence:** `s1/starter/evidence/evidence_D1_1.json`

### 5.1 Start and open tools

```bash
cd ~/day1/s1
./validation_script.sh start
```

Open Grafana `http://localhost:3000` (lab default `admin` / `admin`), Prometheus `http://localhost:9090`, targets `http://localhost:9090/targets`, and checkout metrics `http://localhost:8081/metrics`.

### 5.2 Fix the RED dashboard

1. Grafana → **Dashboards** → **RED Checkout Dashboard**.
2. Find **Payment Duration** → panel title menu (three dots) → **Edit**.
3. Replace the mean query with the p95 histogram query below. Keep the panel unit as seconds (`s`); do not multiply by 1000.

```promql
histogram_quantile(0.95, sum by (le) (rate(payment_duration_seconds_bucket[5m])))
```

4. Click **Apply**. Allow 2–3 minutes for samples and the rate window to populate; p95 should expose the slow cohort (about 4.6 seconds; exact values vary).
5. Add a panel for **5xx Error Rate (%)** and use:

```promql
100 * sum(rate(http_requests_total{service="checkout-service",status=~"5.."}[5m])) / sum(rate(http_requests_total{service="checkout-service"}[5m]))
```

6. Set unit to **Percent (0–100)**, click **Apply**, then **Save dashboard** and confirm.

### 5.3 Verify Prometheus

Open `/targets`; `shopnow-checkout` must be **UP**. In Prometheus Graph, test:

```promql
up{job="shopnow-checkout"}
rate(http_requests_total{service="checkout-service"}[5m])
histogram_quantile(0.95, sum by (le) (rate(payment_duration_seconds_bucket[5m])))
```

If Prometheus is not ready, run from `~/day1/s1`:

```bash
docker compose -p telemetry-d1-s1 -f lab/docker-compose.yml ps
docker compose -p telemetry-d1-s1 -f lab/docker-compose.yml logs --tail=100 prometheus
curl -fsS http://localhost:9090/-/ready
```

S1 mounts `s1/starter/conf/` into Prometheus. Keep `prometheus.yml` and `legacy_rules.yml` together. The target must be Docker service DNS `checkout:8081`, not `localhost:8081`.

### 5.4 Evidence and validation

Complete `s1/starter/evidence/evidence_D1_1.json` with valid JSON and record the observed defect, root cause, both queries, platform verification and remediation. Use the S1 example in `EVIDENCE_PASS_EXAMPLES.md` to ensure the five evidence checks are satisfied. Run:

```bash
./validation_script.sh check
```

The validator checks the evidence and reads the saved Grafana dashboard API. A query typed but not saved will fail the live dashboard check.

## 6. S2 — TEL-D1-102: Orders Fail for One Product: Follow the Trace

**Time:** 75 minutes | **Category:** Distributed tracing  
**Run from:** `~/day1/s2` | **Evidence:** `s2/starter/evidence/evidence_D1_2.md`

### 6.1 Start and verify services

```bash
cd ~/day1/s2
./validation_script.sh start
```

Wait for frontend, checkout, payment, inventory, Jaeger, Loki and Grafana. Open Jaeger `http://localhost:16686`, Grafana `http://localhost:3000`, and Loki readiness `http://localhost:3100/ready`. Health endpoints: `8080/health`, `8081/health`, `8082/health`, `8083/health` on localhost. The load generator sends a seeded request and then mixed traffic; wait 30–60 seconds if necessary.

### 6.2 Find the failed trace in Jaeger

1. Open Jaeger → **Search**.
2. **Service:** `frontend`. **Operation:** `POST /api/checkout` if available. **Lookback:** `Last Hour`.
3. Click **Find Traces**.
4. Open a trace with a red error marker; the root operation should be `frontend: POST /api/checkout`.
5. In the trace waterfall, expand `frontend` → `checkout-service` → `inventory-service` until `inventory.reserveStock` is visible.
6. Select `inventory.reserveStock`. Inspect Tags: `error=true`, `error.type=StockReservationException`, `product.sku=PROD-7729`, and HTTP `409`.
7. Inspect the parent checkout span: the customer-facing request returns HTTP `500`. Inventory's `409 Conflict` is the dependency failure; checkout masks it as a generic `500`.
8. Copy the Trace ID from the browser URL. The URL format is:

```text
http://localhost:16686/trace/<32-character-trace-id>
```

Copy the full 32-character hexadecimal value after `/trace/`. Runtime traces can differ; do not assume one fixed ID.

### 6.3 Correlate the same ID in Loki

1. Open Grafana Explore: `http://localhost:3000/explore`.
2. Select the **Loki** data source.
3. Enter the query below, replacing the placeholder with the exact Trace ID copied from Jaeger, then click **Run query**.

```logql
{app="inventory-service"} |= "PASTE_THE_32_CHARACTER_TRACE_ID_HERE"
```

4. Confirm the result contains `StockReservationException`, `PROD-7729`, and the cycle-count audit lock. The `trace_id` in the log line must match the Jaeger URL.

Optional terminal query:

```bash
TRACE_ID='PASTE_THE_32_CHARACTER_TRACE_ID_HERE'
curl -G -s 'http://localhost:3100/loki/api/v1/query_range' \
  --data-urlencode "query={app=\"inventory-service\"} |= \"${TRACE_ID}\"" \
  --data-urlencode 'limit=20' | python3 -m json.tool
```

### 6.4 Evidence and validation

Complete `s2/starter/evidence/evidence_D1_2.md` with the actual Trace ID, full Jaeger URL, root operation, failing span, SKU, inventory 409 vs checkout 500, exact LogQL query using the same ID, exception, root cause and recommended action. Follow the S2 worked format in `EVIDENCE_PASS_EXAMPLES.md`; replace the example token everywhere with your own runtime Trace ID. Run:

```bash
./validation_script.sh check
```

The updated validator accepts any valid 32-character hexadecimal runtime Trace ID, but requires that same ID in the Jaeger URL and Loki query.

### 6.5 S2 recovery note — only if build or containers fail

Do not rebuild if the normal `start` command succeeds. If the image build fails, a container repeatedly exits, or the stack is inconsistent, run these commands **one by one from `~/day1/s2`**:

**Step 1 — Rebuild without cache**

```bash
docker compose -p telemetry-d1-s2 -f lab/docker-compose.yml build --no-cache
```

Wait until the build completes.

**Step 2 — Recreate services**

```bash
docker compose -p telemetry-d1-s2 -f lab/docker-compose.yml up -d --force-recreate
```

**Step 3 — Check containers**

```bash
docker compose -p telemetry-d1-s2 -f lab/docker-compose.yml ps
```

All containers should show `Up`. If not, inspect:

```bash
docker compose -p telemetry-d1-s2 -f lab/docker-compose.yml logs --tail=150
```

Do not continue until required services and health endpoints are ready.

## 7. S3 — TEL-D1-103: Six Alerts at Shift Start, One Real Problem

**Time:** 60 minutes | **Category:** Alert triage  
**Run from:** `~/day1/s3` | **Evidence:** `s3/starter/evidence/evidence_D1_3.json`

### 7.1 Start and open tools

```bash
cd ~/day1/s3
./validation_script.sh start
```

Open Alertmanager `http://localhost:9093`, Prometheus alerts `http://localhost:9090/alerts`, Prometheus graph `http://localhost:9090/graph`, Grafana `http://localhost:3000`, and simulated DB activity `http://localhost:8083/pg_stat_activity`. Allow about 60 seconds for alert `for: 30s` windows.

### 7.2 Investigate the alert storm

1. Alertmanager → **Alerts**. Review `CheckoutSlow`, `PaymentTimeout`, `ProfileQueryDegraded`, `OrderHistory504`, `DiskIOWaitHigh`, and `DatabaseQueueSaturation`.
2. Prometheus → **Alerts**. Inspect each rule's expression and state.
3. Grafana → **Dashboards** → **USE Dashboard - PostgreSQL Primary**.
4. Compare utilization, saturation and errors. Disk queue is approximately 38 (normal below 2 in this simulation) and I/O await approximately 280 ms; CPU and memory are comparatively normal.
5. Verify in Prometheus Graph:

```promql
db_disk_queue_length{instance_role="primary"}
db_disk_io_await_milliseconds{instance_role="primary"}
db_cpu_utilization_percent{instance_role="primary"}
db_memory_utilization_percent{instance_role="primary"}
```

6. Open `/pg_stat_activity`. Identify PID `9182`, user `analytics_batch`, application `nightly-report-runner`, active state, `IO / DataFileRead`, and a long 90-day aggregation over orders/order_items with no index on `created_at`.
7. Explain the chain: the unindexed reporting query drives primary disk I/O saturation; application latency and timeout alerts are downstream symptoms.

### 7.3 Evidence and safe remediation

This endpoint is a simulator, not a live PostgreSQL database. Do not run a destructive `kill` command. Recommend controlled cancellation of the rogue batch query, index/query review, moving heavy reporting away from peak traffic, and routing reporting to the healthy read replica after checking replication lag. Complete `s3/starter/evidence/evidence_D1_3.json` using the S3 example in `EVIDENCE_PASS_EXAMPLES.md`, then run:

```bash
./validation_script.sh check
```

## 8. Reset, backups and scenario transition

After each scenario, run from its scenario folder:

```bash
./validation_script.sh reset
```

The controller stops the scenario, removes its named volumes and restores clean starter files from `lab/baseline/`. Modified starter files are backed up beside the participant file with a `.bak-<timestamp>` suffix. Preserve backups before resetting if you need them. Then enter the next scenario folder and run `start`.

## 9. Troubleshooting

### Port conflict

```bash
ss -ltnp | grep -E ':(3000|3100|8080|8081|8082|8083|9090|9093|16686)\b' || true
docker ps --format 'table {{.Names}}\t{{.Ports}}'
```

Stop the previous Day 1 scenario using its reset command. Do not kill unknown processes.

### Docker daemon or permissions

```bash
docker info
sudo systemctl status docker --no-pager
```

Resolve daemon/permission access before proceeding. The controller does not install Docker.

### Container exits

From the scenario folder:

```bash
docker compose -p telemetry-d1-s2 -f lab/docker-compose.yml ps -a
docker compose -p telemetry-d1-s2 -f lab/docker-compose.yml logs --tail=150
```

Replace the project with `telemetry-d1-s1` or `telemetry-d1-s3` for other scenarios.

### Prometheus target DOWN

Check `http://localhost:9090/targets`, then inspect Prometheus logs. S1 target must be `checkout:8081`; S3 target must be `dbsim:8083`. These are Docker service names, not host localhost addresses.

### Jaeger has no traces

```bash
docker compose -p telemetry-d1-s2 -f lab/docker-compose.yml ps
docker compose -p telemetry-d1-s2 -f lab/docker-compose.yml logs --tail=80 loadgen
```

Confirm services are running, select Service `frontend`, Lookback `Last Hour`, and wait 30–60 seconds.

### Loki returns no rows

Check `http://localhost:3100/ready`, choose Loki in Grafana Explore, use `{app="inventory-service"}`, and paste the exact Trace ID from the Jaeger URL.

## 10. Completion checklist

- [ ] Docker and Docker Compose are working.
- [ ] Linux execute permissions were set after extraction.
- [ ] S1 p95 and 5xx panels are saved; validation passes.
- [ ] S2 same runtime Trace ID is recorded in Jaeger URL and Loki query; RCA is complete; validation passes.
- [ ] S3 causal alert and PID 9182 are identified; safe mitigation is documented; validation passes.
- [ ] Each scenario was reset before moving to the next.
- [ ] Evidence files contain no placeholders.


## Appendix A — Evidence files and validator pass examples

Use the package-root file `EVIDENCE_PASS_EXAMPLES.md` for complete copy-ready S1 and S3 JSON evidence, the S2 trace/log correlation format, required keywords, exact file paths, and expected validator scores. For S2, always capture the Trace ID from your own Jaeger browser URL; never reuse an instructor example ID.
