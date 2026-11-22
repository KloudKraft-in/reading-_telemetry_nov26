# TEL-D2-201: Davis Opened a Problem: Find the Root Cause

Instructor runbook (learners do not run anything).

1. Before class: confirm shared URLs (Dynatrace) and read-only learner roles.
2. At start: enable easyTravel fault `CreditCardCheckError500` on ip-172-30-0-220; note UTC time; confirm the signal is visible in the tools.
3. During class: sign off per the 5 rules using `validation_script.sh|.ps1 check <evidence file>` (instructor-only helper) or by eye.
4. At end: disable the fault; confirm problems/monitors recover.
