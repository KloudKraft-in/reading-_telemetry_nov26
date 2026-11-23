# Reading Telemetry & Observability - Participant Lab Guide: Day 4 (v2.0)

## Hands-On Production Scenarios
### New Relic, Grafana, Loki & Prometheus

---

## 1. Setup Requirements

All three labs run on your own laptop or VM with Docker. Nothing needs root, systemd or a real account of your own.

| Component | Version | Check |
| :--- | :--- | :--- |
| Docker + Compose v2 | Docker 24+ | `docker compose version` |
| Python | 3.8+ | `python3 --version` (Windows: `python --version`) |
| Browser | any current one | - |
| Hardware | 2 vCPU, 4 GB RAM free, 5 GB disk | - |

Ports used (free them first): `3000` Grafana, `3100` Loki, `9090` Prometheus, `8095` simulator. Every lab binds to `127.0.0.1` only.

**Run one scenario at a time.** s2 and s3 both use port 3000. `reset --yes` stops everything and frees the ports.

New Relic (lab s1 only): your instructor gives you a login to a shared New Relic account. Do not create your own account and never paste licence keys into your evidence.

The Grafana login is `admin` with the password in `starter/kit/.env` (a local placeholder, not a real credential).

## 2. Standard Lab Workflow

1. Open a terminal in the scenario folder (`day4/s1`, `s2` or `s3`).
2. `./validation_script.sh start` (Windows: `.\validation_script.ps1 start`). The first start downloads images and can take a few minutes.
3. Read `starter/README_START_HERE.txt`.
4. Investigate, fix, and fill `starter/evidence/`.
5. `./validation_script.sh check`. Each check explains what is missing. Fix and re-run.
6. `./validation_script.sh reset --yes` deletes the lab and your work, so use it only to start over or when finished.

---

## 3. Scenarios

### TEL-D4-401: Slow-Transaction Report for the Ops Review (60 min)

**Platform:** New Relic (NRQL) and Prometheus. **Folder:** `day4/s1`.

**Ticket.** Operations needs a p95 latency ranking of ShopNow-Production transactions. The default APM overview does not show the slowest transactions, and it looks healthy.

**Start.** Run `start`, then wait 5-10 minutes so that Prometheus has data.

**Tasks.**

1. In the New Relic NRQL Query builder, rank the top 5 transactions by p95 (also show average and max). Use `FACET name`.
2. Show the trend of the slowest transaction with `TIMESERIES`.
3. Find out which errors hit the slowest transactions (`FROM TransactionError`, `FACET error.class`).
4. Cross-check in Prometheus (http://localhost:9090) with `histogram_quantile`.
5. Explain in the RCA why the default overview hides the problem (average vs percentile).
6. Fill `starter/evidence/evidence_D4_1.md` and run `check`.

**Hints.** Metric `http_request_duration_seconds_bucket`, label `handler`. In NRQL use `percentile(duration, 95)`.

### TEL-D4-402: Error Panel Shows Zero During an Outage (75 min)

**Platform:** Grafana and Loki. **Folder:** `day4/s2`.

**Ticket.** payment-service is failing, yet the Grafana panel "Payment Error Volume" shows 0.

**Start.** Run `start`. It creates the outage (about 90 ERROR logs per minute) and loads the dashboard. Wait 5 minutes.

**Tasks.**

1. In Grafana **Explore** (datasource Loki), look at `{app="payment-service"}` and find why the existing query returns 0.
2. Fix the panel query so that it returns **errors per minute** from the JSON field `level`.
3. Set thresholds: base green, **Warning at 5**, **Critical at 20** errors per minute.
4. **Save** the dashboard (the check reads the saved version).
5. Fill `starter/evidence/evidence_D4_2.json` (replace every `<<FILL_...>>`; `verifiedOnPlatform` is `true` or `false`).

**Hints.** Compare the case of "error" in the query and in the logs. Use the JSON parser stage. `count_over_time(...[1m])` already gives events per minute.

### TEL-D4-403: Latency Percentile and Service Variable Are Wrong (90 min)

**Platform:** Grafana and Prometheus. **Folder:** `day4/s3`.

**Ticket.** On the "ShopNow SRE Dashboard" the latency panel is a flat line, the error panel is not a percentage, and choosing a service gives "No Data".

**Start.** Run `start`. Let it run 5-10 minutes so that `rate()` has data.

**Tasks.**

1. Fix **P95 Latency**: compute the percentile over a recent window, grouped correctly, and filter on `$service`.
2. Fix **Service Error Rate**: percentage of 5xx requests out of all requests (rates, not raw counters), filtered on `$service`.
3. Fix the **service variable** (Dashboard settings -> Variables) so that all four full names appear: `order-service`, `payment-service`, `inventory-api`, `notification-service`.
4. **Save** the dashboard.
5. Fill `starter/evidence/evidence_D4_3.json` and run `check`.

**Hints.** Counters and histogram buckets only grow; `rate()` turns them into per-second values. In a Grafana variable regex, the first capture group becomes the value.

---

## 4. Evidence Rules

- Replace every `<<FILL_...>>` placeholder. The check fails while any `<<` remains.
- Paste your real queries, not descriptions.
- Never put keys, tokens or passwords in evidence files.
