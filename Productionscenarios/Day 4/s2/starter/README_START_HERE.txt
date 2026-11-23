TEL-D4-402  Error Panel Shows Zero During an Outage
===================================================
GOAL
  The Grafana panel "Payment Error Volume" shows 0 while payment-service is
  failing. Repair the query, set alert thresholds, and document the fix.

START
  ./validation_script.sh start        (Windows: .\validation_script.ps1 start)
  Starts Loki, Promtail, Grafana and a payment-service log generator, creates
  the outage (about 90 ERROR logs per minute) and imports the broken dashboard.
  Wait 5 minutes before verifying.

WHERE TO WORK
  Grafana http://localhost:3000  user admin / password from starter/kit/.env
  Dashboards -> Payment Dashboard -> Payment Error Volume -> Edit
  Loki (Explore, datasource Loki): logs are JSON with a "level" field.

WHAT TO DELIVER
  1. Query returns ERRORS PER MINUTE using the JSON "level" field
     (not a text match on the word "error").
  2. Thresholds: green base, Warning (yellow) at 5, Critical (red) at 20
     errors per minute.
  3. SAVE the dashboard.
  4. Fill starter/evidence/evidence_D4_2.json.

CHECK
  ./validation_script.sh check

RESET (deletes your work)
  ./validation_script.sh reset --yes

The Grafana password is a local placeholder, not a real credential.
