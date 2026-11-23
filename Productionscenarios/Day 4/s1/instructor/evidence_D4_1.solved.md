# Incident Evidence: TEL-D4-401 (Slow-Transaction Report for the Ops Review)

- **Participant Name:** Sample Learner
- **Date & Time:** now
- **Ticket ID:** `TEL-D4-401`
- **Course Outcome:** `CO-10`
- **Platform:** Vendor SaaS (New Relic NRQL) & Prometheus

## 1. Problem Identification & Initial Observations
- **Observed Failure:** APM overview shows a fine average
- **Culprit Service / Host / Component:** CheckoutController#processPayment
- **Slowest transaction and p95 (name, seconds):** CheckoutController#processPayment 4.2 s

## 2. Diagnostic Query & Telemetry Evidence
NRQL 1 - top-5 ranking by p95 (with average and max):
```text
SELECT percentile(duration, 95), average(duration) FROM Transaction WHERE appName = 'ShopNow-Production' FACET name LIMIT 5
```
NRQL 2 - trend of the slowest transaction (TIMESERIES):
```text
SELECT percentile(duration, 95) FROM Transaction WHERE appName='ShopNow-Production' TIMESERIES
```
NRQL 3 - which errors hit the slowest transactions (TransactionError):
```text
SELECT count(*) FROM TransactionError WHERE appName='ShopNow-Production' FACET error.class
```
PromQL cross-check (and the top rows of its result):
```text
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[1d])) by (le, handler))
```

## 3. Root Cause Analysis (RCA)
The overview shows the average, and the average hides the slow tail: ten percent of requests are slow, so the percentile (p95) exposes it while the mean looks healthy.

## 4. Verification & Solution Details
- **Fixed Metric / Rule / Parameter:** percentile 95
- **Observed Result After Fix:** ranked first
- **Recommended Action Item:** Add p95 alert on processPayment and profile the gateway call
