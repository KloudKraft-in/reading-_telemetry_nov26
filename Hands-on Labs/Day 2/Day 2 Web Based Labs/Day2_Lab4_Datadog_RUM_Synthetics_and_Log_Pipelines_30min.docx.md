

| NIIT TRAINING DIVISION  \|  LTM \- iRUN Full Stack Engineering |
| ----- |
|  **TRAINING LAB GUIDE****LAB EXERCISE \- 9****Datadog RUM, Synthetics & Log Pipelines — Real User Sessions, Shared Synthetic Test Results, Log Pipelines and Browser-to-Backend Correlation SOP**Read Real User Sessions and Errors in RUM  ·  Inspect the Shared Synthetic Browser Test Results  ·  Read the Log Pipeline and Save a Seat-Prefixed View  ·  Correlate a Browser Error to the Backend Trace (Browser Only) |

| Module Series | Observability & Incident Triage — Day 2: Enterprise Observability Platforms & Tool Navigation |
| :---- | :---- |
| **Lab Type** | Guided Hands-On SOP — Browser-Only User-Experience Monitoring with Datadog (Read-Only plus Personal Saved Views) |
| **Duration** | 30 minutes (2 min start-up check \+ 22 min guided UI tasks \+ 6 min validation & debrief) |
| **Difficulty** | ⭐⭐⭐ Beginner-Intermediate — Guided, Read-and-Correlate |
| **Platform** | 100 % browser-only lab on the shared Datadog SaaS organisation https\://app.datadoghq.com (KloudKraft), monitoring the instructor's pre-instrumented Ubuntu EC2 host ip-172-30-0-220 that runs easyTravel (easytravel-frontend, easytravel-backend) with Datadog Agent 7 and dd-java-agent.jar already active (env:cohort). No VM, no terminal |
| **Document Version** | v1.0  \|  IT Training Division  \|  2026 |
| **Learner Name** | \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ |
| **Date & Batch** | \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ |
| **Prerequisite Lab Completed** | ☐  Day 2 Lab 2 (Datadog Platform) — completed; cohort Datadog credentials and your seat prefix (u01\_ to u40\_) received |
| **Instructor Sign-Off** | \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ |

# 1\. LAB OVERVIEW

## 1.1  Why This Lab Exists

Backend dashboards can be green while users still suffer. Datadog RUM shows what real browsers experienced, Synthetics shows what a scripted user sees on a schedule, and log pipelines decide whether the backend log lines are searchable and linked to traces. Together they connect a user complaint to a failing backend call.  
In this lab you work only in your browser. You read real-user sessions, views and errors in RUM for easyTravel, inspect the results of the shared Synthetic Browser Test (you create none, because the trial allows only 5 org-wide), read the easyTravel log pipeline and save a seat-prefixed log view, and correlate a browser error with its backend trace and log.

| 🎯  NIIT iRUN Alignment |
| :---- |
| INCIDENT OWNERSHIP: You can show what users experienced and which backend call caused it. |
|  |
| TROUBLESHOOTING EXCELLENCE: You will combine RUM, Synthetics, traces and logs with unified tags. |
|  |
| OPERATIONAL READINESS: You can explain why a log pipeline and trace IDs are needed for correlation. |

## 1.2  Lab Scenario

| 📢  Incident Briefing — Users Report Checkout Errors on easyTravel |
| :---- |
| TIME: 16:45  │  PRIORITY: HIGH  │  ASSIGNED TO: You |
|  |
| REQUEST RECEIVED: "Customers see an error when they pay on easyTravel. Show us what real users experienced, whether the scripted checkout test also failed, how our backend logs are processed, and which backend call is behind the browser error." |
|  |
| CONTEXT: easyTravel is served through an NGINX RUM proxy on the instructor's EC2 host ip-172-30-0-220 (env:cohort); the browser SDK, Agent 7 and dd-java-agent.jar are already active. A shared Synthetic Browser Test runs against the site. You only read and correlate in https\://app.datadoghq.com and create your own saved view. |
|  |
| YOUR MISSION: Read RUM, inspect the shared Synthetic results and the log pipeline, and correlate a browser error to the backend. You have 22 minutes for the core tasks. |

