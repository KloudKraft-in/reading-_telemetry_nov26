# Incident Evidence: TEL-D1-102 — Orders Fail for One Product: Follow the Trace

Complete every field using evidence from your own run. Do not copy the sample Trace ID from the instructor reference.

- **Participant Name:**
- **Date & Time (local):**
- **Ticket ID:** `TEL-D1-102`
- **Course Outcome:** `CO-02`
- **Platform:** Self-Hosted (Jaeger & Loki)

## 1. Problem Identification & Initial Observations
- **Observed customer symptom:**
- **Culprit service / component:**
- **Affected SKU:**

## 2. Jaeger Trace Evidence
- **Trace ID:**
- **Jaeger Trace URL:**
- **Root operation:**
- **Failing child operation:**
- **Observed failing span duration (ms):**
- **Inventory response status:**
- **Checkout response status:**
- **Error tag / exception:**

## 3. Loki Log Evidence
Paste the exact LogQL query used. It must contain the same Trace ID recorded above.

```logql

```

- **Log message / exception text:**
- **Trace ID in log line matches Jaeger:**

## 4. Root Cause Analysis (RCA)
Explain why the reservation failed, why inventory returned HTTP 409, why checkout returned HTTP 500, and how the warehouse bin cycle-count audit lock caused the failure.

## 5. Verification & Recommended Remediation
- **What did you verify in Jaeger?**
- **What did you verify in Loki?**
- **Was the same Trace ID used in both tools?**
- **Recommended operational action:**
- **Prevention / follow-up action:**

## 6. Completion
- **Validation command executed:** `./validation_script.sh check`
- **Validation result:**
- **Evidence file saved:** `starter/evidence/evidence_D1_2.md`
