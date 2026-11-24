# Reading Telemetry & Observability - Participant Lab Guide: Day 5

## Hands-On Production Scenarios, Troubleshooting & Resolution Guidelines
### Azure, Cloud Platforms & Operational Dashboards

---

## 1. Module-Wise Setup Requirements

All three scenarios run in the **cloud consoles of your browser** (Azure portal for scenario 1, AWS Management Console for scenarios 2 and 3) - no local tooling and no Docker. Each scenario is independent: you can do them in any order.

### What Each Scenario Needs

| Scenario | Platform | You need | Nothing else is installed |
| :--- | :--- | :--- | :--- |
| **TEL-D5-501** Top failing dependency | Azure Application Insights (portal + Cloud Shell) | Azure sandbox subscription with rights for one resource group, your seat id (`u01`-`u40`) | Telemetry is sent from Azure Cloud Shell |
| **TEL-D5-502** Lambda timeouts | AWS CloudWatch Logs Insights + X-Ray (console) | AWS sandbox account (CloudFormation, Lambda, S3, CloudWatch, X-Ray), your seat id, the shared-VPC `SubnetIds` and `SecurityGroupId` from your instructor | No CLI, no SDK |
| **TEL-D5-503** Pager fatigue | AWS CloudWatch alarms + dashboards (console) | AWS sandbox account (CloudFormation, Lambda, IAM role creation for Lambda, EventBridge, SNS, CloudWatch), your seat id | No CLI, no SDK, no Docker |

### Workstation (all scenarios)

- **Operating System:** Ubuntu 20.04 / 22.04 / 24.04 LTS, Windows 10 / 11, or macOS.
- **Hardware:** any modern computer with a current browser.
- **Python 3.8+** (`python3 --version`) - runs the validation checker. Nothing else is installed.
- **Editor:** Visual Studio Code (recommended) or any text editor.

### Accounts, Costs and Safety

- Use only the **sandbox** accounts of the course. Never run these labs in a production subscription or account.
- The Azure connection string and any AWS keys are secrets: do not paste them into the evidence file, chats or tickets.
- Everything you create costs a few cents per day; each scenario ends with a **clean-up** step - do it.

---

## 2. Common Instructions for Trainers and Participants

### Standard Lab Workflow

1. Open the scenario folder `reading_telemetry/day5/<scenario_id>` (`s1`, `s2`, `s3`) and read `starter/README_START_HERE.txt`.
2. Initialize the incident:
   ```sh
   # Ubuntu / Linux / macOS:
   cd reading_telemetry/day5/<scenario_id>
   ./validation_script.sh start

   # Windows PowerShell:
   cd reading_telemetry\day5\<scenario_id>
   .\validation_script.ps1 start
   ```
   `start` prints the ticket and the steps. (For all three scenarios the cloud resources are created by you, following the README.)
3. Investigate with the platform tools. Take notes of exact queries, ids and numbers.
4. Fill in `starter/evidence/evidence_D5_<n>.md` completely - **replace every `<<FILL_...>>` token**.
5. Validate:
   ```sh
   ./validation_script.sh check          # Windows: .\validation_script.ps1 check
   ```
   The check reads your evidence (and for TEL-D5-503 your exported dashboards). It tells you which of the 5 rules failed and why. Your instructor reviews the quality of your reasoning in addition to the score.
6. Clean up your cloud resources: `./validation_script.sh reset --yes` (Windows: `.\validation_script.ps1 reset -Yes`) restores the starter files - **it deletes your own work**, run it only after sign-off.

---

## 3. Day 5: Azure, Cloud Platforms & Operational Dashboards

### Scenario TEL-D5-501: Top Failing Dependency in Application Insights

- **Ticket ID:** `TEL-D5-501` | **Category:** Cloud Dependency Analysis | **Suggested Time:** 75 mins
- **Starter Artifacts Location:** `reading_telemetry/day5/s1/starter/` (`send_telemetry.py`, `README_START_HERE.txt`, `evidence/`)

#### The Story

During recent production operations on the ShopNow microservices architecture, operations noticed checkout degradation. The checkout service calls several third-party vendors (fraud scoring, payment gateway, shipping rates) and an internal inventory service. Engineers report downstream failures but cannot tell **which vendor is failing**, or connect the dependency errors to the exceptions the application throws. You are assigned to find the failing dependency, quantify it, correlate it with exceptions and record the evidence.

