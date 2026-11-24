# Day 5 Lab 5 — Alert Hygiene kit (Docker)

Self-contained: ShopSim, Prometheus 3.5, Alertmanager 0.28 and a webhook sink that prints every notification. No other lab is needed.

Requirements: Docker with Compose v2, curl, jq, python3 (Linux, macOS, or Windows with WSL2). Internet access once, to pull the images.

```
cd day5-lab5
./scripts/setup.sh        # starts the stack and runs verify.sh
./scripts/verify.sh
./scripts/fault.sh db-pool   # (or payment-slow | none)
./scripts/reset.sh
```

| URL | What |
|---|---|
| http://localhost:9090 | Prometheus (rules, alerts) |
| http://localhost:9093 | Alertmanager |
| http://localhost:9095 | Runbook pages (RB-CHK-002, RB-DB-003) |

`work/` — learner files: `noisy-rules.yml`, `alert-history.csv` (+ generator), `alert-noise.py`, starting Alertmanager config.
`solutions/` — instructor only: tuned rules, promtool tests, Alertmanager config, RB-WEB-004 runbook. Do not hand out before Task 4.

Not verified in the authoring environment: promtool/amtool/Docker output and image tags. Run `./scripts/setup.sh` and the promtool test once before class.
