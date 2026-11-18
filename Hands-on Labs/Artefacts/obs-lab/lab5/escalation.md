# Escalation — Payment Gateway Degradation Affecting Checkout

| Field | Value |
|---|---|
| Time (IST) | 15:20 |
| Severity | SEV1 — Checkout journey failing or slow for many users; payment is a Tier-1 service. |
| Affected service(s) | payment (tier 1), checkout |
| Customer impact | Multiple users experiencing checkout errors and slow payment processing. |
| Escalated to | payments-oncall → next: psp-vendor-support |
| Runbook | RB-PAY-004 |

## Evidence (one line per platform, with link or query)

- Metrics: Datadog — 42 checkout errors in 5 minutes.
- Traces: New Relic — `/api/checkout` AJAX calls have p95 latency of 3.1 seconds.
- Logs: Dynatrace — Payment response time degradation associated with the external PSP gateway call.
- Events: AWS — `obs-lab-psp-latency` alarm is in ALARM; PSP vendor status reports degraded performance.

## Ask

Please investigate the PSP gateway degradation, confirm the vendor-side issue and initiate failover if available.

## Next update

15:30 IST via the incident communication channel.

