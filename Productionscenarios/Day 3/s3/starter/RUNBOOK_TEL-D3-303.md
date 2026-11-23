# TEL-D3-303: Datadog Monitors — Instructor Runbook (learners do not run anything)

Independent setup: needs only the Datadog organisation and the easyTravel host `ip-172-30-0-220` (Agent 7 + `dd-java-agent.jar`, `env:cohort`). Does not need S1 or S2.

## Before class (about 30 minutes ahead)

1. Confirm APM shows `easytravel-backend` with `env:cohort` and Metrics Summary lists `trace.servlet.request.errors` and `trace.servlet.request.hits`.
2. Create the shared broken monitor in the UI (Monitors > New Monitor > Metric > Source toggle) with the query in `starter/conf/datadog_monitor_broken.json`, name `[SHARED][BROKEN] easyTravel Backend Errors (TEL-D3-303)`, no notifications, tag `shared:true`. Do not fix it.
3. On the EC2 host run `./validation_script.sh start` (switches `CreditCardCheckError500` ON through the config service on port 8091). Note the UTC start time and announce it.
4. Wait 5 minutes. Confirm the broken monitor is green or No Data, and that this graph is above zero: `sum:trace.servlet.request.errors{env:cohort,service:easytravel-backend}.as_count()`.
5. Give learners Monitors Write (own monitors only) and check the monitor quota: 40 learners x 3 monitors = 120.

## End of class

`./validation_script.sh reset` (fault OFF). Remove leftover `[u..]` monitors: Manage Monitors, filter `tag:lab:d3-303`, delete composites first. Keep or delete the shared broken monitor.

## Not verified

That the metric names and tags match your org, and that monitor A crosses 5 % under the fault (traffic dependent). Tune the learner threshold in the guide if your error ratio is lower.