*Figure: Day 2 Lab 9 — Starting Environment: Browser → Datadog SaaS (KloudKraft): RUM, Synthetics, Logs, APM ← NGINX RUM Proxy, Agent 7 and dd-java-agent.jar on EC2 ip-172-30-0-220 (env:cohort)*

## 1.3  Conceptual Foundation

User-experience monitoring has two angles: real users (RUM) and scripted users (Synthetics). Logs and traces explain the cause.  
*Figure: Datadog User-Experience Chain — Browser (RUM Session → View → Action → Error / Resource) · Synthetic Test Run → Backend Trace (APM) → Log Line (Pipeline) — Joined by service, env and trace\_id*

| Product | Shows | Answers | Key Fields |
| :---- | :---- | :---- | :---- |
| RUM | Sessions, views, actions, errors, resources | What did real users experience? | application, view.name, error.message |
| Synthetics | Scheduled scripted test runs | Does the journey work right now? | test, location, step, result |
| Logs / pipelines | Parsed, tagged log events | What did the backend say? | service, status, trace\_id |
| APM | Services and traces | Which backend call failed? | service, env, resource\_name |

*Figure: Browser-to-Backend Correlation — RUM Error with Trace Link → APM Trace (CreditCardCheckError500 Span) → Backend Log Line with the Same trace\_id*

## 1.4  Learning Objectives

* Read RUM sessions, views, actions and errors for easyTravel  
* Inspect the results of a shared Synthetic Browser Test without creating one  
* Read a log pipeline and explain how trace IDs are mapped  
* Save a seat-prefixed log view  
* Correlate a browser error with its backend trace and log  
* Respect the trial quota of 5 Synthetic Browser Tests org-wide

## 1.5  What You Will NOT Do

| 🚫  Hard Stops — Absolute Prohibitions for This Lab |
| :---- |
| ✗  NEVER run CLI commands or install agents — this lab is 100 % browser-based |
| ✗  NEVER create Synthetic Browser Tests — the trial is capped at 5 org-wide; inspect the pre-created shared test results instead |
| ✗  NEVER modify or delete shared dashboards, pipelines, log-based metrics, RUM applications or \[SHARED\] objects |
| ✗  NEVER create monitors that notify external channels — use only your own e-mail or no notification |
| ✗  NEVER put credentials or API keys in a screenshot or in this document |

## 1.6  Shared Organisation and Seat Prefix

The lab runs on one shared Datadog trial organisation. Every learner signs in with cohort credentials and uses a seat prefix, u01\_ to u40\_, for everything they create.

| 👥  Shared Organisation and Seat Prefix |
| :---- |
| All 40 learners sign in to https\://app.datadoghq.com (KloudKraft) with cohort credentials. Name anything you save with your seat prefix u01\_ through u40\_, for example the saved view u01\_easyTravel\_errors. |
|  |
| Pipelines, RUM applications and the Synthetic test are shared: read only. Only your own saved view may be created. |

# 2\. PREREQUISITES & START-UP CHECK — 2 MINUTES

## 2.1  Knowledge Prerequisites

