# Incident Evidence: TEL-D5-502 (Lambda Timeouts: Logs Insights Meets X-Ray)

- **Participant Name:** <<FILL_YOUR_NAME>>
- **Date & Time:** <<FILL_TIMESTAMP>>
- **Ticket ID:** `TEL-D5-502`
- **Course Outcome:** `CO-13`
- **Platform:** Cloud (AWS CloudWatch & X-Ray)

## 1. Problem Identification & Initial Observations
- **Observed Failure:** <<FILL_OBSERVED_FAILURE_SUMMARY>>
- **Culprit Service / Host / Component:** <<FILL_CULPRIT_COMPONENT>>
- **Lambda request id of one timed-out invocation:** <<FILL_REQUEST_ID>>
- **X-Ray trace id of that invocation:** <<FILL_TRACE_ID>>
- **Stalled subsegment and its duration:** <<FILL_SUBSEGMENT_AND_SECONDS>>

## 2. Diagnostic Query & Telemetry Evidence
Logs Insights queries (timeouts, then the log lines of one request):
```text
<<PASTE_LOGS_INSIGHTS_QUERIES_HERE>>
```
Timed-out log line and the trace waterfall (names and durations of the segments):
```text
<<PASTE_TIMEOUT_LINE_AND_WATERFALL_HERE>>
```

## 3. Root Cause Analysis (RCA)
<<EXPLAIN_WHY_THE_PUTOBJECT_CALL_STALLED_NAME_THE_NETWORK_COMPONENT_THAT_IS_MISSING>>

## 4. Verification & Solution Details
- **Fixed Metric / Rule / Parameter:** <<FILL_FIXED_PARAMETERS>>
- **Observed Result After Fix:** <<FILL_VERIFICATION_RESULT_INCLUDING_THE_LOG_MESSAGE_AFTER_THE_FIX>>
- **Recommended Action Item:** <<FILL_RECOMMENDED_REMEDIATION>>
