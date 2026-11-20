# Day 1 — Evidence Entry Examples and Pass Criteria

Use this file together with the Participant Guide. Complete the evidence file **after** starting the scenario and collecting evidence from the running tools. The validator checks both evidence text and live services; evidence text alone is not enough.

> Important: S1 and S3 examples below are ready-to-use evidence wording. Replace participant/date details. S2 must use the Trace ID from the participant's own Jaeger trace. Never copy the illustrative ID below.

---

## S1 — TEL-D1-101: Checkout latency / RED dashboard

**File:** `s1/starter/evidence/evidence_D1_1.json`

Replace the complete file content with valid JSON. The following example contains all five evidence keywords required by the evidence validator. Keep the PromQL expressions intact.

```json
{
  "ticket": "TEL-D1-101",
  "participant": "Your Name",
  "date": "2026-11-19 14:30 IST",
  "courseOutcome": "CO-01",
  "incidentSummary": {
    "observedDefect": "The dashboard looked green because the mean latency hid the slow checkout tail; customers experienced checkout delays and timeouts above 4.5 seconds.",
    "rootCauseComponent": "checkout-service payment duration distribution and the misleading mean latency panel."
  },
  "telemetryFixes": {
    "primaryQueryOrFix": "histogram_quantile(0.95, sum by (le) (rate(payment_duration_seconds_bucket[5m])))",
    "secondaryQueryOrThreshold": "100 * sum(rate(http_requests_total{service=\"checkout-service\",status=~\"5..\"}[5m])) / sum(rate(http_requests_total{service=\"checkout-service\"}[5m]))"
  },
  "verification": {
    "verifiedOnPlatform": true,
    "mitigationRecommendation": "Saved the RED Checkout Dashboard with the p95 histogram_quantile query and the 5xx error-rate panel. Verified the shopnow-checkout Prometheus target is UP. Investigate the slow payment cohort and downstream dependency latency."
  }
}
```

**S1 evidence checks:** valid JSON; no `<<FILL_...>>` placeholders; evidence contains `histogram_quantile`, `payment_duration_seconds_bucket`, `rate(`, `http_requests_total`, and `status=~`.

**S1 live checks (must also pass):**
1. The lab is running and checkout, Prometheus, and Grafana health endpoints respond.
2. In Grafana, save the **RED Checkout Dashboard** after editing it.
3. The Payment Duration panel query contains `histogram_quantile`, `payment_duration_seconds_bucket`, and `rate(`.
4. A second panel contains `http_requests_total` and `status=~"5.."`.

Run from `~/day1/s1`:
```bash
./validation_script.sh check
```
Expected: **7/7** checks. If the evidence checks pass but one of the last two checks fails, reopen Grafana, correct the panel, click **Apply**, then **Save dashboard**.

---

## S2 — TEL-D1-102: Jaeger trace and Loki log correlation

**File:** `s2/starter/evidence/evidence_D1_2.md`

The validator requires a real 32-character hexadecimal Trace ID, and the exact same ID in:
- a full Jaeger URL beginning `http://localhost:16686/trace/`
- the Loki query `{app="inventory-service"} |= "TRACE_ID"`

**Do not paste the sample ID as your own.** In Jaeger, open the failed trace, copy the ID from the browser URL after `/trace/`, and replace `PUT_YOUR_ACTUAL_TRACE_ID_HERE` everywhere below.

~~~~markdown
# Incident Evidence: TEL-D1-102 — Orders Fail for One Product: Follow the Trace

- **Participant Name:** Your Name
- **Date & Time (local):** 2026-11-19 14:30 IST
- **Ticket ID:** `TEL-D1-102`
- **Course Outcome:** `CO-02`
- **Platform:** Self-Hosted (Jaeger & Loki)

## 1. Problem Identification & Initial Observations
- **Observed customer symptom:** Checkout for promotional SKU PROD-7729 fails; customer-facing checkout returns HTTP 500.
- **Culprit service / component:** inventory-service reservation operation.
- **Affected SKU:** PROD-7729

## 2. Jaeger Trace Evidence
- **Trace ID:** `PUT_YOUR_ACTUAL_TRACE_ID_HERE`
- **Jaeger Trace URL:** `http://localhost:16686/trace/PUT_YOUR_ACTUAL_TRACE_ID_HERE`
- **Root operation:** frontend: POST /api/checkout
- **Failing child operation:** inventory.reserveStock
- **Observed failing span duration (ms):** Record the duration shown in your trace, for example 18
- **Inventory response status:** HTTP 409 Conflict
- **Checkout response status:** HTTP 500
- **Error tag / exception:** error=true; error.type=StockReservationException

## 3. Loki Log Evidence
```logql
{app="inventory-service"} |= "PUT_YOUR_ACTUAL_TRACE_ID_HERE"
```
- **Log message / exception text:** StockReservationException; stock reservation rejected because the warehouse bin is locked by the cycle-count audit.
- **Trace ID in log line matches Jaeger:** Yes

