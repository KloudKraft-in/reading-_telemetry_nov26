# Incident Evidence: TEL-D4-401 (Slow-Transaction Report for the Ops Review)

- **Participant Name:** <<FILL_YOUR_NAME>>
- **Date & Time:** <<FILL_TIMESTAMP>>
- **Ticket ID:** `TEL-D4-401`
- **Course Outcome:** `CO-10`
- **Platform:** Vendor SaaS (New Relic NRQL) & Prometheus

## 1. Problem Identification & Initial Observations
- **Observed Failure:** <<FILL_OBSERVED_FAILURE_SUMMARY>>
- **Culprit Service / Host / Component:** <<FILL_CULPRIT_COMPONENT>>
- **Slowest transaction and p95 (name, seconds):** <<FILL_TRANSACTION_AND_P95_SECONDS>>

## 2. Diagnostic Query & Telemetry Evidence
NRQL 1 - top-5 ranking by p95 (with average and max):
```text
<<PASTE_NRQL_RANKING_QUERY_HERE>>
```
NRQL 2 - trend of the slowest transaction (TIMESERIES):
```text
<<PASTE_NRQL_TIMESERIES_QUERY_HERE>>
```
NRQL 3 - which errors hit the slowest transactions (TransactionError):
```text
<<PASTE_NRQL_ERROR_QUERY_HERE>>
```
PromQL cross-check (and the top rows of its result):
```text
<<PASTE_PROMQL_QUERY_AND_RESULT_HERE>>
```

## 3. Root Cause Analysis (RCA)
<<EXPLAIN_WHY_THE_DEFAULT_OVERVIEW_HIDES_THE_SLOW_TRANSACTION_AVERAGE_VS_PERCENTILE>>

## 4. Verification & Solution Details
- **Fixed Metric / Rule / Parameter:** <<FILL_FIXED_PARAMETERS>>
- **Observed Result After Fix:** <<FILL_VERIFICATION_RESULT>>
- **Recommended Action Item:** <<FILL_RECOMMENDED_REMEDIATION>>
