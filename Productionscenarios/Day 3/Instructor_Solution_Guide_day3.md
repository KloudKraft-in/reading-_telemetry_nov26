# Reading Telemetry & Observability - Instructor Solution Guide: Day 3

## 1. What Changed and Why

| Scenario | Before | Now | Learner effort |
| :--- | :--- | :--- | :--- |
| S1 TEL-D3-301 | Splunk Free "self-hosted" with a one-line sample log and no data | **Local Docker Splunk** with a generated data set (3000 checkout + 2400 web events, last 4 h) | Docker + one start command |
| S2 TEL-D3-302 | Dynatrace Grail on a ShopNow story (`inventory-worker`, `DeadlockException`) with a Splunk parity check | **Dynatrace in the browser on the shared easyTravel host**; DQL in Notebooks; parity check against the Logs app | Browser only |
| S3 TEL-D3-303 | Datadog monitor JSON (`shopnow.checkout.duration`, p95) | **Datadog in the browser on the shared easyTravel host**; broken shared monitor, own monitors built in the UI | Browser only |

The ShopNow identifiers `inventory-worker`, `DeadlockException`, `shopnow.checkout.duration` and `env:staging`/`env:prod` are retired. S1 keeps its original story, host (`web-prod-04`), error-code format (`ERR-4011`) and queries.

### Independence

Every scenario has its own platform, setup, start/reset and sign-off.

| Scenario | Needs | Does not need |
| :--- | :--- | :--- |
| S1 | Learner machine with Docker; port 8000 | Shared servers, S2, S3 |
| S2 | Dynatrace tenant + easyTravel host with OneAgent | Datadog, Docker, S1, S3 |
| S3 | Datadog org + easyTravel host with Agent 7 and `dd-java-agent.jar` | Dynatrace, Docker, S1, S2 |

S2 and S3 use the same easyTravel host, so if you run both on the same day one fault window can serve both (start once, announce once). Run them separately if you want clean start times.

## 2. Setup (Instructor)

### S1: Learner Machines (Docker)

1. Tell learners the requirements before class: Docker + Compose v2, 4 GB free RAM, 6 GB free disk, port 8000 free.
2. **Pre-pull the image** to avoid 40 simultaneous 1 GB downloads: `docker pull splunk/splunk:9.2.1` on a local registry/cache, or let learners pull it the day before.
3. Smoke test on one machine: `./validation_script.sh start`, then `index=retail_* earliest=-4h | stats count by index` shows `retail_checkout 3000`, `retail_web 2400`.
4. Splunk Enterprise runs as a trial (60 days) and then reverts to Free; for the lab this is irrelevant.

### S2: Dynatrace (easyTravel)

1. About 30 minutes before class: confirm `fetch logs, from: now() - 10m | summarize count(), by: {dt.process.name}` returns the easyTravel processes.
2. On the EC2 host run `./validation_script.sh start` in `s2/` (fault `CreditCardCheckError500` ON; with `DT_ENV_URL` and `DT_API_TOKEN` exported it also posts the deployment event). Note the UTC time.
3. Wait 5 minutes and run the reference queries in Section 3 to confirm they return rows. Announce the start time.

### S3: Datadog (easyTravel)

1. Confirm APM shows `easytravel-backend` (`env:cohort`) and Metrics Summary lists `trace.servlet.request.errors` and `trace.servlet.request.hits`.
2. Create the shared broken monitor in the UI with the query in `s3/starter/conf/datadog_monitor_broken.json`; no notifications.
3. On the EC2 host run `./validation_script.sh start` in `s3/`. Note the UTC time.
4. Wait 5 minutes. Check the broken monitor is green or No Data, and that `sum:trace.servlet.request.errors{env:cohort,service:easytravel-backend}.as_count()` is above zero.
5. Monitor quota: 40 learners x 3 monitors = 120.

### End of class

`./validation_script.sh reset` in `s2/` and `s3/` (fault OFF). Delete leftover `[u..]` monitors (tag `lab:d3-303`, composites first). Learners run `reset` for S1 themselves.

## 3. Answer Keys and Sign-Off Checks

### S1 TEL-D3-301 (Splunk, local Docker)

| Rule | Expected answer |
| :--- | :--- |
| 1 Culprit host | `web-prod-04`, about 92 % of the errors (232 of 252) |
| 2 Regex | `rex field=_raw "status_code=(?<err_code>ERR-[0-9]{4})"` |
| 3 Pattern | `ERR-[0-9]{4}`; codes found: ERR-4011 (150), ERR-4012 (68), ERR-5003 (34) |
| 4 Timechart | `timechart span=15m count by err_code`: errors start about 2 hours ago, none before the release |
| 5 Sessions | `transaction session_id maxspan=30m \| where duration > 10`: 232 sessions, all on `web-prod-04` |

Reference queries:

```text
(index=retail_web OR index=retail_checkout) earliest=-4h | stats count by host, sourcetype | sort -count
index=retail_checkout earliest=-4h | rex field=_raw "status_code=(?<err_code>ERR-[0-9]{4})" | stats count by host, err_code
index=retail_checkout host=web-prod-04 earliest=-4h | rex field=_raw "status_code=(?<err_code>ERR-[0-9]{4})" | timechart span=15m count by err_code
index=retail_checkout earliest=-4h | transaction session_id maxspan=30m | where duration > 10 | table session_id, duration, eventcount
```

