# Day 1 Lab Environment — Controller and Runtime Notes

Each scenario (`s1`, `s2`, `s3`) has its own Compose file, starter artifacts and pristine reset files under `lab/baseline/`. Shared simulated application code is under `shared/app/`.

## Requirements

- Docker Engine with Docker Compose v2.
- Python 3 on the host (standard library only for `shared/labctl.py`).
- `curl` for manual endpoint checks.
- Internet access on first run to pull pinned images and build the application image.
- Run one scenario at a time; the scenarios reuse host ports and some fixed container names.

## Linux preparation

From the extracted `day1/` directory:

```bash
chmod +x s1/validation_script.sh s2/validation_script.sh s3/validation_script.sh shared/labctl.py
```

## Commands

Run from the relevant scenario directory:

```bash
./validation_script.sh start
./validation_script.sh check
./validation_script.sh reset
```

PowerShell equivalent: `./validation_script.ps1 start`, `./validation_script.ps1 check`, `./validation_script.ps1 reset`.

`start` stops all Day 1 scenario projects, restores the selected scenario's baseline, validates Compose configuration, builds/starts the stack, and waits for all configured HTTP readiness endpoints. `reset` stops the selected project, removes its named volumes, and restores starter files. A modified starter file is copied to a timestamped `.bak-...` file before restore.

## Compose project names

- S1: `telemetry-d1-s1`
- S2: `telemetry-d1-s2`
- S3: `telemetry-d1-s3`

## Scenario ports

- S1: checkout 8081, Prometheus 9090, Grafana 3000.
- S2: frontend 8080, checkout 8081, payment 8082, inventory 8083, Jaeger 16686, Loki 3100, Grafana 3000.
- S3: simulator 8083, Prometheus 9090, Alertmanager 9093, Grafana 3000.

## Validation

- S1 validates the evidence file and reads the saved Grafana dashboard (`red-checkout`) to verify p95 and 5xx expressions.
- S2 validates a runtime 32-hex Trace ID and requires the same ID in the Jaeger URL and Loki query, plus the failing span, SKU, exception and audit-lock root cause. Runtime IDs are not fixed.
- S3 validates the causal alert, corroborating saturation alert, PID, database platform and read-replica mitigation in the evidence file.

All scenario checks require the scenario's relevant services to be ready. Complete evidence and save the Grafana dashboard before running `check`.
