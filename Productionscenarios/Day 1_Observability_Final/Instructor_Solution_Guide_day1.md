# Day 1 — Reading Telemetry & Observability
## Instructor Solution & Operations Guide
### Observability Foundations, Incident Investigation and Recovery

> **CONFIDENTIAL — INSTRUCTOR USE ONLY.** This guide contains expected findings, reference answers, reset behavior, and recovery procedures. Distribute the Participant Guide and starter artifacts only when the exercise begins. Keep `instructor/reference_answers/` private.

---

## 1. Instructor delivery model

Day 1 is a three-scenario, self-hosted observability simulation. Participants work with live synthetic telemetry in isolated Docker Compose stacks. The application services are deliberately instrumented to reproduce realistic operational symptoms; the PostgreSQL session page in S3 is a simulator endpoint, not a production database.

| Scenario | Ticket | Primary learning objective | Tools |
|---|---|---|---|
| S1 | TEL-D1-101 | Expose tail latency hidden by averages and restore the missing RED error signal. | Prometheus, Grafana |
| S2 | TEL-D1-102 | Follow one failed checkout across service spans and correlate the same trace to application logs. | Jaeger, Loki, Grafana Explore |
| S3 | TEL-D1-103 | Separate causal infrastructure alerts from application symptoms using USE and dependency reasoning. | Prometheus, Alertmanager, Grafana |

**Delivery rule:** run one scenario at a time. The stacks reuse host ports and some fixed container names. The updated controller stops the other Day 1 scenario projects before starting the selected one.

## 2. Package map and file ownership

Extract the ZIP. The `day1/` directory contains:

```text
day1/
├── Participant_Guide_day1.docx / .md
├── Instructor_Solution_Guide_day1.docx / .md
├── shared/
│   ├── labctl.py
│   └── app/                         # shared simulated services and pinned dependencies
├── s1/
│   ├── validation_script.sh / .ps1
│   ├── lab/                         # Compose file, provisioning and pristine baseline
│   └── starter/                     # participant-editable config and evidence
├── s2/
│   ├── validation_script.sh / .ps1
│   ├── lab/                         # Compose, Loki/Grafana provisioning and pristine evidence
│   └── starter/                     # participant evidence template
├── s3/
│   ├── validation_script.sh / .ps1
│   ├── lab/                         # Compose, Alertmanager, dashboard and pristine baseline
│   └── starter/                     # participant alert/config/evidence artifacts
└── instructor/
    └── reference_answers/           # instructor-only worked evidence; never distribute alone
```

### 2.1 Which files may be edited?

| Path | Owner | Purpose | Participant action |
|---|---|---|---|
| `s1/starter/conf/prometheus.yml` | Participant | Prometheus scrape/rule configuration starter | Inspect; modify only if the exercise explicitly asks. |
| `s1/starter/grafana/dashboard_broken.json` | Participant/Grafana | Broken RED dashboard provisioned into Grafana | Fix the dashboard in Grafana UI and save. |
| `s1/starter/evidence/evidence_D1_1.json` | Participant | S1 incident record | Complete valid JSON. |
| `s2/starter/evidence/evidence_D1_2.md` | Participant | Trace/log/RCA record | Complete using a trace from the current run. |
| `s3/starter/alerts/use-alerts.yml` | Participant | Alert rules starter | Inspect and reason about the rules. |
| `s3/starter/conf/prometheus.yml` | Participant | Prometheus scrape and alert wiring | Inspect; do not change unless instructed. |
| `s3/starter/evidence/evidence_D1_3.json` | Participant | S3 incident record | Complete valid JSON. |
| `*/lab/baseline/` | Instructor/controller | Pristine reset copies | **Never edit during delivery.** |
| `shared/app/` and `shared/labctl.py` | Instructor/controller | Simulators, dependencies and control plane | Do not ask participants to edit. |

## 3. Host preparation — before the class

### 3.1 Supported execution host

Recommended: Ubuntu 22.04/24.04 x86_64 VM, 4 vCPU, 8 GB RAM minimum, 25 GB free disk. Docker Engine and Docker Compose v2 must already be installed and the daemon available. Python 3 is used by `shared/labctl.py` and only standard-library modules are required on the host. Application dependencies are installed in the container image during build.