| Prerequisite | Where Covered | Verified? |
| :---- | :---- | :---- |
| Browser login works (https\://app.datadoghq.com, cohort credentials, seat prefix) | Lab admin / instructor | ☐ |
| Datadog navigation and tags | Day 2 Lab 2 | ☐ |
| RUM and Synthetics concepts | Day 2 Theory — User Experience Monitoring | ☐ |
| Log pipelines and facets | Day 2 Theory — Datadog Log Management | ☐ |
| Unified service tagging | Day 2 Theory — Tags | ☐ |

## 2.2  Start-Up Check — 3 Browser Steps

| ⌨  Start-up check — 3 browser steps (no terminal, no installs) |
| :---- |
|  |
| \# Step 1: Open https\://app.datadoghq.com in Chrome or Firefox and sign in with your cohort credentials |
| \# Step 2: Set the global timeframe selector (top-right) to Past 1 Hour (or Past 2 Hours) |
| \# Step 3: Press Ctrl \+ K / Cmd \+ K → open UX Monitoring → RUM Explorer → confirm easyTravel sessions are listed |
| **📟  Expected Output** |
| The KloudKraft organisation opens, signed in as your seat user |
| Timeframe selector reads Past 1 Hour |
| RUM Explorer lists user sessions for the easyTravel application |
| **PRE-LAB: Record your seat prefix (u01–u40) and the number of RUM sessions shown in the last hour. This is your BASELINE.**  Answer: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_   |

## ![][image1]

## 2.3  Seat Prefix and Naming Convention

Use exactly this name for the only object you create (u\<seat\> is your seat, for example u01). Nothing in this section is run:

| ⌨  Naming convention (UI only — nothing to run) |
| :---- |
|  |
| \# Saved log view:  u\<seat\>\_easyTravel\_errors     e.g. u01\_easyTravel\_errors |
| \# RUM application, Synthetic test and pipelines are shared — read only. |
| \# Synthetic Browser Tests: do not create (trial cap: 5 org-wide). |

# 3\. CONCEPT DEEP-DIVE BEFORE STARTING

## 3.1  RUM, Synthetics and Log Pipelines

RUM runs a small SDK in the user's browser and sends sessions, views, actions, errors and resource timings. A Synthetic Browser Test is a recorded journey a Datadog location replays on a schedule. A log pipeline parses raw logs, remaps attributes (status, service, trace ID) and adds tags, which is what makes logs searchable and linkable to traces.

| 💡  Why This Matters Operationally |
| :---- |
| RUM tells you what the user felt; the trace tells you why. The same trace\_id and service tags link them. |
|  |
| A synthetic test is an early warning: it fails before real users complain, but only for the journey it covers. |

## 3.2  The Critical Distinction: Real Users vs Synthetic Tests

Real-user monitoring shows every actual experience, including devices, networks and rare paths, but only when users arrive. A synthetic test runs on a schedule even at night and gives a clean pass or fail for one journey. Use RUM to measure impact and synthetics to detect outages quickly.

| ⚠️  Most Common Mistake With User-Experience Monitoring |
| :---- |
| A learner records a new Browser Test for practice and uses up the trial's shared quota of 5 tests, so the instructor's test cannot be re-created. |
|  |
| REASON: Browser Tests are a scarce shared resource on a trial. |
|  |
| YOU MUST inspect the pre-created shared test results only and create no Synthetic Browser Tests. |

## 3.3  UX Views and Their Use

| View | Query Based On | Typical Use | This Lab |
| :---- | :---- | :---- | :---- |
| RUM Explorer | Sessions, views, errors | User impact | Task 1 |
| Synthetic test results | Scheduled test runs | Journey availability | Task 2 |
| Log pipelines | Log processing rules | Searchable, linked logs | Task 3 |
| Trace link from RUM | trace\_id and service tags | Browser-to-backend | Task 4 |

| 📝  How to Decide Which UX View to Open |
| :---- |
| Ask: "Is this about users, a scheduled journey, or the backend message?" Users → RUM Explorer. Journey → Synthetic test results. Message → Logs (pipeline and search). Then pivot with service, env and trace\_id. |

# 4\. LAB TASKS

*Figure: Day 2 Lab 9 — 4-Task Browser-Only Datadog RUM, Synthetics & Log Pipelines SOP Workflow (5 \+ 6 \+ 5 \+ 6 \= 22 minutes)*  
*Figure: Expected Result — RUM Sessions and Errors; Shared Synthetic Test Results; Log Pipeline and Saved View; Browser Error Correlated to the Backend Trace and Log*

| TASK 1 — RUM: Read Real-User Sessions, Views and Errors (UI Only) |
| :---- |

| 1 | Read Real-User Sessions, Views and Errors*Datadog RUM, Synthetics & Log Pipelines SOP — Day 2 — Lab 9* | ⏱ 5 min |
| :---: | :---- | :---: |

RUM shows what real browsers experienced. You read the easyTravel sessions, find the views with the most errors and open one error.

| ⌨  Task 1 — RUM Explorer (browser only) |
| :---- |
|  |
| \# Step 1 (UI): UX Monitoring → RUM Explorer → application easyTravel (Past 1 Hour) → Sessions |
| \#   Read: session count, views per session, error count |
| \# Step 2 (UI): Switch the list to Views → group by view name → find the view with the most errors (for example the payment or booking view) |
| \# Step 3 (UI): Switch to Errors → open one error → read the message, view, resource and any trace link |
| **📟  Expected Output** |
| Sessions list with timestamps, user agents and counts of views and errors |
| Views grouped by name; the checkout / payment view has the most errors |
| Error detail: a message about a failed request (HTTP 500\) with the view and resource that failed |
| **1.A  Record the session and error counts and the view with the most errors.**  Answer: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_   |
| **1.B  Paste the message of one RUM error and name the resource that failed.**  Answer: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_   |

| TASK 2 — SYNTHETICS: Inspect the Shared Browser Test Results (UI Only) |
| :---- |

| 2 | Inspect the Shared Synthetic Browser Test*Datadog RUM, Synthetics & Log Pipelines SOP — Day 2 — Lab 9* | ⏱ 6 min |
| :---: | :---- | :---: |

A synthetic test replays a journey on a schedule. You read the results of the shared test the instructor created. Creating a Browser Test is not allowed on this trial.

| ⌨  Task 2 — Synthetic Monitoring (browser only) |
| :---- |
|  |
| \# Step 1 (UI): UX Monitoring → Synthetic Monitoring → Tests → open the shared easyTravel Browser Test (read only) |
| \#   Read: location, frequency, success rate in the last 1 hour, last result |
| \# Step 2 (UI): Open the latest failed run → read the failing step, the error message and the screenshot |
| \# Step 3 (UI): Compare the time of the failure with the RUM error time from the previous task |
| **📟  Expected Output** |
| Test page: a success rate below 100 % with failed runs while the fault is on |
| Failed run: the step that failed (for example payment confirmation) with an error message and a screenshot |
| Times of the failed run and the RUM errors overlap |
| **2.A  Record the test name, success rate, failing step and time of the last failure.**  Answer: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_   |
| **2.B  Why did the synthetic test fail at about the same time as the RUM errors, and what does each add?**  Answer: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_   |

| TASK 3 — LOG PIPELINE: Read the Pipeline and Save a Seat-Prefixed View (UI Only) |
| :---- |

| 3 | Read the Log Pipeline and Save Your View*Datadog RUM, Synthetics & Log Pipelines SOP — Day 2 — Lab 9* | ⏱ 5 min |
| :---: | :---- | :---: |

A pipeline turns raw lines into searchable events. You read the easyTravel pipeline (read only) and save your own log view under your seat prefix.

| ⌨  Task 3 — Logs (browser only) |
| :---- |
|  |
| \# Step 1 (UI): Logs → Configuration → Pipelines → open the easyTravel pipeline (read only) |
| \#   Read: the filter, the parsing processor, and the remappers for status, service and trace\_id |
| \# Step 2 (UI): Logs → Search: query  env:cohort status:error service:easytravel\* |
| \#   Open one error → check that it carries a trace\_id and service tag |
| \# Step 3 (UI): Save the search as a view named  u\<seat\>\_easyTravel\_errors  (e.g. u01\_easyTravel\_errors) |
| **📟  Expected Output** |
| Pipeline: a filter for the easyTravel source, a parser, and remappers for status, service and trace ID |
| Search results: error lines from easytravel-backend; one open event shows service and trace\_id fields |
| Saved view u\<seat\>\_easyTravel\_errors listed under Views |
| **3.A  Name the pipeline processors that make the trace link possible and the fields they set.**  Answer: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_   |
| **3.B  What would you see in the logs if the trace\_id remapper was missing?**  Answer: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_   |

| ⚠️  STOP CHECK — Shared Objects Untouched |
| :---- |
| Before continuing, confirm that you created no Synthetic Browser Test and changed no shared pipeline, RUM application or dashboard, and that your only new object is your saved view. If in doubt, show your instructor. |
|  |
| If in doubt — show your instructor before proceeding to the next task. |

| TASK 4 — CORRELATION: Browser Error to Backend Trace and Log (UI Only) |
| :---- |

| 4 | Correlate a Browser Error with the Backend*Datadog RUM, Synthetics & Log Pipelines SOP — Day 2 — Lab 9* | ⏱ 6 min |
| :---: | :---- | :---: |

You follow one failing payment from the browser to the backend: the RUM error, the APM trace and the log line with the same trace ID.

| ⌨  Task 4 — Correlation (browser only) |
| :---- |
|  |
| \# Step 1 (UI): RUM Explorer → Errors → open an error from the payment / checkout view → use the trace link (Traces / Backend) |
| \#   If there is no link: APM → Traces: env:cohort service:easytravel-backend status:error around the same time |
| \# Step 2 (UI): In the trace find the span CreditCardCheckError500 → note service and duration |
| \# Step 3 (UI): Open the trace's Logs tab (or Logs → Search with the same trace\_id) → read the backend error line |
| **📟  Expected Output** |
| Trace: easytravel-frontend → easytravel-backend with a red span for the credit-card check carrying CreditCardCheckError500 |
| Log line: the backend error text with the same trace\_id as the trace |
| **4.A  Write the correlation chain: RUM error → trace → log, with times and the key fields.**  Answer: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_   |
| **4.B  If RUM could not link to the trace, which tag or setting would you check first?**  Answer: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_   |

# 5\. VALIDATION — CONFIRM FULL READINESS

Do not close the incident or call for instructor sign-off until ALL 8 validation steps below are completed and recorded.  
*Figure: Day 2 — Lab 9 — Datadog RUM, Synthetics & Log Pipelines SOP Validation Checklist (8 checks)*

## 5.1  Validation Task Set

Validation Check 1 — Organisation and RUM reachable

| ⌨  Validation 1 |
| :---- |
|  |
| Review your Pre-Lab record |
| \# PASS criterion: signed in; easyTravel RUM sessions listed and counted |
| **V1: Did you sign in and see RUM sessions?**  Answer: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_   |

Validation Check 2 — RUM read

| ⌨  Validation 2 |
| :---- |
|  |
| Review answers 1.A and 1.B |
| \# PASS criterion: session and error counts, the view with most errors and one error message recorded |
| **V2: Did you read sessions, views and an error in RUM?**  Answer: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_   |

Validation Check 3 — Synthetic results read

| ⌨  Validation 3 |
| :---- |
|  |
| Review answers 2.A and 2.B |
| \# PASS criterion: success rate, failing step and time recorded; overlap with RUM errors explained |
| **V3: Did you read the shared Synthetic test results?**  Answer: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_   |

Validation Check 4 — No Browser Test created

| ⌨  Validation 4 |
| :---- |
|  |
| Synthetic Monitoring → Tests (count) |
| \# PASS criterion: you created no test; the org-wide quota is unchanged |
| **V4: Did you leave the Browser Test quota untouched?**  Answer: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_   |

Validation Check 5 — Pipeline read and view saved

| ⌨  Validation 5 |
| :---- |
|  |
| Review answers 3.A and 3.B; Logs → Views |
| \# PASS criterion: processors named; view u\<seat\>\_easyTravel\_errors saved |
| **V5: Did you read the pipeline and save your view?**  Answer: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_   |

Validation Check 6 — Correlation documented

| ⌨  Validation 6 |
| :---- |
|  |
| Review answers 4.A and 4.B |
| \# PASS criterion: RUM error → trace → log with the same trace\_id documented |
| **V6: Did you correlate a browser error with the backend?**  Answer: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_   |

Validation Check 7 — Link failure reasoned

| ⌨  Validation 7 |
| :---- |
|  |
| Review answer 4.B |
| \# PASS criterion: a plausible tag or setting named (service, env, trace\_id mapping) |
| **V7: Did you name what to check if the link is missing?**  Answer: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_   |

Validation Check 8 — Full lab record complete

| ⌨  Validation 8 — Final completeness check |
| :---- |
|  |
| \# Confirm every answer box (Pre-Lab, 1.A through the last answer) is completed |
| \# Confirm you ran no CLI command, created no Synthetic Browser Test and changed no shared object |
| **V8: Confirm all answer boxes are complete and your evidence is ready to show your instructor.**  Answer: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_   |

**✅  STOP HERE — Show your completed validation record to your instructor before proceeding to Section 7\.**

# 6\. TROUBLESHOOTING — COMMON ISSUES & FIXES

| Issue / Error | Cause | Diagnosis | Fix |
| :---- | :---- | :---- | :---- |
| Cannot sign in to app.datadoghq.com | Wrong site or credentials | Check the URL and your seat credentials | Use https\://app.datadoghq.com and the cohort credentials; ask the instructor |
| RUM Explorer shows no sessions | Timeframe too short or the wrong application | Check Past 1 Hour and the application filter | Widen to Past 2 Hours; pick easyTravel; tell the instructor (Appendix A) |
| Synthetic test not visible | Filter or permission | Search for easyTravel in Tests | Ask the instructor; never create a test |
| RUM error has no trace link | Trace correlation not enabled or timing too old | Look for a trace ID in the error attributes | Search APM traces in the same minute for env:cohort |
| Pipeline page is read only | Shared object | — | Expected: read only; do not edit |
| Saved view name rejected | Seat prefix missing or name used | Compare with Section 2.3 | Use u\<seat\>\_easyTravel\_errors exactly |

# 7\. INSTRUCTOR DEBRIEF — 1 MINUTE

## 7.1  Discussion Questions (pick one if time is short)

| Discussion 1 — Real vs Synthetic |
| :---- |
| What does RUM show that Synthetics cannot, and the reverse? |
| Which one detected the problem first? |
|  |
| Key answer to explore: RUM measures real impact; Synthetics detects outages on a schedule. |
| **Discussion 2 — Trial Quota** |
| Why is a Browser Test quota a shared resource? |
| How would you plan the use of a limited quota? |
|  |
| Key insight: cover the most important journey and share the results. |
| **Discussion 3 — Pipelines** |
| What breaks if the pipeline does not set service and trace\_id? |
| Who should own the pipeline? |
|  |
| Key answer: correlation fails and logs become isolated; a platform team owns it. |
| **Discussion 4 — Impact Statement** |
| How would you describe the user impact using RUM numbers? |
| Which number would you not trust yet? |
|  |
| Answer: share of sessions with errors and affected views; small samples mislead. |

## 7.2  Common Mistakes — Learn From These

| Mistake | Why It Happens | Consequence | Prevention |
| :---- | :---- | :---- | :---- |
| Creating a Browser Test | Wanting to try | Shared quota used up | Read the shared test results only |
| Trusting one signal | One view is easy | Wrong conclusion | Cross-check RUM, Synthetics, trace and log |
| No trace link | Correlation not configured | Slow triage | Check service, env and trace\_id mapping |
| Editing a shared pipeline | Looks harmless | Breaks parsing for everyone | Read only |
| Searching without env filter | Default "all" | Mixed data | Always filter env:cohort |

# 8\. EXTENSION TASKS (Advanced Learners)

| Extension A — Core Web Vitals |
| :---- |
| Open the RUM performance view and read the load time of the booking view. |
| Which vitals would you watch for checkout? |
| Key question: how does backend latency show up in user load time? |
| **Extension B — Synthetic Idea** |
| Describe on paper the steps you would record for a checkout journey (do not create a test). |
| What would you assert at the end? |
| Which location would you choose? |
| **Extension C — Log Facet** |
| Describe on paper which log attribute you would make a facet for the payment error (do not create it). |
| Why are facets needed for some analytics? |
| What is the cost of too many facets? |

# 9\. LAB COMPLETION & SIGN-OFF

## 9.1  Submission Checklist

| ✓ | Completion Criterion | Status |
| :---- | :---- | :---- |
| ☐ | Datadog organisation reached; RUM sessions visible | ☐ Pass / ☐ Fail |
| ☐ | RUM sessions, views and an error read | ☐ Pass / ☐ Fail |
| ☐ | Shared Synthetic test results read; no test created | ☐ Pass / ☐ Fail |
| ☐ | Log pipeline read; seat-prefixed view saved | ☐ Pass / ☐ Fail |
| ☐ | Browser error correlated to the backend trace and log | ☐ Pass / ☐ Fail |
| ☐ | All 8 validation checks completed and all answer boxes filled in | ☐ Pass / ☐ Fail |

## 9.2  Grading Criteria

| Assessment Area | Criteria | Marks | Weight |
| :---- | :---- | :---- | :---- |
| Task 1 — RUM | Sessions, views and an error read | 20 | 20% |
| Task 2 — Synthetics | Shared test results read; no test created | 25 | 25% |
| Task 3 — Log Pipeline | Pipeline read; seat-prefixed view saved | 25 | 25% |
| Task 4 — Correlation | Browser-to-backend chain documented | 20 | 20% |
| Validation & Documentation | All 8 validation checks completed; answers complete and accurate | 10 | 10% |
| TOTAL |  | 100 | 100% |

## 9.3  Instructor Sign-Off

| Field | Value |
| :---- | :---- |
| Lab Result | ☐  PASS          ☐  PARTIAL          ☐  REPEAT REQUIRED     \|     Score: \_\_\_\_\_\_\_ / 100 |
| Instructor Name | \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ |
| Instructor Signature & Date | \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ |
| Remarks / Feedback | \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_  \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ |
| Completion Date & Time | \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ |

# 10\. QUICK REFERENCE — DATADOG RUM, SYNTHETICS & LOG PIPELINES COMMAND CARD

Bookmark this page. Every Datadog path and query you need in SOP order.

| Category | Path / Query | Purpose |
| :---- | :---- | :---- |
| Start-up | Ctrl \+ K / Cmd \+ K → UX Monitoring → RUM Explorer | Find RUM |
| RUM sessions | RUM Explorer → easyTravel → Sessions | User impact |
| RUM errors | RUM Explorer → Errors → open one | Browser error |
| Synthetics | UX Monitoring → Synthetic Monitoring → Tests (read only) | Scheduled journey |
| Failed run | Test → latest failed run → step and screenshot | Failing step |
| Pipelines | Logs → Configuration → Pipelines (read only) | Parsing and remapping |
| Log search | Logs → Search: env:cohort status:error service:easytravel\* | Error lines |
| Saved view | Save as u\<seat\>\_easyTravel\_errors | Personal view |
| Traces | APM → Traces: env:cohort service:easytravel-backend status:error | Flame graph |
| Log by trace | Logs → Search: env:cohort @trace\_id:\<id\> | Error line |
| Naming | u\<seat\>\_… · u01\_–u40\_ | Seat prefix |
| Quota | Max 5 Synthetic Browser Tests org-wide (do not create) | Trial limit |

# APPENDIX A — INSTRUCTOR PRE-CLASS RUNBOOK (5 MINUTES BEFORE COHORT)

Instructor only. The runbook takes about 5 minutes; run it before the cohort. Learners never see or run these commands.

| ⌨  Appendix A — Instructor pre-class runbook (EC2 ip-172-30-0-220, 5 minutes before cohort) |
| :---- |
|  |
| \# Step 1: Verify the Agent and the Java tracer on the host |
| sudo datadog-agent status \| grep \-E "API Key\|Hostname\|Site" \| head \-4 |
| ps \-ef \| grep \-c '\[d\]d-java-agent.jar' |
|  |
| \# Step 2: Verify that the RUM proxy and the app answer (host ports are examples; adjust to your NGINX setup) |
| curl \-s \-o /dev/null \-w "%{http\_code}\\n" http\://localhost/ |
|  |
| \# Step 3: Enable the CreditCardCheckError500 plugin, then switch it off after FAULT\_MINUTES |
| export FAULT\_MINUTES=20 |
| curl \-s "http\://localhost:8091/services/ConfigurationService/setPluginEnabled?name=CreditCardCheckError500\&enabled=true" |
| (sleep \$((FAULT\_MINUTES\*60)); curl \-s "http\://localhost:8091/services/ConfigurationService/setPluginEnabled?name=CreditCardCheckError500\&enabled=false") & |
|  |
| \# Step 4 (UI, as a test learner): generate a few browser sessions on the site (open easyTravel and run a booking 3–5 times); then check RUM Explorer, the shared Synthetic test (it must have run), the pipeline and APM traces |
| **📟  Expected Output** |
| API Key … valid · Hostname: ip-172-30-0-220 · Site: datadoghq.com   then   a number ≥ 1 |
| 200 |
| HTTP 200; within minutes RUM errors, failed Synthetic runs, failed traces and error logs appear in Datadog |

| ⚠️  INSTRUCTOR ONLY — Notes for 40 Concurrent Learners |
| :---- |
| Verify before class: RUM sessions exist for easyTravel, the shared Synthetic Browser Test exists and has recent failed runs (the trial allows only 5 Browser Tests org-wide), the easyTravel log pipeline maps trace\_id, and learners can save log views. |
|  |
| The RUM application, test and pipeline names are examples. Browser sessions are needed to produce RUM data: open the site yourself or let the Synthetic test run. Run Step 3 again if the fault ends before class. |

| *Official Lab Guide — Day 2 — Lab 9: Datadog RUM, Synthetics & Log Pipelines SOP  \|  IT Training Division  \|  NIIT iRUN Framework  \|  Version 1.0  \|  Classification: Internal Training* |
| :---: |

*IT Training Division  \|  NIIT iRUN Framework  \|  Confidential — For Training Use Only  \|  Do Not Distribute*

[image1]: <data:image/png;base64,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>