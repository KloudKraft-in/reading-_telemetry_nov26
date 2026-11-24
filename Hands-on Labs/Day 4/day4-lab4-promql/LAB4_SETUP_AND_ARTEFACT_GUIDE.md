# Day 4 Lab 4 — PromQL Fundamentals Setup & Artefact Guide

## 1. Unified Directory Structure (`day4-promql/`)

```text
day4-promql/
├── prometheus.yml                    # Configures 5s scrape_interval for prometheus, easytravel, and node jobs
├── mock_easytravel.py                # Exposes http_server_requests_total{env="cohort",service,route,method,status} & duration histogram
├── faultctl.sh                       # Instructor Cue controller: Cue R1 (reset), Cue C1 (on), Cue C2 (off)
└── setup_lab4.sh                     # One-command Ubuntu launcher & Prometheus target verifier
```

---

## 2. Purpose of Every Artefact

1. **`prometheus.yml`**
   * **Purpose:** Sets `scrape_interval: 5s` (matching Pre-Lab check `4 × 5s = 20s` / `[1m]` rate window) and scrapes three jobs on `obs-net`: `prometheus` (`localhost:9090`), `easytravel` (`easytravel-mock:8000`), and `node` (`node-exporter:9100`).
2. **`mock_easytravel.py`**
   * **Purpose:** Emits Prometheus counters and histograms matching the Day 4 Lab 4 metric contract:
     * `http_server_requests_total{env="cohort",service,route,method,status}` across `easytravel-frontend` (`/`, `/search`, `/booking`, `/checkout`) and `easytravel-backend` (`/api/journeys`, `/api/booking`, `/api/checkout/creditcard-check`, `/api/auth`).
     * `http_server_request_duration_seconds_bucket` / `_sum` / `_count`.
     * Starts with **0 `5xx` errors** while healthy (so Task 1 Step 4 `status!~"2.."` returns `0` before Cue C1), and injects `HTTP 500` errors (~35% on `/checkout`) when Cue C1 is enabled.
3. **`faultctl.sh`**
   * **Purpose:** Implements all three Appendix A instructor cues on the Ubuntu host:
     * `./faultctl.sh reset` (**Cue R1** — restarts `easytravel-mock` so counters reset to `0`, making `resets(...[10m]) = 1` and `delta(...[10m]) < 0` in Task 2).
     * `./faultctl.sh on` (**Cue C1** — enables `CreditCardCheckError500` for Task 3 error-rate queries).
     * `./faultctl.sh off` (**Cue C2** — disables `CreditCardCheckError500` before Task 4 aggregations).
4. **`setup_lab4.sh`**
   * **Purpose:** Creates `obs-net`, starts `easytravel-mock`, `node-exporter`, and read-only `prometheus` (`prom/prometheus:latest` without `--web.enable-admin-api` or `--web.enable-lifecycle`), sets fault state to `OFF`, and verifies all 3 targets are `UP` at `5s`.

---

## 3. Ubuntu Terminal Launch & Cues (R1, C1, C2)

### Quick Launch from ZIP
```bash
unzip day4-promql-lab4.zip -d ~/
cd ~/day4-promql
chmod +x setup_lab4.sh faultctl.sh mock_easytravel.py
./setup_lab4.sh
```

### Triggering Instructor Cues During Validation
```bash
cd ~/day4-promql

# Cue R1 (Task 2 Step 2): Restart metrics exporter to reset counters to 0 (wait 45s after)
./faultctl.sh reset

# Cue C1 (Task 3 Step 1): Turn CreditCardCheckError500 ON (wait 2 min after)
./faultctl.sh on

# Cue C2 (Task 3 Step 5 / Before Task 4): Turn CreditCardCheckError500 OFF
./faultctl.sh off

# Check current fault status
./faultctl.sh status
```
