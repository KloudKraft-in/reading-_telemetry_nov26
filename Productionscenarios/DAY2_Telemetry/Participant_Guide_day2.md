# Reading Telemetry & Observability \- Participant Lab Guide: Day 2

## Hands-On Production Scenarios, Troubleshooting & Resolution Guidelines (Browser-Only Edition)

### Enterprise Observability Platforms & Tool Navigation

---

## 1\. Module-Wise Setup Requirements

All three Day 2 scenarios are **100 % browser-based**. You do not install anything, run no terminal command, start no Docker container and open no local port. The instructor runs the incident on the shared EC2 host `ip-172-30-0-220` (easyTravel, `env:cohort`) and the shared platform tenants. You investigate in the browser and record your findings in an **evidence worksheet** (a Word or Google Doc supplied by your instructor).

### What You Need

| Item | Requirement | How to Check |
| :---- | :---- | :---- |
| **Browser** | Current Chrome or Firefox | Open any platform URL below |
| **Seat number** | `u01` to `u40` (from your instructor) | Used in names and worksheet |
| **Evidence worksheet** | One per scenario (Word / Google Doc) | Instructor shares the copy |
| **Screen capture** | Any screenshot tool | You attach screenshots to the worksheet |

### Platform Access (Shared, Provided by Your Instructor)

| Platform | Address | Access Model |
| :---- | :---- | :---- |
| **Dynatrace** | `https://qcw66226.live.dynatrace.com` | Read-only group `Cohort-40` |
| **Datadog** | `https://app.datadoghq.com` (organisation KloudKraft, `env:cohort`) | Cohort login; seat prefix `u01_`–`u40_` |
| **Grafana** | `<grafana-url-shared-by-your-instructor>` | Viewer; dashboards read only |

### Rules for a Shared Environment

- Read, search, filter and screenshot as much as you like. **Never** close, mute, edit or delete shared problems, monitors, dashboards, alert rules or saved objects.  
- Name anything you create with your seat prefix (`u<seat>_` or `[u<seat>]`).  
- Create monitors that notify only your own e-mail, or nobody. **Do not create Synthetic Browser Tests** (the Datadog trial allows only 5 org-wide).  
- Always use a time filter (for example Last 2 hours). Do not paste credentials into screenshots or the worksheet.

---

## 2\. Common Instructions for Trainers and Participants

### Standard Scenario Workflow (UI Only)

1. Your instructor starts the incident and announces the **start time** (UTC and IST). Write it in your worksheet.  
2. Open your evidence worksheet for the scenario and read the ticket (Story and Expected Failure below).  
3. Open the platform named in the scenario in your browser. Set the time range to **Last 2 hours**.  
4. Follow the Investigation Guidelines. Paste the **exact query or screen path** you used and one screenshot per platform into the worksheet.  
5. Fill in every field of the worksheet (no `<<FILL_...>>` tokens left) and tick the 5 self-check boxes.  
6. Call your instructor for **sign-off**: the instructor checks your worksheet against the 5 rules (Section 4\) in the browser. There is no script to run.

### Where Things Are (Same Folder Structure as Before)

Each scenario folder (`s1/`, `s2/`, `s3/`) keeps `starter/README_START_HERE.txt` and `starter/evidence/evidence_D2_N.md`. You fill the evidence file in your browser/editor and call your instructor. The `validation_script` files in each folder are **instructor-only** sign-off helpers; learners do not run them, and there is no Docker, setup script or local service.

\--- \| :--- \| \| `./validation_script.sh start` / `.ps1 start` \| Instructor starts the incident; you read the ticket \| \| Edit `starter/evidence/*.md` in a local editor \| Fill the evidence worksheet in the browser \| \| `./validation_script.sh check` \| Instructor sign-off against the 5 rules \| \| `./validation_script.sh reset` \| Instructor ends the incident; nothing to reset on your side \|

---

## 3\. Day 2: Enterprise Observability Platforms & Tool Navigation

### Scenario TEL-D2-201: Davis Opened a Problem: Find the Root Cause

- **Ticket ID:** `TEL-D2-201` \| **Category:** Platform Triage \| **Suggested Time:** 75 mins  
- **Platform:** Dynatrace (browser) \| **Worksheet:** `Evidence_D2_1`

#### The Story

The shop team runs easyTravel on the shared EC2 host `ip-172-30-0-220`. Checkout fails intermittently. Dynatrace's Davis AI has automatically opened a problem on the booking / payment path. Navigating the Dynatrace menus is slow during an incident. You are assigned to find the root cause quickly: the failing service, the failing call and the code-level evidence.

#### A. Expected Failure (What You Should See)

1. Open the dynatrace url send by your admin and login using the outlook credentials.&nbsp;  
2. Open the **Problems** app, timeframe **Last 2 hours**.  
3. **Observed:** an Active (or recently Closed) Davis problem on easyTravel with a response-time or failure-rate title. Record its problem ID or title in your worksheet.

*Why this matters:* Davis shows many affected entities. Only one is the root cause. Paging the wrong team costs time.

#### B. Step-by-Step Investigation Guidelines

