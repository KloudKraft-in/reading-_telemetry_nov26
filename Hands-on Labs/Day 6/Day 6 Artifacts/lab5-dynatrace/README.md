# Day 6 Lab 5 (Dynatrace) — artifacts

| File | Use |
|---|---|
| `dynatrace-import.ndjson` | Instructor only: incident logs to ingest once into the tenant (fields timestamp, loglevel, content, service.name, trace_id). Uses an ingest token that only the instructor holds; no token is stored here. |
| `q.py` | Offline fallback (python3 only): metrics, traces, events and logs with identical answers. |
| `data/` | Synthetic incident data (metrics.csv, traces.json, events.log, logs). |
| `dql-queries.txt` | The DQL queries of the lab (field names unverified in a tenant). |

Cost: depends on the Dynatrace tenant (trial or sandbox supplied by the instructor). Clean-up: remove the ingested logs and revoke the ingest token after class.
