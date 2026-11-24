TEL-D5-501: Top Failing Dependency in Application Insights          Suggested time: 75 min
===============================================================================
YOU NEED: browser, Azure sandbox subscription (rights for one resource group), your seat id (u01-u40).
No local software. Everything runs in the Azure portal and Azure Cloud Shell (Bash).

OBSERVED FAILURE
  Downstream third-party dependency failures cause checkout degradation. Engineers cannot
  determine which vendor is failing or correlate errors to application exceptions.

STEP 1 - CREATE YOUR APPLICATION INSIGHTS RESOURCE (5 min)
  Portal -> Create a resource -> Application Insights -> Create
  Resource group: new  rg-shopai-<seat>   |   Name: shopai-<seat>   |   Resource mode: Workspace-based
  Create -> Go to resource -> Overview -> copy the "Connection String" (treat it as a secret).

STEP 2 - SEND THE TELEMETRY (5 min)
  Portal top bar -> Cloud Shell (Bash) -> Manage files -> Upload: starter/send_telemetry.py
    export APPLICATIONINSIGHTS_CONNECTION_STRING='<paste-your-connection-string>'
    python3 send_telemetry.py
  Expected last line: accepted 4573 of 4573 items - it takes 2-5 minutes until they appear in Logs
  Run it ONCE. Running it twice doubles every number.

STEP 3 - CHECK THE DATA (Application Insights -> Logs, time range "Last 4 hours")
    union requests, dependencies, exceptions | summarize rows = count() by itemType
  Expected: request 1500, dependency 2858, exception 215.

STEP 4 - INVESTIGATE (KQL)
  a) Rank the dependencies:
       dependencies
       | where timestamp > ago(4h)
       | summarize TotalCalls = count(), FailedCalls = countif(tostring(success) =~ "false") by target
       | extend FailureRate = round(100.0 * FailedCalls / TotalCalls, 2)
       | sort by FailedCalls desc
  b) Which result codes do the failures have?  (add: by target, resultCode)
  c) Correlate the failing target with the exceptions of the same operation:
       dependencies
       | where timestamp > ago(4h) and tostring(success) =~ "false" and target == "api.external-fraud.io"
       | join kind=inner (exceptions | where timestamp > ago(4h)) on operation_Id
       | project timestamp, operation_Id, target, resultCode, type, innermostMessage
  d) When did it start? (min and max timestamp of the failures; summarize ... by bin(timestamp, 5m) | render timechart)
  e) Compare with the biggest "benign" failure: is inventory-svc 404 an incident?
  Portal: Investigate -> Failures -> Dependencies tab shows the same ranking.

SUBMISSION & EVIDENCE
  1. Fill in starter/evidence/evidence_D5_1.md  (queries, numbers, first failure time, RCA, recommendation)
  2. Validate:   .\validation_script.ps1 check   (Linux/macOS: ./validation_script.sh check)
  The check reads your evidence file; your instructor reviews the quality of the reasoning.

CLEAN UP (after sign-off): delete the resource group rg-shopai-<seat>.
===============================================================================
