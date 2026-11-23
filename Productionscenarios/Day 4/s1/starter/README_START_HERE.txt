TEL-D4-401  Slow-Transaction Report for the Ops Review
======================================================
GOAL
  Find the slowest transactions of ShopNow-Production by p95 latency (not the
  average), and record the queries and your findings in the evidence file.

START
  ./validation_script.sh start        (Windows: .\validation_script.ps1 start)
  This starts a local simulator (:8095) and Prometheus (:9090). Wait 5-10
  minutes so that Prometheus has data before you run PromQL.

WHERE TO WORK
  * New Relic (NRQL Query builder, app ShopNow-Production): use the SHARED
    account that your instructor gives you. Do not create your own account.
  * Prometheus http://localhost:9090 : the same data as PromQL, for the
    cross-check. Metric: http_request_duration_seconds_bucket

EVIDENCE
  Fill every <<FILL_...>> in starter/evidence/evidence_D4_1.md
  (slowest transaction + p95, 4 query blocks, RCA, recommendation).

CHECK
  ./validation_script.sh check

RESET (deletes your work)
  ./validation_script.sh reset --yes

No real credentials are used. Never paste licence keys or tokens in evidence.