- **Action:** Open the problem card. Record title, status, start time, duration and the **Root cause** entity.  
- **Action:** Open the **Affected entities** list and separate the root cause from the entities that are only affected.  
- **Action:** Follow the transaction flow in **Smartscape / Services** from the frontend to the backend and the credit-card check.  
- **Action:** Open the **Events** tab (and the **1 Events** chip) and record the event name, type and time.&nbsp;  
- **Action:** Complete worksheet `Evidence_D2_1` and request sign-off.

#### C. Action Items to Solve

1. Fill every worksheet field using only what you read in Dynatrace.  
2. Paste the exact screen path or query you used for the failed-request view.  
3. Name the root cause, the owning team (from the instructor's service catalog) and the next action.  
4. Tick the  self-check boxes and call your instructor.

---

### Scenario TEL-D2-202: Datadog Monitor Fires: Find the Cause

- **Ticket ID:** `TEL-D2-202` \| **Category:** Alert Investigation \| **Suggested Time:** 75 mins  
- **Platform:** Datadog only (browser) \| **Worksheet:** `evidence_D2_2.md`

#### The Story

A Datadog composite monitor on easyTravel (`env:cohort`) has fired: backend error rate above its threshold together with a second condition on the same host. Using only Datadog, you must trace the alert to its cause: the monitor, a failed APM trace and the correlated logs.

#### A. Expected Failure (What You Should See)

1. Open `https://app.datadoghq.com`, set the timeframe to **Past 2 Hours**.  
2. **Monitors → Manage Monitors**, search `easyTravel`, open the composite monitor (or the `[SHARED]` Error Rate monitor).  
3. **Observed:** a monitor in ALERT / WARN with a recent transition time. Record the time (UTC), thresholds and tags.

#### B. Step-by-Step Investigation Guidelines

- **Action:** In the monitor status/history, note the transition time and the component conditions (a and b).  
- **Action:** **APM → Traces**: `env:cohort service:easytravel-backend status:error`. Open a failed trace and copy its **trace ID**.  
- **Action:** **Logs → Explorer**: `env:cohort status:error @trace_id:<your-trace-id>`. Read the correlated log lines.  
- **Action:** Confirm the error signature (`CreditCardCheckError500`) and the service that produced it.  
- **Action:** Complete `evidence_D2_2.md` with the monitor details, trace ID, log query, log lines and one screenshot per view.

#### C. Action Items to Solve

1. Record monitor name, time, thresholds and tags.  
2. Record the trace ID and the exact Logs query.  
3. Paste the matching log evidence (time, service, status, message).  
4. State whether the monitor, trace and logs agree, and why.  
5. Tick the 5 self-check boxes and call your instructor.

---

### Scenario TEL-D2-203: Grafana Shows Latency: Write the Escalation

- **Ticket ID:** `TEL-D2-203` \| **Category:** Escalation Engineering \| **Suggested Time:** 90 mins  
- **Platform:** Grafana only (browser) \| **Worksheet:** `evidence_D2_3.md`

#### The Story

Checkout is degraded on easyTravel. The on-call engineer sees a slow dashboard and an open alert but cannot decide whom to escalate to. Using only Grafana (dashboard, Explore on the read-only Prometheus data source, and Alert rules), build one causal hypothesis and write an executive escalation note with deep links.

#### A. Expected Failure (What You Should See)

1. Open `<grafana-url-shared-by-your-instructor>` and the checkout RED dashboard.  
2. **Observed:** the p95 latency panel rises and the error ratio climbs in the incident window.

#### B. Step-by-Step Investigation Guidelines

- **Action:** Open the latency panel in **View** mode for the incident window and copy the URL (it must contain `viewPanel=`).  
- **Action:** **Explore** (Prometheus): `histogram_quantile(0.95, sum by (le) (rate(http_request_duration_seconds_bucket[5m])))`. Note p95 and when it rose.  
- **Action:** **Explore**: `sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))`. Note the error ratio. (Adjust metric names to those shown in the Metrics browser if they differ.)  
- **Action:** **Alerting → Alert rules**: view (never edit) the related rule and its state.  
- **Action:** Write the escalation note in `evidence_D2_3.md`.

#### C. Action Items to Solve

1. Paste the panel link and both PromQL queries with the values you read.  
2. Write severity with a reason, a 3-sentence executive summary and a causal hypothesis.  
3. Name the escalation target and next level using the service catalog from your instructor.  
4. Tick the 5 self-check boxes and call your instructor.

---

## 4\. Sign-Off Rules (Checked by Your Instructor in the Browser)

| \# | Rule | You Pass When |
| :---- | :---- | :---- |
| 1 | Problem / alert identified | The problem, monitor or incident window is named with its time |
| 2 | Failing service or component isolated | The root cause entity or service is named and distinguished from affected ones |
| 3 | Code-level or log-level evidence captured | A failing span, method, error message or log line is pasted |
| 4 | Second view confirms | A second view in the same platform agrees (S1 PurePath vs Smartscape, S2 trace vs logs, S3 dashboard vs PromQL), with screenshots |
| 5 | Worksheet complete | No `<<FILL_...>>` left; queries, links and next action present |

&nbsp;