#### A. Expected Failure (Reproduction Steps)

1. Run `./validation_script.sh start` (Windows: `.\validation_script.ps1 start`) and read the ticket.
2. **Create the data:** in the Azure portal create a workspace-based Application Insights resource `shopai-<seat>` (resource group `rg-shopai-<seat>`). In Cloud Shell (Bash) upload `send_telemetry.py`, export your connection string and run it once:
   ```sh
   export APPLICATIONINSIGHTS_CONNECTION_STRING='<paste-your-connection-string>'
   python3 send_telemetry.py
   ```
   Expected: `telemetry: 1500 requests | 2858 dependencies | 215 exceptions` and `accepted 4573 of 4573 items`.
3. Wait 2-5 minutes. In **Application Insights -> Logs** (time range *Last 4 hours*) run `union requests, dependencies, exceptions | summarize rows = count() by itemType` - you must see 1500 / 2858 / 215. If they are doubled, the script ran twice: create a new resource.
4. **Observed Error:** checkout requests fail and the Failures blade is full of failed dependencies, but nothing says which vendor to call.

*Why this fails:* every non-2xx dependency result is counted as a failure, expected and unexpected ones are mixed, and the dependency rows are not yet connected to the exceptions of the same operation.

#### B. Step-by-Step Investigation Guidelines

- **Action:** Rank all dependency targets by failed calls **and** by failure rate (`summarize count(), countif(...) by target`). Use `tostring(success) =~ "false"` - in some schemas `success` is text.
- **Action:** Break the failures down by `resultCode`. Ask: which failures are expected behaviour for this system, which are an outage, which are background noise?
- **Action:** Pick the suspect and connect it to the application errors: join its failed calls with the `exceptions` table on `operation_Id` (`join kind=inner`), and look at the exception type and message.
- **Action:** Find when the failures started and ended (`min`/`max` of `timestamp`, or `summarize ... by bin(timestamp, 5m) | render timechart`).
- **Action:** Check what the users saw: `requests | where name == "POST /api/checkout" | summarize count() by resultCode`.
- **Action (portal):** Investigate -> Failures -> Dependencies tab, and open one end-to-end transaction. Do they agree with your queries?
- **Action:** Record queries and findings in `starter/evidence/evidence_D5_1.md`.

#### C. Action Items to Solve

1. Create the resource, send the telemetry once and verify the counts.
2. Identify the failing vendor, its failed / total calls and its failure rate; name the HTTP code and the exception type.
3. State when it started, and explain why the other failing dependency with many failures is **not** the incident.
4. Fill all fields of `starter/evidence/evidence_D5_1.md`, including a recommended action.
5. Run the validation check (Linux: `./validation_script.sh check`, Windows: `.\validation_script.ps1 check`) and clean up: delete resource group `rg-shopai-<seat>` after sign-off.

#### D. What the Validation Checks

| Rule | What it looks for in your evidence |
| :--- | :--- |
| 1 | A ranking query on `dependencies` (summarize, countif, by target) |
| 2 | The culprit named, with failed calls, total calls and the percentage |
| 3 | An inner join with `exceptions` on `operation_Id`; the HTTP code and exception type |
| 4 | A written judgment about the biggest *benign* failure |
| 5 | No placeholders, first-failure time, RCA of at least 80 characters, a concrete recommendation |

---

### Scenario TEL-D5-502: Lambda Timeouts: Logs Insights Meets X-Ray

- **Ticket ID:** `TEL-D5-502` | **Category:** Serverless Tracing & Logs | **Suggested Time:** 75 mins
- **Starter Artifacts Location:** `reading_telemetry/day5/s2/starter/` (`aws/invoice-stack.yaml`, `aws/invoice_generator.py`, `README_START_HERE.txt`, `evidence/`)

#### The Story

The order-invoice Lambda of ShopNow is started every minute. Every invocation now ends with **`Task timed out after 30.00 seconds`**. The CloudWatch logs show the timeout but nothing about what the function was waiting for. You are assigned to find the stalled downstream call and the missing piece of infrastructure behind it.

#### A. Expected Failure (Reproduction Steps)

