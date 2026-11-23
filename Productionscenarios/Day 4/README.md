# Day 4 - Reading Telemetry & Observability (v2.0)

Learners run everything locally with Docker Compose. Each scenario is independent (own compose project, own evidence).

| Scenario | Ticket | Stack | Ports |
|---|---|---|---|
| s1 | TEL-D4-401 | Simulator + Prometheus, plus New Relic (shared instructor account) | 8095, 9090 |
| s2 | TEL-D4-402 | Loki + Promtail + Grafana + log generator | 3000, 3100 |
| s3 | TEL-D4-403 | Simulator + Prometheus + Grafana | 3000, 8095, 9090 |

Run ONE scenario at a time (s2 and s3 share port 3000; `reset --yes` frees it).
Each scenario: `./validation_script.sh start | check | reset --yes` (Windows: `.\validation_script.ps1 ...`).
Requires Docker with Compose v2 and Python 3. No real credentials; the Grafana password is a local placeholder (`starter/kit/.env`).
