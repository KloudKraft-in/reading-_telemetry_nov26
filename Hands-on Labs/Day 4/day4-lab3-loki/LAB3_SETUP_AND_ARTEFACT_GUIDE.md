# Day 4 Lab 3 — Loki LogQL Setup & Artefact Guide

## 1. Unified Directory Structure (`day4-loki/`)

```text
day4-loki/
├── loki/
│   ├── docker-compose.yml            # Starts Grafana Loki 3.1.1 on obs-net (port 3100)
│   └── et_json_log_feed.py           # Pushes structured easyTravel JSON logs to Loki
├── provisioning/
│   └── datasources/
│       └── loki.yml                  # Auto-provisions Loki data source in Grafana (http://loki:3100)
├── faultctl.sh                       # Shared Cue C1/C2 switch (updates both Lab 2 metrics & Lab 3 logs)
└── setup_lab3.sh                     # One-command Ubuntu launcher & readiness check
```

## 2. Purpose of Every Artefact

1. **`loki/docker-compose.yml`** — Launches `grafana/loki:3.1.1` on port `3100` attached to `obs-net` (`http://loki:3100`).
2. **`loki/et_json_log_feed.py`** — Generates structured easyTravel JSON logs with all 10 SOP keys (`ts`, `level`, `service`, `message`, `route`, `http_status`, `duration_ms`, `exception`, `trace_id`, `span_id`) under labels `service_name` and `deployment_environment="cohort"`.
3. **`provisioning/datasources/loki.yml`** — Auto-provisions the **Loki** data source (`uid: loki`, `url: http://loki:3100`) in Grafana.
4. **`faultctl.sh`** — Shared Cue C1/C2 switch (`./faultctl.sh on` / `./faultctl.sh off` / `./faultctl.sh status`) that toggles `~/obs-lab/control/fault.flag` and `easytravel-mock`.
5. **`setup_lab3.sh`** — One-command Ubuntu setup script that starts Loki, wires the Grafana data source, starts the log shipper, and verifies readiness.

## 3. Ubuntu Terminal Launch & Fault Cues

```bash
unzip day4-loki-lab3.zip -d ~/
cd ~/day4-loki
chmod +x setup_lab3.sh faultctl.sh loki/et_json_log_feed.py
./setup_lab3.sh

# Cue C1 (Task 1 Step 2)
./faultctl.sh on

# Cue C2 (End of Task 3)
./faultctl.sh off
```