1. Run `./validation_script.sh start` (Windows: `.\validation_script.ps1 start`) and read the ticket.
2. In the AWS console: **CloudFormation -> Create stack -> Upload a template file** `starter/aws/invoice-stack.yaml`. Stack name `invoice-s2-<seat>`; parameters `Seat`, `SubnetIds`, `SecurityGroupId` (from your instructor). Acknowledge IAM creation. Wait for `CREATE_COMPLETE`.
3. Wait 3 minutes. The function `invoice-generator-<seat>` runs every minute.
4. **Observed Error:** CloudWatch Logs show `Task timed out after 30.00 seconds` for every invocation.

*Why this fails:* the logs record the start of the work and the platform's timeout message - not the call that never returned.

#### B. Step-by-Step Investigation Guidelines

- **Action:** In **CloudWatch -> Logs Insights** (log group `/aws/lambda/invoice-generator-<seat>`) find the timed-out invocations with a `filter @message like /Task timed out/` query. Note one request id.
- **Action:** Show all log lines of that request (`filter @requestId = "..."`). Copy the `trace_id` of the JSON line.
- **Action:** Open that trace in **X-Ray** (traces list / trace map) and read the waterfall: which subsegment takes almost all of the 30 seconds? Which resource does it annotate?
- **Action:** Ask why a call from this function cannot finish: open the Lambda **Configuration -> VPC**, the subnets, their **route table**, and **VPC -> Endpoints**. What can the function reach from there?
- **Action:** Write the root cause, then wait for your instructor to apply the fix in the shared VPC, and verify it with new invocations (log message and subsegment duration).
- **Action:** Complete `starter/evidence/evidence_D5_2.md`.

#### C. Action Items to Solve

1. Deploy the stack and wait for timeouts to appear.
2. Collect: one request id, its trace id, the stalled subsegment with its duration, the bucket.
3. Identify the missing infrastructure component and explain the mechanism.
4. After the instructor's fix, verify with the log line written after the fix (copy its message) and the new subsegment duration.
5. Fill the evidence file, run the validation check, then clean up: empty the S3 bucket `shopnow-invoices-archive-<seat>-<account>` and delete the stack.

#### D. What the Validation Checks

| Rule | What it looks for in your evidence |
| :--- | :--- |
| 1 | A Logs Insights query with `filter`, the timeout message and a request id |
| 2 | An X-Ray trace id and the subsegment `S3:PutObject` |
| 3 | The subsegment duration (about 29.x seconds) and the bucket name |
| 4 | A root cause naming the VPC / private subnet, route and the missing S3 gateway endpoint |
| 5 | After-fix evidence (the log message of a successful invocation), no placeholders, a recommendation |

---

### Scenario TEL-D5-503: Pager Fatigue: Tune the CloudWatch Alarms and Rebuild the Dashboard

- **Ticket ID:** `TEL-D5-503` | **Category:** Alert Governance & Dashboard Design | **Suggested Time:** 90 mins
- **Starter Artifacts Location:** `reading_telemetry/day5/s3/starter/` (`aws/pager-stack.yaml`, `README_START_HERE.txt`, `evidence/`)

#### The Story

On-call engineers receive more than 80 alarm notifications per week: one-minute CPU spikes and any single failed request wake them up. Critical incidents are ignored. The only dashboard is one flat page of 16 widgets that nobody can read in a few seconds. You are assigned to tune the two CloudWatch alarms and to rebuild the dashboard in two tiers.

#### A. Expected Failure (Reproduction Steps)

1. Run `./validation_script.sh start` (Windows: `.\validation_script.ps1 start`) and read the ticket.
2. **Create the data:** in the AWS console open **CloudFormation -> Create stack -> Upload a template file** `starter/aws/pager-stack.yaml`. Stack name `pager-s3-<seat>`, parameter `Seat`, tick the IAM acknowledgement. Wait for `CREATE_COMPLETE` (about 2 minutes). The stack publishes metrics every minute and back-fills the last 6 hours.
3. Open **CloudWatch -> Alarms -> All alarms**. You will see `HostHighCPU-<seat>` and `CheckoutErrors-<seat>`. Open each one and set the graph to *1 h*.
4. **Observed Error:** both alarms go into ALARM many times per hour: on one-minute CPU spikes and on a handful of failed requests out of about 650.

