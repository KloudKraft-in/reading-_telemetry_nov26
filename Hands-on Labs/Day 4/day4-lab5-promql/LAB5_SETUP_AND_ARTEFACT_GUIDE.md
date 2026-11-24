# Day 4 — Lab 5 Setup & Artefact Guide
**PromQL Percentiles, Label Matching & Saturation (`histogram_quantile`, `on`/`ignoring`/`group_left`, USE Saturation, Recording Rules)**

---

## 1. Directory Structure
```text
day4-promql-adv/
├── faultctl.sh                          # Fault toggle script (Cue C1 ON, Cue C2 OFF, status)
├── mock_easytravel.py                   # Exposes counters + duration histograms (le="0.25" .. "+Inf")
├── prometheus.yml                       # 5s scrape config + /etc/prometheus/rules/*.yml
├── setup_lab5.sh                        # Starts read-only Prometheus, node-exporter (textfile), easytravel-mock
├── rules/
│   └── easytravel-recording.yml         # 4 recording rules in group easytravel-recording
└── textfile/
    └── easytravel_service_info.prom     # Info metric mapping service -> team, tier
```

---

## 2. Deployment & Pre-Lab Check
1. Extract this archive and make the scripts executable:
   ```bash
   chmod +x day4-promql-adv/faultctl.sh day4-promql-adv/mock_easytravel.py day4-promql-adv/setup_lab5.sh
   ```
2. Start the Lab 5 stack:
   ```bash
   ./day4-promql-adv/setup_lab5.sh
   ```
3. Open the read-only Prometheus web UI at `http://<ec2-public-ip>:9090`:
   * **Graph tab:** Query `easytravel_service_info` (**Table** tab) and verify two series (`easytravel-frontend` → `team="web-platform"`, `easytravel-backend` → `team="payments"`, both `tier="1"`, value `1`).
   * **Status → Rules:** Confirm group `easytravel-recording` displays all 4 rules with state `OK`.

---

## 3. Instructor Cue Commands
* **Cue C1 (Start of Task 2 — `CreditCardCheckError500 ON`):**
  ```bash
  ./day4-promql-adv/faultctl.sh on
  ```
  *Keep the fault ON through Task 2 and Task 3.*
* **Cue C2 (End of Task 3 — `CreditCardCheckError500 OFF`):**
  ```bash
  ./day4-promql-adv/faultctl.sh off
  ```