Windows 10/11 with Docker Desktop Linux containers and PowerShell is supported for the scenario controller scripts. For the smoothest delivery, use Ubuntu/Linux for the full Compose workflow.

### 3.2 Host preflight — run once per VM

```bash
docker --version
docker compose version
docker info
python3 --version
curl --version
```

Expected: Docker CLI present, Compose v2 reported, daemon information returned, Python 3 available, and curl available. Do not reinstall Docker if these checks already pass.

### 3.3 Extract and set executable permissions — Linux

1. Extract the archive to a known location, for example `~/day1`.
2. Enter the directory that contains `s1`, `s2`, `s3` and `shared`.
3. Run the permission command immediately after extraction:

```bash
cd ~/day1
chmod +x s1/validation_script.sh s2/validation_script.sh s3/validation_script.sh shared/labctl.py
```

4. Verify:

```bash
ls -l s1/validation_script.sh s2/validation_script.sh s3/validation_script.sh shared/labctl.py
```

The scripts should show executable bits (`x`). If the ZIP was extracted again, repeat `chmod` because some extraction tools do not preserve Unix executable permissions.

### 3.4 Windows PowerShell

No chmod step is required. Open PowerShell in the extracted `day1` folder and use `cd .\s1`, `cd .\s2`, or `cd .\s3`. Run `.\validation_script.ps1 start`, `.\validation_script.ps1 check`, and `.\validation_script.ps1 reset` (remove the leading space before the dot when entering the command).

### 3.5 Ports and overlap

The scenarios use these ports:

| Port | Component |
|---:|---|
| 3000 | Grafana |
| 3100 | Loki (S2) |
| 8080 | S2 frontend |
| 8081 | S1 checkout or S2 checkout |
| 8082 | S2 payment |
| 8083 | S2 inventory or S3 telemetry simulator |
| 9090 | Prometheus (S1/S3) |
| 9093 | Alertmanager (S3) |
| 16686 | Jaeger (S2) |

S1/S2/S3 must not run concurrently. Before class, check for unrelated processes occupying these ports:

```bash
ss -ltnp | grep -E ':(3000|3100|8080|8081|8082|8083|9090|9093|16686)\\b' || true
docker ps --format 'table {{.Names}}\\t{{.Ports}}'
```

Do not kill unknown host processes. Resolve conflicts with the VM owner before class.

## 4. Master execution flow — follow in this order

1. Distribute `Participant_Guide_day1.docx` and the ZIP package. Keep this guide and `instructor/reference_answers/` private.
2. Confirm Docker/Compose/Python preflight on each participant VM.
3. Confirm the participant extracted the package and ran chmod on Linux.
4. Refer to `EVIDENCE_PASS_EXAMPLES.md` for the exact participant evidence values and validator rules. Start S1 from `~/day1/s1`; guide the RED dashboard investigation; collect evidence; run `check`; reset.
5. Start S2 from `~/day1/s2`; guide Jaeger-to-Loki correlation; collect evidence; run `check`; reset.
6. Start S3 from `~/day1/s3`; guide alert classification and USE analysis; collect evidence; run `check`; reset.
7. Review evidence, ask participants to explain the causal chain, and confirm the completion checklist.

**Important controller behavior:** `start` stops all Day 1 scenario Compose projects, resets the selected scenario to baseline, validates its Compose model, builds the application image, starts containers, and polls readiness endpoints. `reset` stops the selected project, removes its named volumes, and restores baseline starter files.

### 4.1 Standard command pattern

Linux, from the scenario directory:

```bash
./validation_script.sh start
./validation_script.sh check
./validation_script.sh reset
```

PowerShell, from the scenario directory:

```powershell
.\validation_script.ps1 start
.\validation_script.ps1 check
.\validation_script.ps1 reset
```

### 4.2 Evidence backup and restore paths

Pristine evidence files are held under each scenario's `lab/baseline/` directory. The controller restores these into `starter/evidence/` on `start`/`reset`. Before overwriting a changed starter file, it saves the participant's previous copy beside it, for example:

