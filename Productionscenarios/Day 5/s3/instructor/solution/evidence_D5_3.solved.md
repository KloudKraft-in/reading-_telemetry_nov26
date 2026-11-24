# Incident Evidence: TEL-D5-503 (Pager Fatigue: Tune the Alarms and Rebuild the Dashboard)

- **Participant Name:** Sample Learner
- **Date & Time:** now
- **Ticket ID:** `TEL-D5-503`
- **Course Outcome:** `CO-13`
- **Platform:** Cloud (AWS CloudWatch alarms & dashboards)

## 1. Problem Identification & Initial Observations
- **Observed Failure:** 80 alarms a week
- **Culprit Service / Host / Component:** HostHighCPU and CheckoutErrors
- **CPU alarm: breaching episodes in the last 60 minutes (count them on the graph):** 7
- **Error alarm: breaching episodes in the last 60 minutes (count them on the graph):** 11

## 2. Diagnostic Query & Telemetry Evidence
What each untuned alarm compares and what it ignores (settings you read on the alarm page: statistic, period, evaluation periods, datapoints to alarm, threshold):
```text
HostHighCPU: Average > 80, period 60, 1 of 1 datapoint, so a single one-minute spike alarms. CheckoutErrors: Sum of Errors > 0, so any failed request alarms; it counts errors instead of a ratio against requests.
```
The metric math expression you used for the error ratio and the metrics behind it:
```text
m1 = Requests (Sum), m2 = Errors (Sum); e1 = 100*m2/m1
```

## 3. Root Cause Analysis (RCA)
Both alarms act on one datapoint and the error alarm is a count, not a ratio.

## 4. Verification & Solution Details
Alarm settings AFTER your tuning (copy them from the alarm pages):
- **CPU alarm - Statistic:** Average
- **CPU alarm - Threshold (greater than):** 80
- **CPU alarm - Period (seconds):** 60
- **CPU alarm - Evaluation periods:** 10
- **CPU alarm - Datapoints to alarm:** 10
- **CPU alarm - Treat missing data:** notBreaching
- **CPU alarm - Severity:** warning
- **CPU alarm - Runbook URL:** https://runbooks.shopnow.example/RB-CPU-001
- **Error alarm - Metrics used:** Requests (m1), Errors (m2), expression 100*m2/m1
- **Error alarm - Threshold (greater than, percent):** 5
- **Error alarm - Period (seconds):** 60
- **Error alarm - Evaluation periods:** 3
- **Error alarm - Datapoints to alarm:** 3
- **Error alarm - Treat missing data:** notBreaching
- **Error alarm - Severity:** critical
- **Error alarm - Runbook URL:** https://runbooks.shopnow.example/RB-CHK-002

- **Observed Result After Fix:** one ALARM per incident
- **Recommended Action Item:** Review alarm thresholds every quarter and add runbooks
- **Dashboards:** tier1.json and tier2.json saved into this folder (Actions -> View/edit source -> copy): yes
