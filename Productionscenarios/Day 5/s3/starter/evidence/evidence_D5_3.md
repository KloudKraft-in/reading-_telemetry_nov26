# Incident Evidence: TEL-D5-503 (Pager Fatigue: Tune the Alarms and Rebuild the Dashboard)

- **Participant Name:** <<FILL_YOUR_NAME>>
- **Date & Time:** <<FILL_TIMESTAMP>>
- **Ticket ID:** `TEL-D5-503`
- **Course Outcome:** `CO-13`
- **Platform:** Cloud (AWS CloudWatch alarms & dashboards)

## 1. Problem Identification & Initial Observations
- **Observed Failure:** <<FILL_OBSERVED_FAILURE_SUMMARY>>
- **Culprit Service / Host / Component:** <<FILL_CULPRIT_ALARMS>>
- **CPU alarm: breaching episodes in the last 60 minutes (count them on the graph):** <<FILL_NUMBER>>
- **Error alarm: breaching episodes in the last 60 minutes (count them on the graph):** <<FILL_NUMBER>>

## 2. Diagnostic Query & Telemetry Evidence
What each untuned alarm compares and what it ignores (settings you read on the alarm page: statistic, period, evaluation periods, datapoints to alarm, threshold):
```text
<<PASTE_YOUR_ANALYSIS_OF_THE_TWO_UNTUNED_ALARMS_HERE>>
```
The metric math expression you used for the error ratio and the metrics behind it:
```text
<<PASTE_METRIC_MATH_EXPRESSION_HERE>>
```

## 3. Root Cause Analysis (RCA)
<<EXPLAIN_THE_ROOT_CAUSE_OF_THE_ALERT_FATIGUE_FOR_BOTH_ALARMS_AND_THE_DASHBOARD>>

## 4. Verification & Solution Details
Alarm settings AFTER your tuning (copy them from the alarm pages):
- **CPU alarm - Statistic:** <<FILL>>
- **CPU alarm - Threshold (greater than):** <<FILL>>
- **CPU alarm - Period (seconds):** <<FILL>>
- **CPU alarm - Evaluation periods:** <<FILL>>
- **CPU alarm - Datapoints to alarm:** <<FILL>>
- **CPU alarm - Treat missing data:** <<FILL>>
- **CPU alarm - Severity:** <<FILL>>
- **CPU alarm - Runbook URL:** <<FILL>>
- **Error alarm - Metrics used:** <<FILL>>
- **Error alarm - Threshold (greater than, percent):** <<FILL>>
- **Error alarm - Period (seconds):** <<FILL>>
- **Error alarm - Evaluation periods:** <<FILL>>
- **Error alarm - Datapoints to alarm:** <<FILL>>
- **Error alarm - Treat missing data:** <<FILL>>
- **Error alarm - Severity:** <<FILL>>
- **Error alarm - Runbook URL:** <<FILL>>

- **Observed Result After Fix:** <<FILL_VERIFICATION_RESULT>>
- **Recommended Action Item:** <<FILL_RECOMMENDED_REMEDIATION>>
- **Dashboards:** tier1.json and tier2.json saved into this folder (Actions -> View/edit source -> copy): <<FILL_DONE_YES_NO>>