## 4. Root Cause Analysis (RCA)
The inventory reservation failed because the warehouse bin for SKU PROD-7729 was locked during a cycle-count audit. inventory-service returned HTTP 409 Conflict with StockReservationException. checkout-service surfaced the dependency failure to the customer as HTTP 500. The same Trace ID was used to correlate the Jaeger trace and Loki log.

## 5. Verification & Recommended Remediation
- **What did you verify in Jaeger?** The frontend checkout trace, failing inventory.reserveStock span, SKU PROD-7729, error tag, and HTTP 409 inventory failure.
- **What did you verify in Loki?** The inventory-service log for the same Trace ID contains StockReservationException and the cycle-count audit lock.
- **Was the same Trace ID used in both tools?** Yes
- **Recommended operational action:** Confirm the active cycle-count lock with warehouse operations, avoid retry storms, and retry the reservation only after the lock is released.
- **Prevention / follow-up action:** Expose a clear inventory conflict response, add lock-state visibility, and apply bounded retry/backoff only for retryable failures.

## 6. Completion
- **Validation command executed:** `./validation_script.sh check`
- **Validation result:** Record the actual command output.
- **Evidence file saved:** `starter/evidence/evidence_D1_2.md`
~~~~

The code block above is a **format example**. Replace every occurrence of `PUT_YOUR_ACTUAL_TRACE_ID_HERE` with the actual ID from the trace URL. Also replace the example span duration with the value shown in your selected trace.

**S2 evidence checks:** same runtime ID in the `Trace ID:` line, full Jaeger URL and exact Loki LogQL; `inventory.reserveStock`; `PROD-7729`; `StockReservationException`; `cycle-count audit`; both `409` and `500`.

**S2 live checks:** frontend, checkout, payment, inventory, Jaeger, Loki and Grafana must all be ready.

Run from `~/day1/s2`:
```bash
./validation_script.sh check
```
Expected: **5/5** checks.

---

## S3 — TEL-D1-103: Alert storm / PostgreSQL disk queue

**File:** `s3/starter/evidence/evidence_D1_3.json`

Replace the complete file content with valid JSON. This example includes all five evidence keywords required by the evidence validator.

```json
{
  "ticket": "TEL-D1-103",
  "participant": "Your Name",
  "date": "2026-11-19 14:30 IST",
  "courseOutcome": "CO-03",
  "incidentSummary": {
    "observedDefect": "Six alerts fired together. The primary causal alert is DatabaseQueueSaturation, corroborated by DiskIOWaitHigh; the other application alerts are downstream symptoms.",
    "rootCauseComponent": "PostgreSQL primary disk I/O saturation caused by the long-running unindexed reporting query."
  },
  "telemetryFixes": {
    "primaryQueryOrFix": "DatabaseQueueSaturation: db_disk_queue_length > 35. Corroborating alert: DiskIOWaitHigh: db_disk_io_await_milliseconds > 250.",
    "secondaryQueryOrThreshold": "PID 9182 belongs to analytics_batch / nightly-report-runner and is running a long 90-day aggregation without an index on created_at."
  },
  "verification": {
    "verifiedOnPlatform": true,
    "mitigationRecommendation": "After confirming replication health and lag, route reporting reads to the healthy PostgreSQL read replica. Review the query plan and created_at index, reschedule the batch outside peak hours, and verify primary disk queue and I/O await return to normal. Do not kill a real process; this lab endpoint is a simulator."
  }
}
```

**S3 evidence checks:** valid JSON; no placeholders; evidence contains `DatabaseQueueSaturation`, `DiskIOWaitHigh`, `9182`, `PostgreSQL`, and `replica`.

**S3 live checks:** simulator, Prometheus, Alertmanager and Grafana must be ready. Allow about 60 seconds for alert rules to move to Firing.

Run from `~/day1/s3`:
```bash
./validation_script.sh check
```
Expected: **5/5** checks.

---

## Final validation sequence

Run only one scenario at a time. After reviewing and saving evidence, run its `check` command. Preserve the evidence file or its timestamped backup before running `reset`; reset restores the starter evidence template.

| Scenario | Evidence file | Expected validator result |
|---|---|---:|
| S1 / TEL-D1-101 | `s1/starter/evidence/evidence_D1_1.json` | 7/7 |
| S2 / TEL-D1-102 | `s2/starter/evidence/evidence_D1_2.md` | 5/5 |
| S3 / TEL-D1-103 | `s3/starter/evidence/evidence_D1_3.json` | 5/5 |

A passing evidence score does not replace the live checks. If a check fails, read the specific `[FAIL]` line, correct the evidence or UI configuration, and run `check` again.
