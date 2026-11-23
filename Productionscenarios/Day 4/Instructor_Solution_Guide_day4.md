# Reading Telemetry & Observability - Instructor Solution Guide: Day 4 (v2.0)

> **CONFIDENTIAL - TRAINER USE ONLY.** Do not distribute to participants.

## 1. What changed in v2.0 and why

| Problem in the original package | Fix |
| :--- | :--- |
| Labs needed root, systemd and `/opt/labs`; not runnable for 40 learners on their own machines | Self-contained Docker Compose kit per scenario; the harness is `validate.py` (Python standard library) with thin `.sh` / `.ps1` wrappers |
| s3 depended on running s1 and s2 first | Each scenario has its own compose project and data |
| Checks were keyword greps on an answer card | Live checks against Prometheus, Loki and the Grafana API, plus evidence content checks |
| Thresholds differed between the guide (Warning > 1, Critical > 5) and the checks | One definition: Warning 5, Critical 20 errors per minute |
| s2 solution used `rate(...[5m])` (per second) while the thresholds were per minute | Query must return errors per minute (`count_over_time(...[1m])`) |
| s3 regex fix did not match the starter regex | Starter regex is `/^(order\|payment\|inventory\|notification).*$/`, solution uses `(?:...)` |
| Guide listed Splunk (8000), Jaeger, Alertmanager and 8080-8083 | Removed: not used by any Day 4 lab |
| s1 required a real New Relic agent per learner | One shared simulator (`s1/instructor/newrelic-sim/`) feeds one New Relic account |

## 2. Fleet and logistics

- Learner machines: Docker 24+ with Compose v2, Python 3.8+, 4 GB RAM free. Pre-pull images before class (`docker compose pull` in each `starter/kit`): `prom/prometheus:v3.5.0`, `grafana/grafana:12.0.2`, `grafana/loki:2.9.8`, `grafana/promtail:2.9.8`, `python:3.12-slim`.
- Ports `3000, 3100, 9090, 8095` free. One scenario at a time per machine.
- **New Relic (s1):** create one account; add learners as Basic users; run `s1/instructor/newrelic-sim` on the instructor machine at least 30 minutes before class (see its README). If New Relic is not ready, learners complete the PromQL parts and you demonstrate the NRQL screens.
- No real credentials ship in the package. The Grafana password is the placeholder `admin` in `.env`; the New Relic licence key exists only in your own `.env`.

## 3. Methodology

1. Present each scenario as a ticket and do not reveal the cause.
2. Learners run `start` and observe the failure before changing anything.
3. Ask questions (golden signals, RED, average vs percentile) rather than giving the answer.
4. Evidence must contain real queries before `check` is run.

## 4. Solutions

### TEL-D4-401: Slow-Transaction Report

**Expected failure.** The APM overview shows a healthy average (about 1.9 s for processPayment) because 10 % of its requests are slow.

**Solution queries.**

```text
SELECT percentile(duration, 95) AS 'P95', average(duration), max(duration) FROM Transaction WHERE appName = 'ShopNow-Production' FACET name LIMIT 5 SINCE 1 day ago
SELECT percentile(duration, 95) FROM Transaction WHERE appName = 'ShopNow-Production' AND name = 'CheckoutController#processPayment' TIMESERIES SINCE 1 hour ago
SELECT count(*) FROM TransactionError WHERE appName = 'ShopNow-Production' FACET error.class SINCE 1 day ago
```

```text
topk(5, histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[1d])) by (le, handler)))
```

**Expected result.** `CheckoutController#processPayment` first, p95 about 4.2 s (accepted 3.5 - 5.0). The simulator's ranking was verified locally with bucket interpolation.

**RCA.** The overview shows the average, which hides a slow tail; the percentile exposes it. Recommendation: alert on p95 per transaction and investigate the payment gateway call.

**Check (5 rules).** Live Prometheus top handler and p95; NRQL ranking; NRQL TIMESERIES and TransactionError; PromQL cross-check and the named slowest transaction; evidence complete (RCA at least 80 characters, mentions average and percentile).

**Rubric (20 pts).** 4 per rule.

### TEL-D4-402: Error Panel Shows Zero

**Expected failure.** The panel query `sum(count_over_time({app="payment-service"} |= "error" [1m]))` returns 0: the line filter is case-sensitive, the logs say `"level":"ERROR"`.

**Solution query.**

```text
sum(count_over_time({app="payment-service"} | json | level="ERROR" [1m]))
```

Thresholds: base green, 5 yellow, 20 red. Expected value during the outage is about 90 per minute. Reference file: `s2/instructor/dashboard_fixed.json`. Save the dashboard.

**Check (5 rules).** Saved panel query repaired; live Loki value at least 20; thresholds exactly 5 and 20 with green base and red top; evidence names the fix and the cause; evidence complete with `verifiedOnPlatform` true.

**Teaching note.** `rate(...[5m])` gives per-second values (about 1.5), which never reach the thresholds. Discuss the unit.

### TEL-D4-403: Percentile and Variable

**Defects.** (1) p95 without `rate()` is cumulative since start. (2) Error rate is a raw counter sum, not a percentage. (3) Variable regex captures only the prefix (`order` instead of `order-service`).

**Solutions.**

```text
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{service=~"$service"}[5m])) by (le, service))
100 * sum(rate(http_requests_total{status=~"5..", service=~"$service"}[5m])) / sum(rate(http_requests_total{service=~"$service"}[5m]))
/^(?:order|payment|inventory|notification).*$/
```

Reference file: `s3/instructor/dashboard_fixed.json`.

**Check (5 rules).** p95 query shape; error-rate query shape; regex emulation shows all 4 full names; live evaluation sane (p95 0-15 s, error 0-30 %); evidence complete.

## 5. Scoring

Each scenario is 5 checks. Total 15 checks, 100 points: 33 + 33 + 34. Partial credit is per check. Solved evidence samples are in each `instructor/` folder.

## 6. Clean-up

Learners: `./validation_script.sh reset --yes`. Instructor: `docker compose down` in `newrelic-sim`. Revoke or delete the New Relic licence key and the learner users after class.

## 7. Unverified items (read before class)

The authoring environment had no Docker, so the following were not run end to end:

- Docker images and compose files; Loki 2.9 and Grafana 12 behaviour; Promtail parsing of the JSON logs.
- The Grafana dashboard import API and saved-dashboard read by `validate.py` (tested only against a mock server).
- The Loki instant query used for the live check, and the Prometheus checks against real data (the simulator's p95 was verified by local calculation).
- PowerShell wrappers (syntax not run on Windows).
- New Relic: Basic-user NRQL access, free-tier data limits for 40 users, `error.class` format, the shared simulator.
- Timing: how long the first image pull takes on your network.

**Do a full dry run of each scenario on a clean machine before class.**
