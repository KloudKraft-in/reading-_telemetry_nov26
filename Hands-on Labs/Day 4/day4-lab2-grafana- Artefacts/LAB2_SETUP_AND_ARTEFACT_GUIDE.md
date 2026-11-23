# Day 4 Lab 2 — Candidate Environment Setup & Artefact Guide

## 1. Unified Folder Structure (`day4-grafana/`)

All starter files (both the unmodified baseline files and the updated Lab 2 SOP scripts/configs) are packaged together inside a single ready-to-deploy directory: **`day4-grafana/`**.

```text
day4-grafana/
├── dashboards/
│   └── easytravel-overview.json          # Unchanged starter baseline dashboard (Tasks 1–4 left unsolved)
├── provisioning/
│   ├── dashboards/
│   │   └── dashboards.yml                # Unchanged read-only folder provisioning ("easyTravel (shared)")
│   └── datasources/
│       └── datasources.yml               # Updated Prometheus-only default data source config
├── prometheus.yml                        # Unchanged Prometheus scrape config (scrapes easytravel-mock:8000)
├── mock_easytravel.py                    # Updated metric generator supporting manual Cue C1/C2 + auto fallback
├── setup_lab.sh                          # Added one-command Ubuntu setup & container launcher
├── create_grafana_seats.sh               # Added script to provision empty candidate folder u01 (or u01..u40)
└── faultctl.sh                           # Added Cue C1/C2 fault controller (on / off / auto / status)
```

---

## 2. Purpose of Every File Provided

### Unmodified Baseline Files (Kept Identical to Original Starter)
1. **`dashboards/easytravel-overview.json`**
   * **Purpose:** The read-only starter dashboard (`uid: easytravel-overview`, `title: easyTravel Overview`) with the 6 initial panels and `env`/`route` variables. Tasks 1–4 are intentionally left undone so candidates build `u01_easyTravel_Dev` themselves.
2. **`provisioning/dashboards/dashboards.yml`**
   * **Purpose:** Provisions `/var/lib/grafana/dashboards` into **`easyTravel (shared)`** as read-only (`editable: false`, `disableDeletion: true`) so candidates must use *Save as copy*.
3. **`prometheus.yml`**
   * **Purpose:** Configures Prometheus (`scrape_interval: 5s`) to scrape itself (`localhost:9090`) and `easytravel-mock:8000`.

### Updated & Added Lab 2 SOP Files
4. **`provisioning/datasources/datasources.yml`** *(Updated)*
   * **Purpose:** Provisions `Prometheus` (`uid: prometheus`, `url: http://prometheus:9090`) as the default data source and removes the unused Jaeger entry so there are no broken data source connections.
5. **`mock_easytravel.py`** *(Updated)*
   * **Purpose:** Python HTTP metrics server on port `8000` (`/metrics`) emitting `http_server_requests_total` and `http_server_request_duration_seconds_bucket` for `env="cohort"` (`easytravel-frontend` and `easytravel-backend`). Supports both manual Cue C1/C2 toggling via `faultctl.sh` and an automatic 3-minute fault spike fallback.
6. **`setup_lab.sh`** *(Added)*
   * **Purpose:** One-command Ubuntu launch script that creates the `obs-net` Docker network, starts `easytravel-mock`, `prometheus`, and `grafana`, and provisions the candidate's empty `u01` folder.
7. **`create_grafana_seats.sh`** *(Added)*
   * **Purpose:** Calls the Grafana HTTP API (`POST /api/folders`) to pre-create candidate seat folders (`u01`, or `u01`..`u40`) required before starting Task 1.
8. **`faultctl.sh`** *(Added)*
   * **Purpose:** Instructor/evaluator fault switch (`./faultctl.sh on` for Cue C1 `CreditCardCheckError500 ON`, `./faultctl.sh off` for Cue C2 `OFF`, plus `auto` and `status`).

---

## 3. How to Start Docker & Run the Lab on Ubuntu Terminal

### Step 1: Start and Enable Docker
```bash
sudo systemctl enable --now docker
sudo usermod -aG docker "$USER"
docker --version
```
*(If you just added your user to the `docker` group, run `newgrp docker` or open a new terminal session.)*

### Step 2: Extract the ZIP and Run `setup_lab.sh`
```bash
unzip day4-grafana-lab2-unified.zip -d ~/lab2
cd ~/lab2/day4-grafana
chmod +x setup_lab.sh create_grafana_seats.sh faultctl.sh
./setup_lab.sh
```

### Step 3: Manual Container Commands (If Starting Containers Step-by-Step)
```bash
cd ~/lab2/day4-grafana

# 1. Create the shared Docker network
docker network create obs-net

# 2. Run the easyTravel metrics exporter (port 8000 on obs-net)
docker run -d --name easytravel-mock --network obs-net   -v "$PWD/mock_easytravel.py:/app/mock_easytravel.py:ro"   python:3.11-slim python /app/mock_easytravel.py

# 3. Run Prometheus (port 9090)
docker run -d --name prometheus --network obs-net -p 9090:9090   -v "$PWD/prometheus.yml:/etc/prometheus/prometheus.yml:ro"   prom/prometheus:latest

# 4. Run Grafana (port 3000, login: admin / admin)
docker run -d --name grafana --network obs-net -p 3000:3000   -e GF_SECURITY_ADMIN_USER=admin   -e GF_SECURITY_ADMIN_PASSWORD=admin   -v "$PWD/provisioning/datasources:/etc/grafana/provisioning/datasources:ro"   -v "$PWD/provisioning/dashboards:/etc/grafana/provisioning/dashboards:ro"   -v "$PWD/dashboards:/var/lib/grafana/dashboards:ro"   grafana/grafana:latest

# 5. Provision empty candidate folder u01
./create_grafana_seats.sh http://localhost:3000 admin:admin 1
```

### Step 4: Verify Readiness Before Candidate Handoff
```bash
# Confirm all 3 containers are running
docker ps --format "table {{.Names}}	{{.Status}}	{{.Ports}}"

# Confirm both Prometheus targets report "health":"up"
curl -s http://localhost:9090/api/v1/targets | grep -o '"health":"[^"]*"'
```
Open **`http://<VM_PUBLIC_IP>:3000`** (or `http://localhost:3000`), sign in with **`admin` / `admin`**, and verify that **`easyTravel (shared) → easyTravel Overview`** displays live data and folder **`u01`** exists and is empty.

### Step 5: Control Fault Cues C1 & C2 During Task 2 (Optional)
```bash
cd ~/lab2/day4-grafana

# Cue C1: Turn CreditCardCheckError500 ON (/checkout 5xx errors spike)
./faultctl.sh on

# Cue C2: Turn CreditCardCheckError500 OFF (/checkout 5xx errors return to 0)
./faultctl.sh off

# Check status or revert to automatic 3-minute cycle
./faultctl.sh status
./faultctl.sh auto
```

### Step 6: Restart Containers After a VM Stop/Reboot
```bash
docker start easytravel-mock prometheus grafana
```