*Why this fails:* each alarm triggers on a single one-minute datapoint (1 of 1), the error alarm counts failures instead of comparing them with the traffic, and neither has a severity or a runbook.

#### B. Step-by-Step Investigation Guidelines

- **Action:** For each alarm write down: statistic, period, evaluation periods, datapoints to alarm, threshold, treat missing data. What does it compare and what does it ignore?
- **Action:** On each alarm graph (1 h) count how many separate times the line goes above the threshold. Record both numbers in the evidence file.
- **Action:** Tune `HostHighCPU-<seat>` (*Actions -> Edit*): Average CPU above 80 for 10 consecutive minutes (period 60 s, 10 evaluation periods, 10 datapoints to alarm), treat missing data as *not breaching*, severity `warning`, runbook link in the description.
- **Action:** Tune `CheckoutErrors-<seat>`: change the metric to a **ratio** with metric math (`Requests` as m1, `Errors` as m2, expression `100*m2/m1`), alarm above 5 (percent) for 3 minutes (period 60 s, 3 of 3), not breaching on missing data, severity `critical`, runbook link in the description. The links are in `starter/README_START_HERE.txt`.
- **Action:** Think: what would happen with a 5-minute period for the error alarm? (The check simulates your settings on the lab data.)
- **Action:** In **CloudWatch -> Dashboards** build **ShopNow-Tier1-<seat>** (3-6 widgets readable in 5 seconds, plus a text widget with a link to Tier 2) and **ShopNow-Tier2-<seat>** (at least 8 widgets, plus a text widget with a link back to Tier 1). Use *Actions -> View/edit source* to copy the flat dashboard. Save the source of both as `starter/evidence/tier1.json` and `tier2.json`.
- **Action:** Complete `starter/evidence/evidence_D5_3.md`, including the settings of both alarms after tuning.

#### C. Action Items to Solve

1. Create the stack and confirm that both alarms flap on the 1-hour graph.
2. Tune both alarms until each would alarm once per incident, not on spikes or background errors.
3. Build and export the two dashboards.
4. Fill the evidence file and run the validation check.
5. Clean up when signed off: delete the stack and your two dashboards.

#### D. What the Validation Checks

| Rule | What it checks |
| :--- | :--- |
| 1 | Episodes counted on both graphs (about 7 and 11 per hour, +/-2) and the two noisy settings explained |
| 2 | CPU alarm settings, simulated on the lab data: sustained 10 minutes, one ALARM per incident, missing data not breaching |
| 3 | Error alarm: ratio of Errors to Requests above about 5 % for 3 minutes, one ALARM per incident |
| 4 | Severity (CPU = warning, errors = critical) and a runbook URL for each alarm |
| 5 | `tier1.json` (3-6 widgets + link to Tier 2) and `tier2.json` (8+ widgets + link to Tier 1) saved; evidence complete |

---

## 4. Troubleshooting

| Problem | Likely cause | Fix |
| :--- | :--- | :--- |
| Application Insights Logs are empty | Data not ingested yet / wrong time range | Wait 2-5 minutes, use *Last 4 hours* |
| Script: "Set APPLICATIONINSIGHTS_CONNECTION_STRING first" | New Cloud Shell session | Export the variable again |
| Ingestion rejected (HTTP 4xx) | Wrong connection string, or ingestion by key disabled by policy | Copy it again; ask your instructor |
| Stack creation fails: bucket or function exists | Earlier attempt with the same seat | Delete the failed stack, empty the bucket, retry |
| No timeouts in Logs Insights | Schedule has not run | Wait 3 minutes; check the EventBridge rule is enabled |
| Stack creation fails: `Custom::Backfill` or IAM error (TEL-D5-503) | Missing permission for IAM roles, Lambda or CloudWatch | Ask your instructor; use your own seat id |
| Alarm graph is empty (TEL-D5-503) | Wrong region or time range | Use the region of the stack, graph range 1 h |
| Cannot edit the alarm to metric math | Using the old single-metric screen | Edit -> Specify metric and conditions -> *Select metric* -> *Math expression* |
| Dashboard JSON will not save | Missing quotes or comma after copy-paste | Use *View/edit source* on the flat dashboard and change only widgets |