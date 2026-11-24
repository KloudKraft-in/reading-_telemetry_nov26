TEL-D5-503: Pager Fatigue: Tune the Alarms and Rebuild the Dashboard          Suggested time: 90 min
===============================================================================
YOU NEED: browser, AWS sandbox account (CloudFormation, Lambda, IAM role creation for Lambda, EventBridge, SNS, CloudWatch), your seat id (u01-u40).
No CLI, no Docker. Everything runs in the AWS Management Console. Use the region the instructor names. Nothing is installed locally except Python for the check.

OBSERVED FAILURE
  On-call engineers receive 80+ alarm notifications per week: one-minute CPU spikes and any single failed request page them.
  Critical incidents get ignored. The only dashboard is one flat page of 16 widgets that nobody can read in a few seconds.

STEP 1 - DEPLOY (5 min)
  CloudFormation -> Create stack (new resources) -> Upload template: starter/aws/pager-stack.yaml
  Stack name: pager-s3-<seat>   Parameter: Seat = <seat>   Tick the IAM acknowledgement -> Submit -> wait for CREATE_COMPLETE (about 2 min).
  The stack publishes metrics every minute and back-fills the last 6 hours, so graphs are full at once.
  It creates alarms HostHighCPU-<seat> and CheckoutErrors-<seat> and the dashboard ShopNow-Flat-<seat>.

STEP 2 - DIAGNOSE (CloudWatch -> Alarms -> All alarms)
  Open each alarm. Write down: statistic, period, evaluation periods, datapoints to alarm, threshold, treat missing data.
  Look at the graph (set the time range to 1 h). Count how many separate times the line goes above the threshold in the last 60 minutes.
  Question: why does HostHighCPU alarm on a one-minute spike? Why does CheckoutErrors alarm on 3 failed requests out of 650?

PART A - TUNE THE ALARMS (CloudWatch -> Alarms -> select the alarm -> Actions -> Edit)
  HostHighCPU-<seat>      Average CPU > 80 for 10 consecutive minutes (period 60 s, evaluation periods 10, datapoints to alarm 10),
                          treat missing data = not breaching, severity warning,
                          description:  severity=warning runbook_url=https://runbooks.shopnow.example/RB-CPU-001
  CheckoutErrors-<seat>   Change the metric to a RATIO with metric math: Requests (id m1, Sum) and Errors (id m2, Sum), expression 100*m2/m1;
                          alarm when the ratio is > 5 (percent) for 3 minutes (period 60 s, evaluation periods 3, datapoints to alarm 3),
                          treat missing data = not breaching, severity critical,
                          description:  severity=critical runbook_url=https://runbooks.shopnow.example/RB-CHK-002
  Add the tag severity=<warning|critical> if the console offers tags (otherwise the description is enough).
  The runbook links are fictional; they stand for your team's runbook pages. Do not add an SNS subscription (nobody must be emailed).

PART B - DASHBOARDS (CloudWatch -> Dashboards -> ShopNow-Flat-<seat>)
  Tier 1 "Is the business OK?" (readable in 5 seconds): create dashboard ShopNow-Tier1-<seat> with 3-6 metric/alarm widgets
    (requests, error %, CPU, alarm status) plus one TEXT widget with a markdown link to ShopNow-Tier2-<seat>.
  Tier 2 "Why?": create dashboard ShopNow-Tier2-<seat> with at least 8 widgets (copy the flat dashboard and keep all drill-downs)
    plus one TEXT widget with a link back to ShopNow-Tier1-<seat>.
  Tip: on the flat dashboard use Actions -> View/edit source, copy the JSON, create the new dashboard, Actions -> View/edit source, paste, then edit.
  Export: on each new dashboard -> Actions -> View/edit source -> copy -> save as starter/evidence/tier1.json and starter/evidence/tier2.json.

SUBMISSION & EVIDENCE
  1. Fill in starter/evidence/evidence_D5_3.md
  2. Validate:   .\validation_script.ps1 check   (Linux/macOS: ./validation_script.sh check)

CLEAN UP (after sign-off): CloudFormation -> delete stack pager-s3-<seat>, then CloudWatch -> Dashboards -> delete ShopNow-Tier1-<seat> and ShopNow-Tier2-<seat>.
  (Alarm edits you made in the console are removed with the stack.)
===============================================================================
