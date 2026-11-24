# Day 5 Lab 3 (Azure) — artifacts

| File | Use |
|---|---|
| `appinsights-gen.py` | Run in Azure Cloud Shell (Bash). Sends 1 800 requests, 3 046 dependencies and 52 exceptions (fixed seed 5150) to YOUR Application Insights resource through the v2 track endpoint. `--dry-run` writes telemetry.jsonl instead of sending. |
| `kql-queries.kql` | Every KQL query of Tasks 1-4 and both extensions. |
| `appinsights-lab.arm.json` | Instructor option: pre-creates the workspace and the Application Insights resource of one seat (portal: Deploy a custom template). |

Expected values (same for every learner; only the clock times differ): requests 1 800 · dependencies 3 046 · exceptions 52.
Cost: about 4 MB of telemetry per learner — inside the 5 GB per month free allowance of Log Analytics. Clean-up: delete the resource group (or the two resources).
