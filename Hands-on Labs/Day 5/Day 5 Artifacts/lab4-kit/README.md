# Day 5 Lab 4 — Dashboard Design kit (Docker)

Self-contained: ShopSim (fake shop metrics), Prometheus 3.5, Grafana 12 and a tiny runbook web server. No other lab is needed.

Requirements: Docker with Compose v2, curl, jq, python3 (Linux, macOS, or Windows with WSL2). Internet access once, to pull the images.

```
cd day5-lab4
./scripts/setup.sh        # starts everything, waits until healthy, runs verify.sh (about 2 minutes first time)
./scripts/verify.sh       # re-check at any time
./scripts/fault.sh db-pool   # (or payment-slow | none) — switch the simulated fault
./scripts/reset.sh        # stop and remove containers and volumes (clean start next time)
```

| URL | What |
|---|---|
| http://localhost:3000 | Grafana (user `admin`, password = `GRAFANA_PASSWORD` in `.env` — a placeholder, change it) |
| http://localhost:9090 | Prometheus |
| http://localhost:9095 | Runbook pages (RB-CHK-002) |

Ports bind to 127.0.0.1 only. To share the stack on a lab network set `BIND=0.0.0.0` in `.env` and change the password first.

`work/` holds the helper scripts and dashboard JSON of the guide (`dashboards.py`, `golden-signals.json`, `executive.json`).

Not verified in the authoring environment (no Docker there): image tags, `docker compose` output, ports on your host. Run `./scripts/setup.sh` once before class.
