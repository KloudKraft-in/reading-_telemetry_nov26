# Day 4 Lab 1 — New Relic NRQL Telemetry Generator & Setup Guide

## 1. Unified Directory Structure (`day4-newrelic/`)

```text
day4-newrelic/
├── .env.example                      # Template for NEW_RELIC_LICENSE_KEY, NEW_RELIC_ACCOUNT_ID, NEW_RELIC_REGION
├── nr_easytravel_shipper.py          # Ships easyTravel-Frontend & easyTravel-Backend Transaction, TransactionError, Span events
├── faultctl.sh                       # Instructor Cue C0/C1/C2 switch (CreditCardCheckError500 ON/OFF)
└── setup_lab1.sh                     # One-command Ubuntu launcher & log verifier
```

---

## 2. Purpose of Every Artefact

1. **`nr_easytravel_shipper.py`**
   * **Purpose:** Generates realistic `Transaction`, `TransactionError`, and `Span` telemetry for `easyTravel-Frontend` and `easyTravel-Backend` on host `ip-172-30-0-220` and pushes batches via the New Relic Event API (`insights-collector.newrelic.com`).
   * **Schema & Breakdown Support:** Populates `appName`, `name`, `duration`, `databaseDuration`, `databaseCallCount`, `externalDuration`, `externalCallCount`, `error`, `host`, `http.statusCode`, `trace.id`, and `span.id` so every query in Tasks 1–4 (`keyset()`, `percentile()`, `histogram()`, `databaseDuration`/`externalDuration` breakdown, `COMPARE WITH`, `TransactionError` facets, and `apdex()`) produces authentic results.
2. **`faultctl.sh`**
   * **Purpose:** Controls the `CreditCardCheckError500` fault switch (`./faultctl.sh on` for **Cue C1**, `./faultctl.sh off` for **Cue C2**, `./faultctl.sh status`).
3. **`setup_lab1.sh` & `.env.example`**
   * **Purpose:** Loads your New Relic Ingest License Key and Account ID, initializes the fault to `OFF`, starts the background shipper, and verifies HTTP `200` ingestion.

---

## 3. Ubuntu Terminal Launch & Fault Cues (C1, C2)

### Quick Launch from ZIP
```bash
unzip day4-newrelic-lab1.zip -d ~/
cd ~/day4-newrelic
cp .env.example .env
# Edit .env with your New Relic Ingest License Key and Account ID
nano .env
chmod +x setup_lab1.sh faultctl.sh nr_easytravel_shipper.py
./setup_lab1.sh
```

### Triggering Fault Cues During Validation
```bash
cd ~/day4-newrelic

# Cue C0 (Start of Task 1): Confirm fault is OFF
./faultctl.sh off

# Cue C1 (Start of Task 3): Turn CreditCardCheckError500 ON (wait 4 minutes before Q5–Q7)
./faultctl.sh on

# Cue C2 (End of Task 3 / Before Task 4): Turn CreditCardCheckError500 OFF
./faultctl.sh off
```