```text
s2/starter/evidence/evidence_D1_2.md.bak-20261119-161500
```

The baseline remains at:

```text
s2/lab/baseline/evidence_D1_2.md
```

Equivalent paths exist for S1 and S3. Backups are not deleted by the controller. Instructors should ask participants to copy any evidence they need to retain before resetting.

## 5. S1 instructor runbook — TEL-D1-101

**Ticket:** Checkout Is Slow but the Dashboard Looks Green  
**Time:** 75 minutes  
**Learning outcome:** identify the danger of mean latency on a bimodal distribution; use histogram quantiles; restore a missing 5xx signal.

### 5.1 Start and confirm the stack

```bash
cd ~/day1/s1
./validation_script.sh start
```

The controller should report checkout-service, Prometheus and Grafana ready. If it does not, stop the exercise and troubleshoot before UI work.

Open these pages:

- Grafana: `http://localhost:3000` (default lab credentials `admin` / `admin`)
- Prometheus: `http://localhost:9090`
- Prometheus targets: `http://localhost:9090/targets`
- Checkout metrics: `http://localhost:8081/metrics`

### 5.2 Instructor navigation — Grafana

1. Open Grafana in the browser.
2. Use the left navigation to open **Dashboards**.
3. Open **RED Checkout Dashboard**.
4. Point out the **Payment Duration** panel and its current mean/recording-series query.
5. Open the panel title menu (three dots) → **Edit**.
6. In the query editor, select the Prometheus query field and replace the existing expression with:

```promql
histogram_quantile(0.95, sum by (le) (rate(payment_duration_seconds_bucket[5m])))
```

7. Keep the panel unit in seconds. Do not append `* 1000`; the displayed unit is `s`.
8. Click **Apply** / return to the dashboard. Allow enough time for samples to accumulate; the p95 should expose the ~4.6-second slow cohort.
9. Add a panel using **Add** → **Visualization** (or **Add panel**, depending on Grafana layout).
10. Select the Prometheus data source and enter:

```promql
100 * sum(rate(http_requests_total{service="checkout-service",status=~"5.."}[5m])) / sum(rate(http_requests_total{service="checkout-service"}[5m]))
```

11. Set title **5xx Error Rate (%)**, unit **Percent (0–100)**, and click **Apply**.
12. Click **Save dashboard** in the dashboard header. Confirm the save operation.

### 5.3 Instructor navigation — Prometheus

Open **Status** → **Targets** or directly visit `/targets`. Confirm `shopnow-checkout` is UP. Then open **Graph** and run:

```promql
up{job="shopnow-checkout"}
rate(http_requests_total{service="checkout-service"}[5m])
histogram_quantile(0.95, sum by (le) (rate(payment_duration_seconds_bucket[5m])))
```

Expected interpretation:

- `up` returns 1 for the target.
- Request rate is non-zero after the load generator has sent traffic.
- p95 rises toward the slow cohort (about 4.6 seconds); exact values vary with timing and scrape windows.
- 5xx percentage should be non-zero over a sufficiently long window because the simulator injects a small error share.

### 5.4 S1 Prometheus troubleshooting — resolved configuration pattern

The working S1 Compose file mounts `s1/starter/conf/` into `/etc/prometheus/`. Both `prometheus.yml` and `legacy_rules.yml` must remain in that same directory. `prometheus.yml` references `legacy_rules.yml`; a missing/misnamed rule file or a target of `localhost:8081` can prevent the intended scrape/rule behavior. The target must be `checkout:8081` because Prometheus resolves the Compose service name inside the Docker network.

Run from `~/day1/s1`:

```bash
docker compose -p telemetry-d1-s1 -f lab/docker-compose.yml ps
docker compose -p telemetry-d1-s1 -f lab/docker-compose.yml logs --tail=150 prometheus
curl -fsS http://localhost:9090/-/ready
curl -fsS http://localhost:9090/api/v1/targets
```

If Prometheus is not ready, inspect the logs for YAML parse errors, missing rule files or bind-mount paths. Restore the baseline with `./validation_script.sh reset`, then restart. Do not patch the container filesystem; make any required participant change in `starter/conf/` only.

