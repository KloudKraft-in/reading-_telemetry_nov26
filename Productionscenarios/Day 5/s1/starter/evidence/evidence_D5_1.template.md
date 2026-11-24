# Incident Evidence: TEL-D5-501 (Top Failing Dependency in Application Insights)

- **Participant Name:** <<FILL_YOUR_NAME>>
- **Date & Time:** <<FILL_TIMESTAMP>>
- **Ticket ID:** `TEL-D5-501`
- **Course Outcome:** `CO-13`
- **Platform:** Cloud (Azure Application Insights KQL)

## 1. Problem Identification & Initial Observations
- **Observed Failure:** <<FILL_OBSERVED_FAILURE_SUMMARY>>
- **Culprit Service / Host / Component:** <<FILL_CULPRIT_COMPONENT>>
- **Failure rate of the culprit (failed / total = %):** <<FILL_FAILED_OVER_TOTAL_PERCENT>>
- **First failure time (UTC, HH:MM):** <<FILL_FIRST_FAILURE_TIME>>

## 2. Diagnostic Query & Telemetry Evidence
Query 1 — ranking of the dependencies by failures:
```text
<<PASTE_QUERY_1_HERE>>
```
Query 2 — failed calls of the culprit joined with exceptions:
```text
<<PASTE_QUERY_2_HERE>>
```
Result excerpt (top rows, exception type and message):
```text
<<PASTE_RESULT_EXCERPT_HERE>>
```

## 3. Root Cause Analysis (RCA)
<<EXPLAIN_TECHNICAL_ROOT_CAUSE_AND_WHY_THE_OTHER_FAILING_DEPENDENCIES_ARE_NOT_THE_CAUSE>>

## 4. Verification & Solution Details
- **Fixed Metric / Rule / Parameter:** <<FILL_FIXED_PARAMETERS>>
- **Observed Result After Fix:** <<FILL_VERIFICATION_RESULT>>
- **Recommended Action Item:** <<FILL_RECOMMENDED_REMEDIATION>>
