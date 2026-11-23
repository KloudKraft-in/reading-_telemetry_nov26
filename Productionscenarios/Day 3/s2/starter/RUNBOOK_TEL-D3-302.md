# TEL-D3-302: Dynatrace Grail — Instructor Runbook (learners do not run anything)

Independent setup: needs only the easyTravel host `ip-172-30-0-220` (OneAgent) and the shared tenant. Does not need S1 or S3.

## Before class (about 30 minutes ahead)

1. Confirm OneAgent reports easyTravel and the load generator is running. In a Notebook: `fetch logs, from: now() - 10m | summarize count(), by: {dt.process.name}` returns the easyTravel processes.
2. On the EC2 host run `./validation_script.sh start` (switches `CreditCardCheckError500` ON through the config service on port 8091; if `DT_ENV_URL` and `DT_API_TOKEN` (scope `events.ingest`) are exported it also posts the deployment event "easyTravel Checkout Service v2.4.1 Rollout"). Note the UTC start time.
3. Wait 5 minutes, then check the three queries of the Instructor Guide return data (logs by process, failed spans by service, failure_count timeseries).
4. Give learners Notebook create rights and read access to logs, spans and metrics. Announce the start time.

## End of class

`./validation_script.sh reset` (fault OFF). Learners' Notebooks stay in their own space; delete leftovers only if asked.

## Not verified

Field names on your tenant (`loglevel`, `dt.process.name`, `request.is_failed`) and the metric key `dt.service.request.failure_count`. The scenario tells learners to inspect fields with `| limit 5` if a query returns nothing.