### 5.5 S1 validation and expected result

Participant completes `s1/starter/evidence/evidence_D1_1.json` with valid JSON. The `check` command evaluates the evidence and calls the Grafana dashboard API for UID `red-checkout`. It verifies both expressions are saved. Expected: **7/7 checks** (five evidence rules plus two live Grafana checks) pass. If the UI query was edited but the dashboard not saved, the live check correctly fails.

## 6. S2 instructor runbook — TEL-D1-102

**Ticket:** Orders Fail for One Product: Follow the Trace  
**Time:** 75 minutes  
**Learning outcome:** inspect a distributed trace, identify a failing child span, correlate its trace ID to Loki, distinguish a dependency conflict from the outer HTTP 500.

### 6.1 Start and confirm S2

```bash
cd ~/day1/s2
./validation_script.sh start
```

The Compose project name is `telemetry-d1-s2`. Required services and host ports:

| Service | Container | Host port | Health URL |
|---|---|---:|---|
| frontend | d1-frontend | 8080 | `http://localhost:8080/health` |
| checkout | d1-checkout-service | 8081 | `http://localhost:8081/health` |
| payment | d1-payment-service | 8082 | `http://localhost:8082/health` |
| inventory | d1-inventory-service | 8083 | `http://localhost:8083/health` |
| Jaeger | d1-jaeger | 16686 | `http://localhost:16686` |
| Loki | d1-loki | 3100 | `http://localhost:3100/ready` |
| Grafana | d1-grafana | 3000 | `http://localhost:3000/api/health` |

The load generator waits for the frontend, sends a seeded PROD-7729 request with a W3C traceparent, then sends mixed traffic continuously. A 409 from inventory is deliberately converted to a generic 500 by checkout. Timing and trace IDs may vary.

### 6.2 Jaeger UI — exact instructor navigation

1. Open `http://localhost:16686` in the VM browser.
2. Confirm the **Search** tab is selected.
3. In the left Search form, open **Service** and select `frontend`.
4. If Operation is available, select `POST /api/checkout`; otherwise leave it as `all`.
5. Leave Tags empty initially. Set **Lookback** to **Last Hour**.
6. Click **Find Traces**.
7. The right pane displays the trace duration chart and result rows. Select a row that shows an error badge / red error count. The root operation should read `frontend: POST /api/checkout`.
8. Open that result. Jaeger displays the trace timeline at the top and the **Service & Operation** span tree below.
9. Expand the tree using the chevrons next to `frontend`, `checkout-service`, and `inventory-service` until `inventory.reserveStock` is visible.
10. Select the `inventory.reserveStock` span. In the detail pane, open **Tags**. Expected attributes include:
    - `error = true`
    - `error.type = StockReservationException`
    - `product.sku = PROD-7729`
    - HTTP status code `409`
    - An error/status description stating the warehouse bin is locked due to a cycle-count audit.
11. Select the parent checkout span if necessary. It should show the outward HTTP 500 response. Explain that the inventory dependency returns 409, while the customer-facing checkout endpoint deliberately masks the dependency failure as 500.
12. **Trace ID capture:** read the browser address bar. The path is `/trace/<trace-id>`. Copy the full 32-character hexadecimal value after `/trace/`. Example from the participant's validation screenshots: `2fb318c8439abc2af7bd3cbd645054a5`. This is a reference example, not a required fixed ID.

**Important correction to old materials:** The earlier lab guide instructed participants to search for one fixed trace ID (`4bf92f3577b34da6a3ce929d0e0e4736`). That is the seeded trace context, but a participant may select another valid failed runtime trace. The updated validation accepts any valid 32-character trace ID if the Jaeger URL and Loki query use the same value. Do not fail a participant solely because the chosen ID differs from the seeded ID.

### 6.3 Grafana Explore — exact navigation and LogQL

1. Open `http://localhost:3000/explore`.
2. In the data source selector at the top-left of Explore, choose **Loki** (UID `loki`).
3. Select the query editor / code mode if the UI opens in builder mode.
4. Enter the query, replacing the example with the trace ID just copied from Jaeger:

