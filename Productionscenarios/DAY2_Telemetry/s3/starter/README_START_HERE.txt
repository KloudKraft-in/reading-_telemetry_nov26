TEL-D2-203: Grafana Shows Latency: Write the Escalation
===============================================================================
BROWSER-ONLY, SINGLE-PLATFORM SCENARIO (Grafana). No terminal, no Docker, no local ports.

HOW TO START:
1. Your instructor starts the incident and announces the start time (UTC/IST).
   Write it in starter/evidence/evidence_D2_3.md (copy provided as Word/Google Doc).
2. Open Grafana. Set the time range to Last 2 hours.
3. Shared environment rules: read-only; never close/mute/edit shared problems,
   monitors, dashboards or alert rules. Name anything you create with u<seat>_.

YOUR MISSION:
1. Grafana (URL from your instructor): open the checkout RED dashboard, latency panel in View mode for the incident window; copy the URL (must contain viewPanel=).
2. Explore (Prometheus data source, read only): histogram_quantile(0.95, sum by (le) (rate(http_request_duration_seconds_bucket[5m]))); note the p95 and when it rose.
3. Explore: sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m])); note the error ratio.
4. Alerting > Alert rules: view (do not edit) the related rule and its state.
5. Write one causal hypothesis, severity, a 3-sentence summary, escalation target, ask and next update.

SUBMISSION & EVIDENCE:
1. Fill every <<FILL_...>> field in starter/evidence/evidence_D2_3.md
   (paste exact queries / screen paths / links; add screenshots).
2. Call your instructor for sign-off against the 5 rules in the Participant Guide.
===============================================================================