The counts above come from the seeded generator (`gen_retail_logs.py`, run locally and verified: 3000 events, 252 errors = 8.4 %, 92.1 % on `web-prod-04`). The 252 includes 20 errors on other hosts (ERR-5003 x12, ERR-4012 x8 with message `upstream timeout`). Event times are relative to the start time, so `earliest=-4h` always works; re-running `start` regenerates the data.

### S2 TEL-D3-302 (Dynatrace)

| Rule | Instructor checks in browser | Expected answer |
| :--- | :--- | :--- |
| 1 Culprit | Top row of the summary | The easyTravel backend process has the highest `ErrorCount` (name as shown on your tenant) |
| 2 Method | Pipeline uses `fetch logs`, filter, `summarize ... by: {dt.process.name, error_type}` | Matches the reference below |
| 3 Evidence | Dominant error type | `CreditCardCheckError500` with `ErrorCount` shown |
| 4 Second view | Failed spans / timeseries point to the same service; Logs-app count close to the Notebook count | Same service; counts within a few lines (timing) |
| 5 Complete | No `<<FILL_...>>`; next action named | Check the credit-card check in the backend / payment path |

Reference queries:

```text
fetch logs, from: now() - 2h
| filter loglevel == "ERROR"
| fieldsAdd error_type = if(contains(content, "CreditCardCheckError500"), "CreditCardCheckError500", else: "other")
| summarize ErrorCount = count(), by: {dt.process.name, error_type}
| sort ErrorCount desc

fetch spans, from: now() - 2h | filter request.is_failed == true | summarize failed = count(), by: {service.name} | sort failed desc
timeseries failures = sum(dt.service.request.failure_count), by: {dt.entity.service}, from: now() - 2h | fieldsAdd service = entityName(dt.entity.service)
```

### S3 TEL-D3-303 (Datadog)

| Rule | Instructor checks | Expected answer |
| :--- | :--- | :--- |
| 1 Defects named | Broken monitor read | (1) `env:staging` instead of `env:cohort`; (2) `avg` of a raw count with a fixed threshold of 50 instead of an error ratio |
| 2 Corrected monitor A | Saved monitor | `sum(last_5m):sum:trace.servlet.request.errors{env:cohort,service:easytravel-backend}.as_count() / sum:trace.servlet.request.hits{env:cohort,service:easytravel-backend}.as_count() * 100 > 5` |
| 3 Evidence | Query and metric | `trace.servlet.request.errors`, `sum(last_5m)`, thresholds 5 / warning 2 |
| 4 Second view | Metrics Explorer | Broken query shows no data; same query with `env:cohort` shows data |
| 5 Complete | Monitors B and composite | B: log count of `CreditCardCheckError500` above 10 in 5 minutes; composite `a && b`; all three states recorded while the fault is on (A, B and the composite in Alert) |

## 4. Validation Checklist per Learner (about 3 minutes)

- S1: learner shows the `check` output (5 of 5) and one live query in Splunk.
- S2 and S3: open the evidence beside the platform; tick each rule only after seeing it on screen; spot check one query live.
- Record the result in the class tracker (seat, scenario, rules passed). Pass mark 5 of 5; 4 of 5 = retry once.

## 5. Instructor-Only Runbook (Replaces Provider Scripts)

| Task | Where | Notes |
| :--- | :--- | :--- |
| Start fault (S2/S3) | `s2/validation_script.sh start` or `s3/validation_script.sh start` on the EC2 host | Calls the easyTravel config service (`setPluginEnabled`, `CreditCardCheckError500`, port 8091). `.ps1` equivalents exist |
| Deployment event (S2) | Same script, needs `DT_ENV_URL` and `DT_API_TOKEN` (scope `events.ingest`) | Optional; skipped if variables are not set. Keep tokens out of guides |
| Stop fault | `./validation_script.sh reset` | End of class |
| S1 data | `s1/starter/setup/gen_retail_logs.py` | Run by the learner's start script |

## 6. Common Learner Mistakes

| Mistake | Fix |
| :--- | :--- |
| S1: no results for `earliest=-4h` | Wait 1 minute after `start`; the load runs in the background |
| S1: `rex` run on a field instead of `_raw` | Use `rex field=_raw` |
| S1: container keeps restarting | Give Docker 4 GB RAM; check `docker logs tel-d3-301-splunk` |
| S2: filter after `summarize` returns nothing | Filter first, then summarize |
| S2: `loglevel` returns no rows | Run `fetch logs, from: now() - 2h \| limit 5` and use the field you see |
| S3: editing the shared monitor | Read only; create your own `[u<seat>]` monitors |
| S3: composite refuses to delete a component | Delete the composite first |

## 7. Not Verified

- S1: the Docker compose file and the Splunk CLI calls (`add index`, `add oneshot`) were not run here (no Docker). The generator and the self-check were run. The image tag `splunk/splunk:9.2.1` and the environment variable `SPLUNK_GENERAL_TERMS` may need adjusting for the version you use.
- S2 and S3: field names (`loglevel`, `dt.process.name`, `request.is_failed`), the metric `dt.service.request.failure_count`, the Datadog metrics `trace.servlet.request.*`, and the easyTravel config-service port are taken from the Day 2 and Day 3 lab material, not tested on your tenants.
- S3: whether the error ratio crosses 5 % under the fault depends on traffic. Test once, and lower the threshold in the guide if needed.
- The Windows `.ps1` files were written but not run.