```logql
{app="inventory-service"} |= "<TRACE_ID_FROM_JAEGER>"
```

5. Click **Run query**.
6. Inspect the returned line. It should show the inventory-service error, `StockReservationException`, `PROD-7729`, and the cycle-count audit lock. The line includes `trace_id=<same-id>` and `span_id=...` in the formatted message.
7. If there are no rows, verify the selected datasource is Loki, use the exact label `app="inventory-service"`, remove any extra filters, confirm the copied trace ID, and check Loki readiness.

Optional API verification from the VM terminal:

```bash
TRACE_ID='<TRACE_ID_FROM_JAEGER>'
curl -G -s 'http://localhost:3100/loki/api/v1/query_range' \
  --data-urlencode "query={app=\"inventory-service\"} |= \"${TRACE_ID}\"" \
  --data-urlencode 'limit=20' | python3 -m json.tool
```

### 6.4 S2 evidence — instructor reference answer

The participant file is `s2/starter/evidence/evidence_D1_2.md`. Require:

- Participant and timestamp.
- Actual runtime Trace ID from the browser URL.
- Full Jaeger URL containing that same ID.
- Root operation `frontend: POST /api/checkout`.
- Failed child span `inventory.reserveStock` in `inventory-service`.
- SKU `PROD-7729`.
- Inventory HTTP 409 and parent checkout HTTP 500.
- LogQL `{app="inventory-service"} |= "<same-trace-id>"`.
- Exception `StockReservationException` and the warehouse bin cycle-count audit lock.
- Safe recommendation: coordinate release/availability of the bin after audit, implement explicit conflict/retry or alternate-bin handling, and improve error mapping/observability. Do not disable audit controls.

A worked example is included at `instructor/reference_answers/S2_REFERENCE_EVIDENCE_TEL-D1-102.md`. It contains a trace ID from the captured validation screenshot for teaching purposes. Never copy that example into participant evidence as if it came from their current run.

### 6.5 S2 validation logic and expected result

The updated validator:

1. Rejects unfilled template tokens.
2. Extracts a 32-character hexadecimal Trace ID from the evidence `Trace ID:` field.
3. Requires the Jaeger URL to contain that exact ID.
4. Requires the LogQL query to use that exact ID with the `inventory-service` label.
5. Checks the failing span, target SKU, exception and audit/cycle-count root-cause evidence.
6. Checks all S2 readiness endpoints before reporting a successful evidence validation.

Expected: **5/5 checks** pass. A wrong or missing Trace ID, mismatched URL/query, missing exception, or unready service fails validation with a specific message.

### 6.6 S2 recovery — no-cache rebuild when required

Use this only if the initial controller build fails, a required container exits, or the stack is inconsistent. Run each command from `~/day1/s2` and wait for completion before the next command.

**Step 1 — Rebuild without cache**

```bash
docker compose -p telemetry-d1-s2 -f lab/docker-compose.yml build --no-cache
```

**Step 2 — Recreate all services**

```bash
docker compose -p telemetry-d1-s2 -f lab/docker-compose.yml up -d --force-recreate
```

**Step 3 — Verify container state**

```bash
docker compose -p telemetry-d1-s2 -f lab/docker-compose.yml ps
```

Expected: all eight containers show `Up`. If not, run:

```bash
docker compose -p telemetry-d1-s2 -f lab/docker-compose.yml logs --tail=150
```

The package pins Python application dependencies and includes `setuptools==80.9.0` in `shared/app/requirements.txt`, reflecting the dependency adjustment used during the validated image rebuild. If a build still fails, preserve the full error output; do not keep appending unpinned packages to the requirements file.

## 7. S3 instructor runbook — TEL-D1-103

**Ticket:** Six Alerts at Shift Start, One Real Problem  
**Time:** 60 minutes  
**Learning outcome:** distinguish symptoms from cause using Utilization, Saturation and Errors; correlate infrastructure metrics with a long-running query.

### 7.1 Start and confirm S3

```bash
cd ~/day1/s3
./validation_script.sh start
```

Open:

