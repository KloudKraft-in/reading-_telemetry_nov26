TEL-D4-403  Latency Percentile and Service Variable Are Wrong
=============================================================
GOAL
  Fix the "ShopNow SRE Dashboard" in Grafana. Three defects exist:
    1. p95 latency panel is flat (it ignores time: no rate()).
    2. Error-rate panel is not a percentage ratio of 5xx to all requests.
    3. The $service variable regex truncates names, so selecting a service
       gives "No Data".

START
  ./validation_script.sh start        (Windows: .\validation_script.ps1 start)
  Starts the simulator, Prometheus and Grafana and imports the broken
  dashboard. Let it run 5-10 minutes so rate() has data.

WHERE TO WORK
  Grafana http://localhost:3000  user admin / password from starter/kit/.env
  Dashboards -> ShopNow SRE Dashboard. Edit panels and the variable
  (Dashboard settings -> Variables -> service). SAVE the dashboard.
  Prometheus http://localhost:9090 to test queries.

  Hint: variable regex - the first capture group becomes the value.
  Metrics: http_request_duration_seconds_bucket, http_requests_total{status}

EVIDENCE
  Fill starter/evidence/evidence_D4_3.json

CHECK
  ./validation_script.sh check

RESET (deletes your work)
  ./validation_script.sh reset --yes