- Alertmanager: `http://localhost:9093`
- Prometheus Alerts: `http://localhost:9090/alerts`
- Prometheus Graph: `http://localhost:9090/graph`
- Grafana: `http://localhost:3000`
- Simulated PostgreSQL activity: `http://localhost:8083/pg_stat_activity`

Allow approximately 60 seconds for Prometheus scrape intervals and the alert rules' `for: 30s` windows.

### 7.2 Alertmanager navigation

1. Open `http://localhost:9093`.
2. Select **Alerts**.
3. Review the six alerts: `CheckoutSlow`, `PaymentTimeout`, `ProfileQueryDegraded`, `OrderHistory504`, `DiskIOWaitHigh`, `DatabaseQueueSaturation`.
4. Ask participants which are user-facing symptoms and which are infrastructure-level signals.
5. Do not reveal the root cause immediately. Ask them to compare the alert timing, severity and underlying metric.

### 7.3 Prometheus navigation and exact queries

1. Open `http://localhost:9090/alerts` and inspect each alert's expression and state.
2. Open **Graph** (or `/graph`).
3. Enter and execute the following expressions one at a time:

```promql
db_disk_queue_length{instance_role="primary"}
db_disk_io_await_milliseconds{instance_role="primary"}
db_cpu_utilization_percent{instance_role="primary"}
db_memory_utilization_percent{instance_role="primary"}
```

Expected: disk queue is approximately 38 and I/O await approximately 280 ms; CPU and memory are comparatively normal. This is a saturation problem, not primarily a CPU/memory utilization issue.

### 7.4 Grafana USE dashboard navigation

1. Open `http://localhost:3000`.
2. Open **Dashboards** from the left navigation.
3. Select **USE Dashboard - PostgreSQL Primary**.
4. Review panels for CPU, memory, disk queue, I/O await, hardware errors and checkout p95.
5. Use the panel values to reinforce Utilization vs Saturation vs Errors.

### 7.5 Simulated PostgreSQL session investigation

Open `http://localhost:8083/pg_stat_activity` in a new browser tab. Find PID `9182`:

- user: `analytics_batch`
- application: `nightly-report-runner`
- state: active
- wait event: `IO / DataFileRead`
- running time: approximately 47 minutes
- query: 90-day aggregation joining `orders` and `order_items`, with no index on `created_at`

Explain the causal chain: a long-running, unindexed reporting query creates high primary disk I/O queue and await; the application-facing alerts are downstream effects. The endpoint returns synthetic JSON. There is no live PostgreSQL process behind this simulation and no SQL session should be killed.

### 7.6 Expected S3 evidence and remediation

The evidence file `s3/starter/evidence/evidence_D1_3.json` must identify `DatabaseQueueSaturation` as the primary causal alert, `DiskIOWaitHigh` as corroborating evidence, PID `9182`, PostgreSQL primary, and a read-replica reporting mitigation. Strong answers also propose query/index review, reporting workload scheduling, monitoring replication lag, and verifying recovery after controlled remediation.

Expected validation: **5/5 checks** pass.

## 8. Reset, backups and moving between scenarios

At the end of each scenario, have participants run the reset command from that scenario directory:

```bash
./validation_script.sh reset
```

Reset stops the selected Compose project and removes its named volumes (`down -v`), then restores starter files from that scenario's `lab/baseline/` folder. Any modified starter file is saved as a timestamped `.bak-...` file beside the participant copy before restore. Participants should preserve evidence backups they need before reset.

The updated `start` command also stops all other Day 1 projects before starting a new one. This is a safety net, not a substitute for teaching the explicit reset step.

## 9. Troubleshooting decision tree

### 9.1 `permission denied` when starting the script

Cause: executable bit not set after extraction. From `~/day1`:

```bash
chmod +x s1/validation_script.sh s2/validation_script.sh s3/validation_script.sh shared/labctl.py
```

Then re-enter the scenario directory and retry.

### 9.2 Docker daemon unavailable / permission denied

Run `docker info`. If daemon is stopped, use the host's approved Docker service procedure. If permission denied, resolve group/session access with the VM administrator. The lab controller deliberately does not install Docker or modify host group membership.

### 9.3 Port conflict

Run:

```bash
ss -ltnp | grep -E ':(3000|3100|8080|8081|8082|8083|9090|9093|16686)\\b' || true
docker ps --format 'table {{.Names}}\\t{{.Ports}}'
```

Inspect the owning process/container. Stop the previous Day 1 stack using its reset command. Do not kill unrelated processes.

### 9.4 Compose build fails

From the scenario folder:

```bash
docker compose -p telemetry-d1-s2 -f lab/docker-compose.yml build --no-cache
```

This is the S2 recovery example. Substitute the appropriate project and Compose file for other scenarios. Inspect the first failing package/build line, confirm internet access, and inspect `shared/app/requirements.txt`. Do not repeatedly rebuild without reading the error.

### 9.5 Container exits

```bash
docker compose -p telemetry-d1-s2 -f lab/docker-compose.yml ps -a
docker compose -p telemetry-d1-s2 -f lab/docker-compose.yml logs --tail=150 <service-name>
```

Use service names such as `frontend`, `checkout`, `payment`, `inventory`, `jaeger`, `loki`, `grafana`, `loadgen`.

### 9.6 Prometheus is not ready in S1/S3

```bash
docker compose -p telemetry-d1-s1 -f lab/docker-compose.yml logs --tail=150 prometheus
curl -fsS http://localhost:9090/-/ready
```

Check YAML syntax, mounted config path and the Compose DNS target. S1 must scrape `checkout:8081`; S3 must scrape `dbsim:8083`. The S1 legacy recording rule file must remain alongside `prometheus.yml` in `starter/conf/`.

### 9.7 Jaeger Search has no traces

```bash
docker compose -p telemetry-d1-s2 -f lab/docker-compose.yml ps
docker compose -p telemetry-d1-s2 -f lab/docker-compose.yml logs --tail=100 loadgen
docker compose -p telemetry-d1-s2 -f lab/docker-compose.yml logs --tail=100 checkout
```

Confirm `frontend`, `checkout`, `inventory`, `jaeger` and `loadgen` are running. Search Service `frontend`, set Lookback **Last Hour**, and wait 30–60 seconds.

### 9.8 Loki query returns no rows

Check `http://localhost:3100/ready`; in Grafana Explore choose datasource Loki, use `{app="inventory-service"}`, and paste the exact ID from the Jaeger URL. The LogQL label is `app`, not `service`.

### 9.9 Validation says the S2 trace ID is missing

The trace ID must be recorded on a line beginning `Trace ID:` with exactly 32 hexadecimal characters. The full Jaeger URL must contain the same value after `/trace/`, and the LogQL query must contain the same value. Do not copy a trace ID from a different run or use a short trace prefix.

### 9.10 Validation says dashboard query missing in S1

Edit the correct dashboard (`RED Checkout Dashboard`, UID `red-checkout`), click **Apply**, then **Save dashboard**. The check reads the saved dashboard from Grafana's API; an unsaved editor state is not sufficient.

## 10. Assessment rubric

| Area | Points | Evidence |
|---|---:|---|
| Root-cause reasoning | 25 | Correctly explains the incident mechanism and impact. |
| Query and tool navigation | 25 | Uses valid PromQL/LogQL and finds the correct UI details. |
| Cross-signal correlation | 20 | Connects metrics, traces, logs or alerts instead of relying on one screen. |
| Safe remediation | 15 | Recommends controlled, non-destructive actions. |
| Evidence completeness | 15 | Accurate IDs, queries, outputs, timestamps and no placeholders. |
| **Total** | **100** | Instructor judgement across all scenarios. |

## 11. Final instructor sign-off

- [ ] Host prerequisites passed; no Docker install required.
- [ ] Linux execute permissions set after extraction.
- [ ] S1 starts, Prometheus target is UP, Grafana dashboard fix is saved, validation passes.
- [ ] S2 services are ready, Jaeger trace ID captured from URL, Loki query uses same ID, validation passes.
- [ ] S3 alerts and Prometheus metrics are visible, PID 9182 identified, validation passes.
- [ ] Participant evidence reviewed and backups preserved if required.
- [ ] Each scenario reset; no scenario containers remain running.
- [ ] Instructor-only reference evidence was not distributed as participant work.
