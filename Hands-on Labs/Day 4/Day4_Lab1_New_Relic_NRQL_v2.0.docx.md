

| NIIT TRAINING DIVISION  \|  LTM \- iRUN Full Stack Engineering |
| ----- |
|  **TRAINING LAB GUIDE****LAB EXERCISE \- 1****New Relic NRQL — SELECT, WHERE, FACET, TIMESERIES and Aggregations on Transaction Events to Find Slow Transactions and Build a Performance Report SOP**Explore easyTravel APM Data in New Relic  ·  Explore Event Types  ·  Find Slow Transactions with Percentiles and Histograms  ·  Break Down Database and External Time  ·  Compare Periods  ·  Build a Transaction Performance Report |

| Module Series | Observability & Incident Triage — Day 4: New Relic, Grafana, Loki & Prometheus |
| :---- | :---- |
| **Lab Type** | Guided Hands-On SOP — Query Language (NRQL) |
| **Duration** | 48 minutes (28 min tasks \+ 8 min validation \+ 7 min debrief \+ 5 min start-up check) |
| **Difficulty** | ⭐⭐⭐ Beginner-Intermediate — Guided, Build-a-Query |
| **Platform** | 100% browser-only: shared New Relic account (https\://one.newrelic.com, Query Your Data \+ Dashboards) with the easyTravel entities easyTravel-Backend and easyTravel-Frontend, monitored on the instructor's EC2 host ip-172-30-0-220. No VM, Docker, CLI or licence key. |
| **Document Version** | v2.0  \|  IT Training Division  \|  2026 |
| **Learner Name** | \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ |
| **Date & Batch** | \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ |
| **Prerequisite Lab Completed** | ☐  Observability Day 3 (Labs 1–5) — signed off; Day 2 Lab 3 (New Relic) login works; your seat number (u01–u40) received |
| **Instructor Sign-Off** | \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ |

# 

# 1\. LAB OVERVIEW

## 1.1  Why This Lab Exists

NRQL (New Relic Query Language) looks like SQL: SELECT an aggregation FROM an event type, WHERE conditions, FACET to group, TIMESERIES to draw over time, SINCE/UNTIL for the window and COMPARE WITH for baselines. The most important event type for application performance is Transaction — one event per request handled by an APM-instrumented application, with its name, duration, database and external time, error flag and custom attributes.  
In this lab you work only in your browser. The instructor's easyTravel host already reports to the shared New Relic account. You explore its event types, find slow transactions with percentiles, histograms and duration filters, break the time down into database and external calls, compare a fault period with a baseline during the instructor's CreditCardCheckError500 cue, analyse errors, and build a transaction performance report as your own New Relic dashboard.

| 🎯  NIIT iRUN Alignment |
| :---- |
| INCIDENT OWNERSHIP: You can name the slowest transactions and explain where their time goes. |
|  |
| TROUBLESHOOTING EXCELLENCE: You will separate database, external and application time with NRQL. |
|  |
| OPERATIONAL READINESS: Your transaction performance report becomes the team's daily APM view. |

## 1.2  Lab Scenario

| 📢  Incident Briefing — Which Requests Are Slow, and Why? |
| :---- |
| TIME: 09:30  │  PRIORITY: MEDIUM  │  ASSIGNED TO: You |
|  |
| REQUEST RECEIVED: "Customers say search and booking pages are sometimes slow, and checkout failed for some users earlier. Use NRQL to identify the slow transactions, show whether the time is in our database, an external call or our code, and give us a transaction performance report we can open every morning." |
|  |
| CONTEXT: easyTravel (frontend → backend → database) runs on the instructor's EC2 host ip-172-30-0-220 with a steady load generator. Its transactions reach the shared New Relic account as appName easyTravel-Frontend and easyTravel-Backend. The instructor switches the CreditCardCheckError500 fault ON and OFF at announced cues; you never switch it yourself. |
|  |
| YOUR MISSION: Explore the events, find the slow transactions, analyse the fault window and build your own report dashboard. You have 28 minutes for the core tasks. |

*Figure: Day 4 Lab 1 — Starting Environment: Browser → Shared New Relic Account (easyTravel-Backend, easyTravel-Frontend) ← EC2 Host ip-172-30-0-220 Running easyTravel*

## 1.3  Conceptual Foundation

An NRQL query is one sentence. Every clause has a fixed job.  
*Figure: NRQL Anatomy — SELECT \<aggregation(s)\> FROM \<event type\> WHERE \<conditions\> FACET \<attribute(s)\> SINCE \<time\> \[COMPARE WITH \<time\>\] \[TIMESERIES \<bucket\>\] \[LIMIT n\]*

| Clause | Purpose | Example | SQL / SPL Analogue |
| :---- | :---- | :---- | :---- |
| SELECT … FROM | Aggregation over an event type | SELECT average(duration) FROM Transaction | SELECT … FROM · stats |
| WHERE | Filter events before aggregation | WHERE appName LIKE 'easyTravel%' AND duration \> 1 | WHERE · search/where |
| FACET | Group by attribute(s) | FACET appName, name | GROUP BY · stats … by |
| TIMESERIES / SINCE / COMPARE WITH | Time buckets, window, baseline | SINCE 30 minutes ago TIMESERIES 1 minute COMPARE WITH 1 hour ago | timechart · earliest |

*Figure: Transaction Time Breakdown — duration \= databaseDuration (Datastore segments) \+ externalDuration (External segments) \+ application (own code) — for a search-type transaction the Database Typically Dominates, for a booking/payment transaction the External or Application Part Does*

## 1.4  Learning Objectives

* Explain NRQL clauses: SELECT, FROM, WHERE, FACET, TIMESERIES, SINCE, COMPARE WITH, LIMIT  
* Explore event types and attributes (Transaction, TransactionError, Span)  
* Use aggregation functions: count, average, max, percentile, histogram, apdex, percentage  
* Identify slow transactions and break down database and external time  
* Compare a fault period with a baseline and analyse errors  
* Build a transaction performance report as a dashboard

## 1.5  What You Will NOT Do

| 🚫  Hard Stops — Absolute Prohibitions for This Lab |
| :---- |
| ✗  NEVER run NRQL without SINCE when comparing periods — state the window |
| ✗  NEVER share your New Relic login or paste any API or licence key into a document or screenshot — no key is needed in this lab |
| ✗  NEVER use FACET on unique values (request IDs) — results are truncated and meaningless |
| ✗  NEVER switch faults or change agent, ingest or alert settings — the instructor controls the stack and announces every fault cue |
| ✗  NEVER edit or delete dashboards created by others in the shared account — name yours \[u\<seat\>\] easyTravel — Transaction Performance |

# 

# 2\. PREREQUISITES & SETUP

## 2.1  Knowledge Prerequisites

| Prerequisite | Where Covered | Verified? |
| :---- | :---- | :---- |
| New Relic account, APM & Services, basic NRQL | Day 2 Lab 3 | ☐ |
| NRQL: SELECT, WHERE, FACET, TIMESERIES, aggregations | Day 4 Theory — NRQL | ☐ |
| Transactions and events | Day 4 Theory — New Relic Data Model | ☐ |
| Percentiles and Apdex | Observability Day 1 Lab 2 | ☐ |
| Seat number, New Relic login and instructor fault cues | Lab admin / instructor | ☐ |

## 2.2  Tools & Access Required

| ⌨  Pre-Lab — Browser Start-Up Check (2 Minutes) |
| :---- |
|  |
| \# 1\. Open https\://one.newrelic.com in Chrome or Firefox and sign in with your cohort login; select the shared account (ID 8684150\) ![][image1] |
| \# 2\. Query your data → run: |
| SELECT count(\*) FROM Transaction WHERE appName LIKE 'easyTravel%' SINCE 30 minutes ago  |
|  SELECT uniques(appName) FROM Transaction SINCE 30 minutes ago  |
| **📟  Expected Output** |
| count: a number above 0 |
| appName: easyTravel-Backend and easyTravel-Frontend are listed |
| \# Browser only — no Docker, agent or licence key: the instructor runs easyTravel and the fault switch. |

## 2.3  Pre-Lab Environment State Verification

Run all checks below and confirm the output matches expectations before starting the timed tasks:

| ⌨  Pre-Lab — Verify starting state |
| :---- |
|  |
| \# 1\. Is the data fresh? (the newest transaction should be less than 2 minutes old) |
| SELECT latest(timestamp) FROM Transaction WHERE appName LIKE 'easyTravel%' SINCE 10 minutes ago  |
| \# Expected: a time within the last 1–2 minutes |
| \# 2\. Write down the fault phase the instructor announces (expected: CreditCardCheckError500 OFF) |
| **PRE-LAB: Record the current time and the fault phase the instructor announces (expected: OFF). All NRQL windows in this lab are relative to now.**  Answer: The start-up check shows easyTravel-Backend and easyTravel-Frontend reporting; the newest transaction is under 2 minutes old; the fault phase is OFF (time noted). |

# 

# 3\. CONCEPT DEEP-DIVE BEFORE STARTING

## 3.1  Events, Attributes and Aggregations

New Relic stores telemetry as events in NRDB. An APM agent sends a Transaction event for every request (name, duration, databaseDuration, externalDuration, error, appName, host and request attributes), a TransactionError event for every recorded error (error.class, error.message, transactionName), and Span events for distributed tracing. NRQL aggregates events: count(\*), average(), max(), percentile(attr, 50, 95, 99), histogram(attr, ceiling, buckets), apdex(duration, t: 0.5) and percentage(count(\*), WHERE …).

| 💡  Why This Matters Operationally |
| :---- |
| A transaction list sorted by p95 and broken down into database and external time tells you in one minute which team owns a slowdown. |
|  |
| COMPARE WITH turns "is this normal?" into a number: the same query for the previous period appears next to the current one. |

## 3.2  The Critical Distinction: Average vs Percentile vs Max

average(duration) describes the typical request and hides rare slow ones; percentile(duration, 95\) shows what the slowest 5 % experience; max(duration) shows a single worst case that may be an outlier. A page or service where most requests are fast but a minority hit a slow database path is a good example — the average looks acceptable, the p95 does not.

| ⚠️  Most Common Mistake With NRQL |
| :---- |
| An engineer runs SELECT average(duration) FROM Transaction FACET name and concludes nothing is slow — every transaction averages below 0.4 s. |
|  |
| REASON: The average hides the slow tail, and the query mixes all applications because there is no WHERE appName. |
|  |
| YOU MUST scope with WHERE appName \= …, use percentiles or histograms for latency, and look at the distribution before deciding. |

## 3.3  Aggregation Functions Used in This Lab

| Function | Returns | Example | Use |
| :---- | :---- | :---- | :---- |
| count(\*) / percentage(count(\*), WHERE …) | Number / share of events | percentage(count(\*), WHERE error IS true) | Throughput, error rate |
| average() / max() / percentile() | Central value / worst / tail | percentile(duration, 50, 95, 99\) | Latency |
| histogram(attr, ceiling, buckets) | Distribution | histogram(duration, 3, 30\) | Bimodal behaviour |
| apdex(duration, t: T) | User satisfaction score 0–1 | apdex(duration, t: 0.5) | Service level summary |

| 📝  How to Decide Whether a Transaction Is "Slow" |
| :---- |
| Ask: "Slow for whom and compared with what?" Use p95 (the slowest 5 %) per transaction name, compare it with the same window yesterday or an hour ago (COMPARE WITH), and check the share of requests above your threshold (percentage(count(\*), WHERE duration \> 1)). A transaction is a problem when its tail is slow for many users, not when one request was slow once. |

# 

# 4\. LAB TASKS

*Figure: Day 4 Lab 1 — Four-Task New Relic NRQL SOP Workflow*  
*Figure: Expected Result — Slowest easyTravel Transactions with p95 and Time Breakdown, Error Percentage Rising During the CreditCardCheckError500 Cue, Errors by Class, "\[u\<seat\>\] easyTravel — Transaction Performance" Dashboard*

| TASK 1 — EVENTS: Explore the easyTravel Data |
| :---- |

| 1 | Explore Event Types and Attributes of easyTravel*New Relic NRQL SOP — Day 4 — Lab 1* | ⏱ 6 min |
| :---: | :---- | :---: |

The New Relic agents on the easyTravel host already report to the shared account. You use NRQL to list event types, the attributes of Transaction events, and the first counts per transaction name.

| ⌨  Task 1 — Explore easyTravel events (browser only) |
| :---- |
|  |
| \# Step 1 (New Relic → Query your data): what event types exist and what do Transaction events contain? |
| SHOW EVENT TYPES SINCE 10 minutes ago  |
|  SELECT keyset() FROM Transaction WHERE appName LIKE 'easyTravel%' SINCE 10 minutes ago  |
|  \# Step 2: counts per application and transaction name (always scope with appName) |
| SELECT count(\*) FROM Transaction WHERE appName LIKE 'easyTravel%' FACET appName, name SINCE 10 minutes ago LIMIT 20  |
| **📟  Expected Output** |
| Step 1: event types include Transaction, TransactionError, Span, Metric … |
|         keyset: appName, name, duration, databaseDuration, databaseCallCount, externalDuration, externalCallCount, error, host, … |
| Step 2: two applications (easyTravel-Backend, easyTravel-Frontend), each with several transaction names; note the 3 busiest names |
| **1.A  Which attributes of Transaction show where time was spent? Which attributes tell you which easyTravel tier handled the request?**  Answer: duration, databaseDuration and externalDuration (the rest of duration is the application's own time) show where time was spent. appName (easyTravel-Frontend or easyTravel-Backend) and host show which tier and host handled the request. |
| **1.B  Why does every query include WHERE appName LIKE 'easyTravel%'?**  Answer: It restricts the results to the two easyTravel applications, so other applications in the shared account cannot distort the counts or percentiles; LIKE with % covers both easyTravel-Frontend and easyTravel-Backend. |

# 

| TASK 2 — SLOW TRANSACTIONS: Percentiles, Histograms and Breakdown |
| :---- |

| 2 | Write NRQL Queries to Identify Slow Transactions*New Relic NRQL SOP — Day 4 — Lab 1* | ⏱ 8 min |
| :---: | :---- | :---: |

Identifying slow transactions means comparing average, percentiles and max per transaction, looking at the distribution, listing individual slow requests, and splitting the time into database and external calls.

| ⌨  Task 2 — Query builder (one query at a time) |
| ----- |
|  |
| \# Q1 — average vs tail per transaction (note the slowest name by p95; copy it exactly for Q2) |
| SELECT count(\*), average(duration), percentile(duration, 50, 95, 99), max(duration) FROM Transaction WHERE appName LIKE 'easyTravel%' FACET appName, name SINCE 30 minutes ago LIMIT 10  |
|  \# Q2 — distribution of the slowest transaction (set the ceiling near its max from Q1, 30 buckets) |
| SELECT histogram(duration, 3, 30\) FROM Transaction WHERE appName LIKE 'easyTravel%' AND name \= '\<slowest name from Q1\>' SINCE 30 minutes ago |
| \# Q3 — share of requests slower than 1 s, and the individual slow requests (use 0.5 if nothing is above 1 s) |
| SELECT percentage(count(\*), WHERE duration \> 1\) FROM Transaction WHERE appName LIKE 'easyTravel%' FACET name SINCE 30 minutes ago |
| SELECT name, duration, databaseDuration, externalDuration, host FROM Transaction WHERE appName LIKE 'easyTravel%' AND duration \> 1 SINCE 30 minutes ago LIMIT 10 |
| \# Q4 — where does the time go? |
| SELECT average(duration), average(databaseDuration), average(externalDuration) FROM Transaction WHERE appName LIKE 'easyTravel%' FACET name SINCE 30 minutes ago |
| **📟  Expected Output** |
| Q1: the slowest transaction has a p95 several times its average; max is far above p95 |
| Q2: a main group of fast requests and a smaller group of slow ones (a long right tail) |
| Q3: a few transactions have a non-zero share above the threshold; the slow rows show which duration part is large |
| Q4: database-heavy transactions (search/journey services) vs external-call-heavy frontend transactions; booking/payment transactions mix both |
| **2.A Record avg, p95 and max for the slowest transaction from Q1. Why is the average misleading?**  Answer:  Record the three numbers from Q1 (for example avg 0.35 s, p95 1.8 s, max 2.5 s). The average is misleading because most requests are fast and pull it down, while the slowest 5 % (p95) and the worst case (max) show what unlucky users experience. |
| **2.B  From Q3/Q4: which component (database, external or application) causes the slow requests of your slowest transaction, and which team would you give the evidence to?**  Answer: Name the dominant part from Q4 (for example databaseDuration close to duration for a search service). Database time points to the database/backend team; external time to the owner of the called service; neither points to application code. **Transaction type Typical observation (confirm with your Q4)** Frontend page transactions Total time includes the wait for backend calls (external time) Backend search / journey services Mostly database time Backend booking / payment services Database and external time; errors when the fault is ON Static or health requests Very short; exclude from the analysis  |

# 

| TASK 3 — FAULT & BASELINE: TIMESERIES, COMPARE WITH, Errors |
| :---- |

| 3 | Analyse a Payment Slowdown with TIMESERIES, COMPARE WITH and Error Events*New Relic NRQL SOP — Day 4 — Lab 1* | ⏱ 7 min |
| :---: | :---- | :---: |

When the instructor announces the CreditCardCheckError500 cue, checkout calls start failing with HTTP 500\. You chart the error percentage and p95 per transaction over time, compare the last 5 minutes with the baseline before the fault, and analyse errors with TransactionError.

| ⌨  Task 3 — Fault window, time series, comparison, errors |
| :---- |
|  |
| \# CUE C1 — when the instructor announces "CreditCardCheckError500 ON", write the time down and wait 4 minutes before running the queries below |
| \# Q5 — p95 per transaction over time |
| SELECT percentile(duration, 95\) FROM Transaction WHERE appName LIKE 'easyTravel%' FACET name SINCE 30 minutes ago TIMESERIES 1 minute |
| \# Q6 — last 5 minutes compared with the 5 minutes before the fault |
| SELECT count(\*), percentage(count(\*), WHERE error IS true) AS error\_pct FROM Transaction WHERE appName LIKE 'easyTravel%' SINCE 5 minutes ago COMPARE WITH 10 minutes ago |
| \# Q7 — errors by class, message and transaction; error percentage per transaction |
| SELECT count(\*) FROM TransactionError WHERE appName LIKE 'easyTravel%' FACET error.class, error.message, transactionName SINCE 30 minutes ago |
| SELECT percentage(count(\*), WHERE error IS true) FROM Transaction WHERE appName LIKE 'easyTravel%' FACET appName, name SINCE 30 minutes ago |
| **📟  Expected Output** |
| Q5: p95 lines per transaction; the fault changes errors more than latency — note any line that moves at the cue time |
| Q6: error\_pct clearly higher than the comparison period (shown as a % change) |
| Q7: an error class/message that mentions CreditCardCheckError500 or HTTP 500 on the booking/payment transaction; other transactions stay near 0 % |
| **3.A  Record the before/after error\_pct from Q6. Which NRQL result proves which transaction carries the fault?**  Answer: Record both values (for example 0.5 % before and 20 % after). The FACET on TransactionError (error.class / error.message with transactionName) proves that the failures sit on the credit-card check of the booking/payment transaction, not on all transactions. |
| **3.B  Why can the overall error percentage look small although one transaction is badly affected, and which query shows the real impact?**  Answer: The overall percentage is diluted by many healthy requests. Faceting percentage(count(\*), WHERE error IS true) by transaction name shows the failing transaction at a much higher percentage, which is the user impact.  |

| ⚠️  STOP CHECK — Wait for the Fault-OFF Cue Before the Report |
| :---- |
| Before moving to Task 4, wait for the instructor's cue C2 ("CreditCardCheckError500 OFF") and write the time down. The report should show the fault as a past event in its time series. |
|  |
| If in doubt — show your instructor Q5 and Q6 before proceeding to Task 4\. |

# 

| TASK 4 — REPORT: Transaction Performance Dashboard |
| :---- |

| 4 | Build a Transaction Performance Report*New Relic NRQL SOP — Day 4 — Lab 1* | ⏱ 7 min |
| :---: | :---- | :---: |

A performance report collects the NRQL that answers the daily questions: volume, latency tail, user satisfaction, errors and time breakdown per transaction. You save each query as a widget on a New Relic dashboard.

| ⌨  Task 4 — Dashboard "\[u\<seat\>\] easyTravel — Transaction Performance" |
| :---- |
|  |
| \# Dashboards → Create a dashboard → name: \[u\<seat\>\] easyTravel — Transaction Performance → for each query: Run → Add to dashboard → pick your dashboard |
| \# Widget 1 — Table: one row per transaction |
| SELECT count(\*) AS requests, percentile(duration, 95\) AS p95, apdex(duration, t: 0.5) AS apdex, percentage(count(\*), WHERE error IS true) AS error\_pct FROM Transaction WHERE appName LIKE 'easyTravel%' FACET name SINCE 1 hour ago LIMIT 10 |
| \# Widget 2 — Billboard: overall Apdex and throughput |
| SELECT apdex(duration, t: 0.5), rate(count(\*), 1 minute) FROM Transaction WHERE appName LIKE 'easyTravel%' SINCE 30 minutes ago |
| \# Widget 3 — Line: p95 per transaction |
| SELECT percentile(duration, 95\) FROM Transaction WHERE appName LIKE 'easyTravel%' FACET name SINCE 1 hour ago TIMESERIES |
| \# Widget 4 — Line: error percentage over time (the fault window) |
| SELECT percentage(count(\*), WHERE error IS true) AS error\_pct FROM Transaction WHERE appName LIKE 'easyTravel%' FACET appName SINCE 1 hour ago TIMESERIES |
| **📟  Expected Output** |
| Widget 1: slowest transaction on top by p95; error\_pct highest on the booking/payment transaction |
| Widget 2: Apdex between 0 and 1 and a throughput figure per minute |
| Widget 3/4: the fault cue is visible as a block of raised error percentage; p95 lines show the slow transactions |
| **4.A  List your four widgets with the question each answers. Which widget would you check first every morning?**   Answer:  Widget 1 (table) answers which transaction is slowest and fails most; widget 2 (billboard) answers how satisfied users are overall; widget 3 (p95 line) answers when latency changed; widget 4 (error % line) answers when the fault window occurred. I would check widget 1 first every morning. |
| **4.B  Explain apdex(duration, t: 0.5): what counts as satisfied, tolerating and frustrated?**   Answer:  Satisfied: duration ≤ 0.5 s (T). Tolerating: above 0.5 s up to 2.0 s (4T). Frustrated: above 2.0 s. Apdex \= (satisfied \+ tolerating / 2\) / total requests, a value from 0 to 1\. |

# 

# 5\. VALIDATION — CONFIRM FULL READINESS

Do not close the incident or call for instructor sign-off until ALL 8 validation steps below are completed and recorded.  
*Figure: Day 4 — Lab 1 — New Relic NRQL SOP Validation Checklist*

## 5.1  Validation Task Set

Validation Check 1 — easyTravel reporting

| ⌨  Validation 1 |
| :---- |
|  |
| Review the Pre-Lab start-up check |
| \# PASS criterion: count above 0; easyTravel-Backend and easyTravel-Frontend listed |
| **V1: Is easyTravel reporting to New Relic?**  Answer: Yes — easyTravel-Backend and easyTravel-Frontend return Transaction events in the last 30 minutes, and the newest event is under 2 minutes old. |

Validation Check 2 — Events explored

| ⌨  Validation 2 |
| :---- |
|  |
| Review Task 1 Step 2 |
| \# PASS criterion: Transaction, TransactionError, Span; attributes incl. databaseDuration, externalDuration, host |
| **V2: Did you explore event types and attributes?**  Answer: Yes — I listed the event types (Transaction, TransactionError, Span) and the Transaction attributes with keyset(), including duration, databaseDuration, externalDuration, appName and host.  |

Validation Check 3 — Slow transactions identified

| ⌨  Validation 3 |
| :---- |
|  |
| Review Q1–Q3 |
| \# PASS criterion: slowest transaction named; its p95 well above its average; share above the threshold recorded |
| **V3: Did you identify the slow transaction with percentiles and distribution?**  Answer: Yes — the slowest transaction was identified from Q1 by p95; the histogram showed a long tail and Q3 gave the share of requests above the threshold.  |

Validation Check 4 — Time breakdown

| ⌨  Validation 4 |
| :---- |
|  |
| Review Q4 |
| \# PASS criterion: database vs external vs application time compared for at least two transactions |
| **V4: Did you break the time into database and external parts?**  Answer: Yes — Q4 split each transaction into database, external and remaining application time; the slowest transaction is dominated by its largest component, which names the owning team.  |

Validation Check 5 — Fault analysed

| ⌨  Validation 5 |
| :---- |
|  |
| Review Q5–Q6 and the cue times C1 / C2 |
| \# PASS criterion: error percentage clearly higher after cue C1 than in the comparison period; times of C1 and C2 recorded |
| **V5: Did TIMESERIES and COMPARE WITH show the fault window?**  Answer: Yes — TIMESERIES showed the change at the C1 cue time and COMPARE WITH showed a higher error percentage than the period before the fault; both cue times are written down.  |

Validation Check 6 — Errors analysed

| ⌨  Validation 6 |
| :---- |
|  |
| Review Q7 |
| \# PASS criterion: CreditCardCheckError500 / HTTP 500 errors found by transaction; overall vs per-transaction percentage explained |
| **V6: Did you analyse the errors correctly?**  Answer: Yes — TransactionError faceted by error.class, error.message and transactionName shows the failing booking/payment transaction; the per-transaction percentage is much higher than the overall one.  |

Validation Check 7 — Report built

| ⌨  Validation 7 |
| :---- |
|  |
| Dashboards → "\[u\<seat\>\] easyTravel — Transaction Performance"; instructor cue C2 observed |
| \# PASS criterion: four widgets saved in your own dashboard; fault announced OFF |
| **V7: Is the transaction performance report saved and the fault announced OFF?**  Answer: Yes — my dashboard has four widgets (table, billboard, p95 line, error-percentage line) and the instructor announced the fault OFF (cue C2). |

Validation Check 8 — Full lab record complete

| ⌨  Validation 8 — Final completeness check |
| :---- |
|  |
| \# Confirm every answer box (Pre-Lab, 1.A through 4.B) is completed |
| \# Optional: leave your dashboard in place for the debrief; do not delete other learners' dashboards |
| **V8: Confirm all answer boxes are complete and your evidence is ready to show your instructor.**  Answer: Yes — all Pre-Lab and Task 1–4 answer boxes are complete, the queries were run in the browser, the dashboard is saved and the evidence is ready for the instructor.  |

**✅  STOP HERE — Show your completed validation record to your instructor before proceeding to Section 7\.**

# 

# 6\. TROUBLESHOOTING — COMMON ISSUES & FIXES

| Issue / Error | Cause | Diagnosis | Fix |
| :---- | :---- | :---- | :---- |
| No easyTravel data in NRQL | Wrong account selected or window too short | SELECT uniques(appName) FROM Transaction SINCE 1 day ago | Select account 8684150; widen SINCE; tell the instructor if still empty |
| Access error on APM or Distributed tracing pages | Basic User access covers only Query Your Data and Dashboards | — | Use Query Your Data; the instructor shows APM pages on the shared demo view |
| FACET name shows few values | Few transaction names in the window or wrong appName filter | SELECT uniques(name) FROM Transaction WHERE appName LIKE 'easyTravel%' | Use appName LIKE 'easyTravel%' and widen SINCE |
| duration \> 1 returns no rows | easyTravel transactions are fast in this window | Q1: max(duration) | Lower the threshold to 0.5 or use the slowest p95 |
| COMPARE WITH shows no previous values | No data in the compared window | — | Shorten COMPARE WITH; compare only periods with data |
| Error query empty | Fault not ON yet, or the cue was only just announced | Check the cue time you wrote down | Wait 3–4 minutes after cue C1; widen SINCE to 1 hour ago |

# 

# 7\. INSTRUCTOR DEBRIEF — 7 MINUTES

## 7.1  Discussion Questions

| Discussion 1 — NRQL Anatomy |
| :---- |
| Without notes: write the query for "p95 of each transaction over the last hour, in 1-minute buckets". |
| Which clause would you add to compare with yesterday? |
|  |
| Key answer to explore: SELECT percentile(duration, 95\) FROM Transaction WHERE appName \= … FACET name SINCE 1 hour ago TIMESERIES 1 minute COMPARE WITH 1 day ago. |
| **Discussion 2 — Slow Tails** |
| Why did histogram() make the slow tail of your slowest transaction obvious? |
| What would you ask the owning team to look at? |
|  |
| Key insight: a long tail or two groups point to a code path or dependency that only some requests hit — follow it with spans and logs. |
| **Discussion 3 — Database vs External vs Code** |
| How did databaseDuration and externalDuration change your conclusion for the slowest and the failing transactions? |
| What would "high duration but low database and external" mean? |
|  |
| Key answer: external time \= provider issue; little DB/external time \= own code (CPU, locks, GC). |
| **Discussion 4 — Reports That Get Used** |
| Which widget of your report would a manager read, and which an engineer? |
| How would you make the report trustworthy (time window, appName filter, definitions)? |
|  |
| Answer: Apdex/billboard for managers, table and breakdown for engineers; always state window and scope. |

## 7.2  Common Mistakes — Learn From These

| Mistake | Why It Happens | Consequence | Prevention |
| :---- | :---- | :---- | :---- |
| No appName filter | Short queries | Mixed applications | WHERE appName LIKE 'easyTravel%' |
| Average only | Default aggregation | Slow tail hidden | percentile, histogram, max |
| FACET on high-cardinality attributes | Curiosity | Truncated, useless facets | FACET on names, tiers, hosts |
| No SINCE in comparisons | Default 1 hour | Wrong periods compared | SINCE … COMPARE WITH … |
| Reading TransactionError as error rate | Counts look like rates | Wrong conclusions | percentage(count(\*), WHERE error IS true) FROM Transaction |

# 8\. EXTENSION TASKS (Advanced Learners)

| Extension A — Spans for One Slow Request |
| :---- |
| SELECT \* FROM Span WHERE appName LIKE 'easyTravel%' AND duration \> 0.5 SINCE 30 minutes ago LIMIT 5 |
| Ask your instructor to open the trace of a slow request on the shared demo view (Distributed tracing needs Full Platform User access). |
| Key question: which span holds the time? |
| **Extension B — NRQL Alert Condition** |
| Write on paper (do not create it in the shared account) an alert condition: SELECT percentage(count(\*), WHERE error IS true) FROM Transaction WHERE appName LIKE 'easyTravel%' AND name \= '\<your failing transaction\>' — threshold above 5 % for 3 minutes. |
| Ask your instructor for the next fault cue and mark on your Q5/Q6 charts where the condition would open an incident. |
| Compare with the Datadog monitor from Day 3 Lab 5\. |
| **Extension C — Faceted Apdex** |
| Calculate apdex(duration, t: 0.5) FACET appName. |
| Explain why the frontend and the backend can have different Apdex although they serve the same user request. |
| What would you show to the business? |

# 

# 9\. LAB COMPLETION & SIGN-OFF

## 9.1  Submission Checklist

| ✓ | Completion Criterion | Status |
| :---- | :---- | :---- |
| ☐ | easyTravel data reporting; event types and attributes explored | ☐ Pass / ☐ Fail |
| ☐ | Slow transactions identified with percentiles, histogram and duration filters | ☐ Pass / ☐ Fail |
| ☐ | Time broken down into database and external parts | ☐ Pass / ☐ Fail |
| ☐ | Fault window analysed with TIMESERIES, COMPARE WITH and error queries; fault OFF cue observed | ☐ Pass / ☐ Fail |
| ☐ | Transaction performance report built as a dashboard | ☐ Pass / ☐ Fail |
| ☐ | All 8 validation checks completed and all answer boxes filled in | ☐ Pass / ☐ Fail |

## 9.2  Grading Criteria

| Assessment Area | Criteria | Marks | Weight |
| :---- | :---- | :---- | :---- |
| Task 1 — Events | Event types and attributes explored | 15 | 15% |
| Task 2 — Slow Transactions | Percentiles, histogram, breakdown correct | 30 | 30% |
| Task 3 — Fault Window | TIMESERIES, COMPARE WITH, errors explained | 25 | 25% |
| Task 4 — Performance Report | Four useful widgets; Apdex explained | 20 | 20% |
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

# 

# 10\. QUICK REFERENCE — NEW RELIC NRQL COMMAND CARD

Bookmark this page. Every command you need in SOP order.

| Category | Command | Purpose |
| :---- | :---- | :---- |
| Event types | SHOW EVENT TYPES SINCE 1 hour ago | What exists |
| Attributes | SELECT keyset() FROM Transaction | Field names |
| Count by name | SELECT count(\*) FROM Transaction WHERE … FACET name | Throughput |
| Tail latency | percentile(duration, 50, 95, 99\) | Slow requests |
| Distribution | histogram(duration, 3, 30\) | Bimodal? |
| Share over threshold | percentage(count(\*), WHERE duration \> 1\) | % slow |
| Breakdown | average(databaseDuration), average(externalDuration) | Where time goes |
| Over time | … TIMESERIES 1 minute | Chart |
| Baseline | … SINCE 5 minutes ago COMPARE WITH 10 minutes ago | Change |
| Errors | FROM TransactionError FACET error.class, transactionName | Error classes |
| Error rate | percentage(count(\*), WHERE error IS true) | From Transaction |
| Apdex | apdex(duration, t: 0.5) | Satisfaction |

# APPENDIX A — INSTRUCTOR PRE-CLASS RUNBOOK (INSTRUCTOR ONLY)

INSTRUCTOR ONLY — learners never run these commands. Do this once, at least 30 minutes before the cohort. Commands run on the EC2 host ip-172-30-0-220; everything else is in the browser.  
1\. Confirm easyTravel and the New Relic agents are running and traffic is flowing, then confirm the data in New Relic: Query your data → SELECT count(\*) FROM Transaction WHERE appName LIKE 'easyTravel%' SINCE 5 minutes ago must be above 0, and uniques(appName) must list easyTravel-Backend and easyTravel-Frontend.  
2\. Access: all learners use the shared account (ID 8684150\) with Basic User access (Query your data, Dashboards). Show APM & Services and Distributed tracing on the shared Full Platform User demo view. Tell learners to name their dashboard \[u01\] … \[u40\] easyTravel — Transaction Performance.  
3\. Pre-check the queries: run Task 2 Q1 once and note the three busiest and the slowest transaction names so you can help learners whose names differ from this guide.

| ⌨  Instructor — fault cues (run on the EC2 host) |
| :---- |
|  |
| \# C0  start of Task 1: confirm the fault is OFF |
| ./faultctl.sh off |
| \# C1  start of Task 3 (about T+16): announce "CreditCardCheckError500 ON" and the time |
| ./faultctl.sh on |
| \# C2  end of Task 3 / before Task 4 (about T+23): announce "OFF" and the time |
| ./faultctl.sh off |

4\. faultctl.sh calls the easyTravel ConfigurationService (setPluginEnabled name=CreditCardCheckError500) on port 8091 and prints a time stamp to announce. Write the cue times on the board.  
5\. At the end of the lab confirm the fault is OFF and ask learners to leave their dashboards until the debrief is finished. Delete them only afterwards, from the New Relic dashboard list, and never delete the shared Cohort Overview dashboard.

| *Official Lab Guide — Day 4 — Lab 1: New Relic NRQL SOP  \|  IT Training Division  \|  NIIT iRUN Framework  \|  Version 2.0  \|  Classification: Internal Training* |
| :---: |

*IT Training Division  \|  NIIT iRUN Framework  \|  Confidential — For Training Use Only  \|  Do Not Distribute*

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAowAAAE4CAYAAADRgKIoAABiqElEQVR4Xuzde3hURZ4H/P1j3+d5n+ed3ZlldsYZxbsiihoQEaJyURFE442AYgAVUBEUCDdRwcjFoHJRMDBg1EgiUVCugmRGRUAIg0IACXeCXIIEEggkmpnZnd39vedXp+t0dVUl6Q7p9EnzzfN8nqpTp86l++SkvqlOd/6lW5u7CQAAAACgOv+iNwAAAAAAqP7l4quvIQAAAACA6iAwAgAAAECNEBgBAAAAoEYIjAAAAABQIwRGAAAAAKgRAiMAAAAA1AiBESDOXXrNtXR71yTqlPQwQHy57yFq0aad8T0PAPUPgREgjt3W5T6jDSDe3ND2NqMNAEy5CxeS/rVu/Qajn01kgfHpu6lpySS6uPvt5joA8BWeWdTbAOJVx3sfNNoA4o0+y35920SjT3Vq+/qhsNDYRhVeYLzuOhEUdRc3s/T1ga3bt4sH/9mSpdTsxgRR1/sAxDt+GVpvA2gorW7raLTprr6xlXV2sLptq2tnV1x3g9EGEC/a3nG3ERZVlzSreYIg3K+aQmPNgfGWBGr608RgSDw2UbSHBMfD483tfIC/ODDq7QDnC/4horeprm3Vmp4a/LzRDnCurmgRWXi7/Nrrw962tvUA0VB25gxt3rad1m/6js7+8ouxPlKXNGtutFXnuptuMQKijb6dVNvX/T1TQpb17aUaA6P8ErOJ12gP7oYWov1fFg2ybve3v/3d256/9H2q7Wr9Z+dCyLpcp+577bfrvf4fzMumR/r09Zb566573b/Z4i8OjFffEDrDqH/p5w4QL2r6AXLy1Cmv/vXadcZ6VZHTl/ufPHWYMr8Pbqc7efgvRptq0zyzjXXuN8Roi5bMgurPH6Kj79NPU1IHs53dHCirezm5b0o3t96hh7EOoKEcLy0V5cvjJ9BTz7m/ZG/fucvoV5M/vf8Bfb3uW9qxew+t/PJL0Xb5tS2MfjZqKBw4fLTA9d0HikLW3dblXmNbZvu6tnU7UQ4ZNUbU5bL80vfBwgqM/PXX77431v+/kx+pNjBymOP6kuWfi2Wuf/TxJ15d9tu9dy/1f3aQ1y6/uL6lYGtIfyYDo7qP2++6W9Q7dbnHW8dfHBivuv5Gr22uc8H0bR8f8HTI/gHiRU2BUdf1AfuAzTgwesvztogye/xfvND56oodbqBUAqNcd3LfCqfsRK879U2L53ntIz/aIuq9An1PFswT7S/95TAtGeruo3jtdK9f26uDYW/l4eD5FDkhltdnDw8eVz+G6HvHELcfAmOD+mH3Gq/+Tk9ezqckp57Uwf25OzSwrrrv1R++fIem5m2nj8YFgiNAAxv58liv3rxlq5B1cz7IMvrbfLV2rSiPHD8e0v5Az0eNvja2wKiHRUnfdvbcd0XW0b84IB4tPibqPfv209bWITAynrFTv9p3dsMZqykw6sudunZTdxPypW7DX/w3iJ9/8YWof/n16pB92QKj/iXb9RlGdT1AvLP98JAGpw432qrDgbG4+DhtW/ayFxhXvuKue8mx7dMUUVcDY1vRL4M+KTwlQiC3yRnGzECfjI8+pqK/jDdm/Xgm8+LhHDSvod3L3NnHk6d2VBMYA8H01BZxrKeHDhH4/LYtHinqfF4nT7k/qJfsQ2BsSCvfCV3+Ybc7syKDYm2BceOaNfTDmvAGZYBoOHn6dMiy+nJ0RVWV0d/mh927RXm0pCSkva6BkcNi4d59Rli03Uc7d+3yss8///lPuq3zPd6MIruxXXs69tNxr4/80vfDag2MUvb8XLGTl18N/s1ipIHxZGmpsU7ts2vPHlHKN6rY+toCo95HtuuBkWcz1f5FP/5obAcQL2w/PKS7kx6gVya9RkNGjhIzbwOHDjP6SLYZRjUwnty9WNT1l6S/3c7bTRdhj5fVwHhy+8fuvi2B8eLX1zrHdAOeO0PplrLfbuV81MAogynrfofTVuie16sDU2hboJ+6LUTfD7s3B+odAjOMkQVGnmG8+OoX6IfvFxrrABrC0i++MNokGQTDwS9HMw6ZX3z5lWi7vPl1Rj8bPTDKl6Tfd37pri0wLlq6VOQe/uIZRTUsSnlffu31kV/6fljYgfG2OzuLnYwb777xRWzshMVIAqOsq1+P9n08pP2Fl8eFLOv7tgVG/Uu264HR1p/bHn38CeM4AI2d7YdHddSXcuviiV6djLba9HogWOeAp66TL0uzpwe6M5him373G/tRte31TMh+nx76pFJvuL+VhKCHn679z34i+V4FaGh33ZdktN14S90+ML55y5tEGcmbXvRQWB3b3zBe5oRS2xcHxUNHjujN3pe+H1anwPj/zH7cC4u2wMhvRNGXedZQLk99ewZNn8m/OQb7tGybGLId1/X9sC5JDxjtfG5vvZNBd3YLfkgx95EhVe//xrTpor9cln8DCRBPIh2EX5syNaIfYtExkrI/etfSDvEsIRGf7Qv+9XCvFHrltXRv+fGnn6HnRow0+tXmw1z3lZVIReNd0vqbXNSvbg/Z9xVxYByxZK4XFC9shY83APAr/rdpehtAQ7jp9vBnnNve0SWibatbH/tfdgCi51w+h1Hmt3C/9O2lsAMjm/Pe+yIw/vqZrsY6APAX/I9dOJ/c3OEuow0g3uhBMdz/9JI26TU9F1q/9O1UEQVGAGhcbP9FAwAAzk/VffHfOup9dQiMAHGOPxQZ/zYN4hG/DI2ZRYCGgcAIAAAAADVCYAQAAACAGiEwAgAAAECNEBgBAAAAoEYIjAAAAABQIwRGAAAAAKgRAqOPNb2qGTW5sCkAAABATCEwxgL/C6ta/o0VwiIAAAD4BQJjDFzVso2gt6v0CwUAAAAQKwiMDezSa1pQ8za3ClzX10v6hQIAAACIFQRGn9IvFAAAAECsIDD6lH6h4sUVrdrRNW07xkTTa280zgcAABqff+u3in416pAv8bnp5xsPEBhj4MYOXQS9XaVfqHigB7hY0c8LAAAaDz2g+ZV+3o0dAmMMnI+BMZYzizr93AAAoHHw88yiLt5mGhEYY6C+AuPGyiqq2L3AW64oWU2ZhVU0RulTUVXl0bdn/QYP8vrZluuLHtpiST83AABoHPRQ5nf6+bP0qdOMtrrYvH07Lf3iC6M9XD+dPEkXXXk1HT1eYqyzQWCMgfoKjHoQtAfGHco2g2hN1iDKXL2D8rLGOMvpYvuCbUtpzTanX/pSd3lpurvM2yQOotKyEkoI7CN96QYqKtxM7S3nUxM9tPX+dC9VnDlGy/L30vfZjxrrw/co9TfaaqafGwAANA56IItcOf2dyGinkz979bV/M9efrWWb6ujnz97LzhGlOqFT35M0tWnqBEW9rTZ1CoxfrV1rtKmeGTLMaDsXA557XtDba/PsUPt51Pf5RapeAmPPpVSaP43ySoIB0R4Y5Tcj/waRRhVlG7x2tSyudtn9zcNtT/NmNNNf7B96PrXQQ9sbm85Qxcm93vL3Z6rojXFTqaJ4Le1xjsVtfMxrUpfQD2sWuvVAX1mvqDrmlDPpI6f+A28/cyGV7VxCZd76g3TN1I3UG4ERACAu6IEsUtv/l+hXX/2DWvBy5s9ODPw/Wv7j/4jwl13i1Lf8Qn/nPoH+e/9JtNBp469fjSqjEz/+IsLjfSsriSr/Qe+uLBH7mLDpv+jdN8zj6efPZGC89+Hu1LZDJ2N9bWzh8pJmzY226qgzir+/5DI6+8svRh+bOgXGDd99Z7SpjpeVibJ5QiuB66fOnvXWd3uou1dXw1unrt1EmZzSx2vLmp8bsu/Bw0d4dXX/N9/eQZDr3nx7hii3FhaGbJ+U3IPWbNjgLavnwvoPGuzV5Xmox+zd/6mQ/nVRH4GxyAuCVcEQaA2M6gyjE/gKs0W9oNqAqC2X7aCc3AUCLw+anu0dVz+nmuiB0fP4ZKrY/wW9v7U0sN9Sp30OzXDW/bhmMq0+GXyccpveKw6KoPh+d152A6P3XDjuWLyX7lh2kD7aU0XfVwa3Q2AEAGjc9EAWKf76+z/+zwl7f6Psk0RrPw+0n+TwSKKuzjAS/a8o3RnGYtHnbGC9nGHkgEn//F/a+715PP38WeY8dxyuq0jHX1VpeTn99qKL6XcXXxrxvqIWGDmwfTB/vji59p27iMDIgbC45IRo5/qJU6dEGDvz88+i/5KVK0WAnDrzHbGOA9tnS5eJdRwc9x08KPpzqe6fj7k2P582bSkIOY9d+/ZR98dSQtq+Wb+e+j71tBc2l32xSuyPj3W6spKeHzGSpr2TQfsPHaJho1+gEuexTJ42XRyXw+aLr46n0xUVxmOORH0ERvUiy7o9MO4Tf5fo/m1iHQKjLCvLqcmTC6h4dRo1SRwT0TcZ00PbD872n6a6dZ5VlIHQDYwdqWyzOzPIM5G8PHHxWmX7R2l1Ps8uhgZGXl42f6ZTDqU9TtC8ZvCX3v4QGAEAGj89kEWmhLavc+v81X/X/9DfD58lEQSd8HciEBj5S24j66L8/r9FfXl5oC0QGM8WnXbKExEHRs5F6mRHuONquP1sHun7uCh37NkT8X7CDozXt25DX6/7VuBAKOt6PyYDI9c56HHYkjOM8knhdjn7x+tkfw6SvP7A4cPe9jIwcojjNi7V/XN58MhROnnqtHcO3Gfky2NDZgwZT73y+RU6T5Y6e8mBUZ4bbyuPxX3VGUYOlRs3bw7ZZ6TqIzDWp+Suocv63yfKN8K4ulC/Pl2MfdRGD20y+A1N7e8tPzvQ/reMdwx82WizGTruVaPNRj83AABoHPRAVh/Ey9MB/T85aazvn1Pi1VM+KVXW/eRu+0ZwvU4/f8YvSV953fVGe7giDXqqwr17RZn6Ar+PwVxfk7ADoyrcGUauy8DIM3UcBuU6nr3b/+OPtHjFChHCZP+3Z82mlCf7U7nTxst/3byl2hlGuX8u+e8qv9u61TuH77dtE305IMo2numUfwu558ABUR7+6Sc6dOyYN8PI55X39eqQwMjnw+Fz9LhXaNzE10JeXq8LvwXGhtDslg5GcIsV/dwAAKBx+FXqHiOU+ZZzrvr5M345eOCQYUZ7uK5scQN9uWZNiBl/mmP0q86d3e4z2sIRlcAYrqIjR0TJYVJf1xC6PPCgeJmZX4LW10XT+RgY//Piy4zgFiv6uQEAQOPwH1e1NoOZT/G56uffmNUpMMK5OR8DI2va/HojvDU0/ZwAAKBx+XXnMUY48xs+R/28GzsExhg4XwMjAAAANE4IjDGAwAgAAACNCQJjDCAwAgAAQGOCwBgDCIwAAADQmCAwxgACIwAAADQmCIwxEE5gvL7tbQAAAAC+gMAYA+EERj3ZAwAAAMQKAmMMIDACAABAY4LAGAMIjAAAANCYIDDGAAIjAAAANCZhB8YTp06J8lBxsSivbdValEtXfmH0Zc8OHRZS79S1W419wqHvY8qMmdR/0GCjvftjKca2foLACAAAAI1J2IFx3ca/inLxihUh7Zu2FBh92eGffvLqp86epTffnhGy/mhJCY2dOIm+37bN2LY6+j5efHU87T90iG6+vYNY5jqXSck9jG39BIERAAAAGpOwA2N5ZSV9ve5bqqiqEsvHTpwQyzzDp/dNebI/NU9oRe/NyxbLemBcl78xpP/crCx6fsRIOu0cIzmlD+3cu5e+Wb9erDt5+jS94gTLvQeKxD6+WruW9v/4o1i3tbBQhETehkPjwSNHRTv3Ky45Ic7jL998Q98VFFDiHXd5s6SxVh+BsflNtxhtEDs3tmtvtLW96x6jzdYvHlT3uC5p0YquaduxVvp2AADxoE3Hu+nWzvf5nn7eNmEHxkhwWDteVuaFy9oC4+DU4aIvb8PhT7bzNidPnRbhlNep++B+amDkNjnDyP14f4yPzTOOXN+xe49xrrFQH4ER/OfqhJtClvXAqK+PN7bHpwfD6jS99kZjWwCAxoyDWMduD1Hy40+H5f5eTxhBriEltOtgPAZV2IExkr9hlC9Tj0+fLEo9MLLS8nLKmp8rZgB5NrHbQ93pzM8/i/BXuGcPrc3PF/2279pFy75Y5QVGnmE8cPiwWKcHRg6XXMoZxsHDR9C+gwfpx6PF9Ejfx8U+9HONhWgExgGDn6Pb77qbLrziKjpeWmqsh+jTA2Jty/HG9vj0YFgTfVsAgMaKZxYjCYtSd4ce5KSO9zxIG5189fW3G6jz/T2M9dX5YfceUe7at1+UH3z0Md12dxI9NWSE0Vd/HKqwA2Okf8NYV+oMY7yKRmBs2TYxZPmiK682+jS5MJGWrFwpmOtq95ilbcn7Lxlt4Wh2x/3U0il7TPlMLHe+o6XRp7HRA1Ntyyzj8b7Uk/VKMtY962jRe6yoL59uHo89yNv+6WvKfZX387Cxvr60nvsP+qNXP0C/f6rC6GN7fHoorIm+LQBAY8XhSw+D5ZU/U48nnvFeAZVWrV4b0k8PcdKWH3Z49aVf5Bnrq/Pd1m2i/GbDRlF2cIIsl7Pfn2f0ZfpjkcIOjB273CP+ZvHBR3qJ5TkfZInlS5o1N/pCzaIRGC+49PKQ5Rat2xh9Jn+qBcV7UkV4fKwlL98j6rPH9aEmj0+necvdvty2cN50UR8z5WMjbC55f5Jo68j13DcC2ywLHnPeMm+bJSvfF/UBnd39inbnWE1ectubtAyGz3H3BI7hrJ+91Om7NFssL+Ttlrshc/K4N8R2Lfu5Jbc1e+xV73zU82wIemCqbZlNVut5O2mIEwC379xK3ZzyZUeT6XnUotujlPcnp37z69SC+77kPn6P0+fD5936Nx8+Jcp3+zUV++Ewun3rcqdtGGWMeJQ27NxpnEOTC292Q6vjwW43W9Y3pau7OEHxTwdEHYERAKBmHLz0wNj32aFGm011L00X7t0XDIHbthvra/Lp0s+9+oOPPUHvZecafST9sUhhB0aoP9EIjGVnznj1g0eOGOulAWPeoIXLAwFv8TvUrXt3yg2ErW59nguGOO77TjD4MXeGsV9Im5xhXLLyYxqT5e5nTOfg+iHO/vkYs1/iPm7QWfLpdHps+mc0gvsEjpU73d0v72/IHCWUBtZzqBRl4j00YY67H96nui2f35J5k8Tx5LEakh6YaltmemDk8sNNbskzjBwGuS5nGLd/meEEwe9C96MExs9+2EnPznfXb9/pbsv7431v3+nSz6E2F40gSnjrH3TTXBLLCIwAADXj4KUHwUGjXjbabPSXpQcNH+PVJ775Fr0z931R79q9F42b9IYR+GwmTXnLq/NL26PGjTf6SPpjkRAYYyAagVG6rlVrUfI0t75unjI7mDuljzcTOOa5PjQ7sI5n8GRIaxYIac1S3xGlNTAun+OWi90+Y6aHBrWpz7ovNXdMDC8wcuhckvVqcB8hgdENp82GuMe0BsaV7kzkkAH3h5xHQ9ADU23LLHdGBk0XxhqB8d0R7gwj179f7j4P07/cSdOTtGMrgbHJhaNp+2b3eeZwqM4wfvjaIFoe2HckWgeCYpMLR9GVtyMwAgDUhoOXHgT502b4Jenvtv0Q4t3s3JB+93RPCQlwz40IBkbd629lGG06ORu5RntJOiMzy+jL9MciITDGQDQDo8oWGjt37x7y94I8GxesmyGL/9ZQb9Op28mXpVXV/n1iohowZJ/nzH6KW+8Pnm911MfUkPTAVNtyXXBg1NtC3DyM7grUjZnIKLM9Pj0U1kTfFgCgseLgpQfGcOkBju3ef0AEvU1bttI36/Pp7gd7ipeo+c0rel/dD7t2i3Jn4E0vL0+YLMqBw0Ybfa+6oZXxWCQExhhoqMDY0MaMU2YG62jEc48abY1Fy1tDQ48eoPT18cb2+PRQWJ0rWrUztgUAaMw4gOlhsDZ33p9shLiGpD8GFQJjDNRHYKzug5LBP/TAeD7Sg2F19O0AAOIBh7AHU/oZwdBGD28N6brWtf/SXmtgbNriFvpjm/scSVAHF7a8w3hO6yMwMv6gZA4lEFu2mTXG6/Q2xv31fTRm1T1+iT+UWw+ImFkEgPPFRVdd48v/+JJ4173ULMH+yRg21QbGptdcb4QfqDt+Pus7MAIAAAA0hGoDox544NwhMAIAAEBjhMCouSTxIbr90SHUodewENd3fdzoy255eKDRl9v0fgyBEQAAABqjOgXGdiMW0R2T8o32xu66u/sYbfUJgREAAAAaowgD4/3UPfe/Q1zc/jFLvyS6qtvzIfWmt/b0lrl+9X1DBX076Yqug7z6TQPfNdZHwxXtg+fI+qROMPrI2UN9FpH76v31PgiMAAAA0BhFFBg5uOmBscv03UY/ljT3uFd/KPsXuqHPm94y16sLjA98UC7Ky+7s59WvT5ls9Iu21Rs3U8dHBtPWXftC2vklZ7WUZuV8ZgRGvQ8CIwAAADRGYQfGu6cVUutn3zMCY9e39xp9L7urP13Y5gHRn5dtgVHtnzS3hG574XOxzQNZZ0R58+APRf2S9r2o26wjol+nCeuoy7Rdon7vn45Sm6HzjWPXlzfn2vfdYIHxjxcZFwv855LrEqr1b02aAAAANCr6WCZFFBivTR5nBMbbX8oz+t7/Xhk9mFUu1vNybYFRLl/a6QlvVlEExkCdAyP3kcfkfp3f2EYPf/R349j1ZfGf14py4Muh51pdYLQFTL1PRIHREk7Af/QbCoERAAAaM30sizgwPvhhhSgvvOUBL7hd0qG30Y/d+fpmUV73yHhR2gLjLUNzBbnMJQfBh3KqvBnG++YcC5lhvOuNAurwympRv2fGAWo3cpFx7PrStW8qbd9TRDM//DSkvbrAyH2Zra+EwBh/1JvpkScGUI++/RAYAQCg0dLHtZs73BVZYGSdJqyn63qmGe3xQn/Ti011b3qx0fucS2D84+VXUaf7kiGG+Bro10XeVBwU+cZSby79JgQAAPA727gWcWCMd37+WB09vEBs6NdF/S1MhcAIAACNUXXjGgKjxq8f3K0HF4gN/bqoU/c6/Saszb//9rfG/gEAAOrLby74gzH26PSxTEJgbEAIjI2ffl30G+pcAqO+bwAAgPpWW2jUx7JaA2PTa643Ag/UHT+fDR0Yd+7dR32fGWK0Q93p10W/oRAYAQDA7/TxR6WPZbUGRqlpi1ucwHOfEYAgPBe2vMN4TqMdGN//6GM6eepUCL2PNG7ym0r9NXpk1GtGn5rkrC9UlgfSB+PMPjZLVmaLsmvKM3SXWM4z+viRfl3kjdTq9jtC/n4RgREAAPxKH39U1Y1rtQZGqH/RDox6WKwpMJ7c+j2tfkdud5SmrT8asv4FJVCyceNSRflJYeg+f1w/N7Sfsp2+j06PTqHxTzjloFn02IRsetJpGzhreWgfn9Kvi7yx1D8MfjjlcQRGAADwLX38UdnGNQTGGPFLYORwOE70LwlsFxoY9wW2c7dfToXLX6WJ3/xI0+4LBsatgT5uYJwrwqc8Hu9X9luxKMfb75NvLwmexytuYOTwOFq2+Zh+XWw3lry59JuwNvq+AQAAokEff1S2cQ2BMUaiHRiXrfpzWIFRX68HxtDtltMnXL6zIYzAqM1SzsgJ3dfwTBoo64HAeO9rn1AfZRu/0q+L7cZCYAQAAD/Txx+VbVxDYIyRaAbGH48Ew9rRn36ixwcONfpIJw+udev9l1PhyrFGYOx036si6BWu/4T0wNhp3CKxTgZGNxC6gfGR6avE8uLpA519Zyj7CB57yaez3HogMH7WyP+GEYERAAAaC338UdnGNQTGGIlmYGQDnh9ptEH90K+L7cZCYAQAAD/Txx+VbVxDYIyRaAdGiB79uthurNgHxgzauaiHqFdUVYWU1ek3wO1fnYqqEqNN3zaleztjXX1I7mq26casLqFplvaGkjJ4kCjd57kLtQ+0VxxcavRVcf+KwxtClwOKV6fV+LzXt4Tu/Y22zMIqGmPp25Dkc2s1drUo+bky1lnkjZX1bMq0rA9HTedTUMt9ZjNoxREq2O8+DqY+3xUlwfaa2mpyrt9D8vtCfm/r6z2JNf8MqYvUL91zlz9bYv29GKnf3DaAfjXqUIP7TWJf41x0+vijso1rCIwxgsDYeOnXxXZjxT4wOj/cyziEcOAIDYz9Qga7dpQg+2uDULI2KPKgo7ap4UJuqw7aagBNGlD9AMv0Y+kKctyyfZ+a+0k1Deh2XSgpUW8LUh+Lfg5yXXFIUDDDiHpO8vHyYJhkbOuEmpLgsv68254r9fnVz686/Qb3VuruNhy6g23u9VUDo7qN+nhsQVNuz/ic3O+zLt73m7rOW9YCh+25lY/V+z4OBEYb9Xudt+MQHwyM9n6q0O+j4L2ino/6S1Jo/9DHavulR7bxc6y28/Ot91fPke+36s5ZJc+tusBo+yVRPa78XlO/L/h7W9/GU+21CP4CJfarHCPce1X+bLE9N6xfny7i+yd4nNBjysdqe8yGrsHv81Ch+wyHHuQakn4uOn38UdnGNQTGGEFgbLz062K7sXwRGJ1BbdqWKkpatE8sl+ZPo4zcVe66ys0ilPCA5gVKJTAmDZ/m7UPdnyz7rThCyU594f7QbeUP9YpK95gVuxeE7EO07V8qBlweuHld6LHSaeMs7pfqhMTgQMyBkR8LH3NNWXB/si62zdkRemzet/PYOZCVlpc7bYOC+0zfIGYji8QxM2hnbm9KmLKBlg0OPk45iKuDLZ8DP2fucdPE402Ys1mEQxki3P7BwMh93OO4+5aDb05upigT0lZT6UH3ukihgTH4HMt29TkIHneHt+/0fH68aeJceRv3uT4S3Odh93jLpqdS+yGB59/Zv9x+0PR0d9/OucvAKLfhUh5fPg98nOQhY7z969u77WniWjRJnOYFKXm8MQs3O+2BINLHnZEtWpUqSvW5lY8/oXvg+8x5zDKkyF8qkrIC3weB68Zl2jp+Pnh9u5DAKB6Xcy9wnc/V+352HqOcKdzJZeAY/Lyq57Nxjvv9xKVscx9v6GN174vQ2fdlQ4KlHhgz+JeXnu7zUFGY7Z6DPBduU85Z3U48Z0Pc65QW2L94jPxcBO4P9zlPE/uV+5fby+dG3ptivfJ94T7GQH/nfuHHzd//3jkoz5PYls/TaRPXO3Bd1WPI/aZy2Avsg88n5HtWm0FWnxtpZy4/t+555ex2n/9BYl2qKCvK3HO0PWbxM8E5Bj9Oef0Z/4yTx8vYEvj+S3PWJYYXcIWmlxshriEZ56PRxx+VbVxDYIwRBMbGS78uthurIQLjf1xxY40/FJYddl/W5Pqa1ZvFAMbL/BsyD7Ry8JUDoxoYOQikOr+JVxcY3R/KwWMZgdEJivp26jKHRp4BLVoxyDgWl2pgYhwGZFvobEeqEzCdfaQ3DQZG5disaMUC57H3oJzAS1veeTiDmZiFdQKbG+7SxHHkecjHGDKghpxXWmDwc8NhTYFRfw6SB6d7bbYZQ32GUZTOcyyDp0oNjHzNQ9bxsbdkiMcqnqNAOz/vwf0HtleCgTymGhjlNhVV+7zgkrkteDx11k3fXrQPDg3FLOR8ZynB48JgALQFxmAA1wNjD2dQD8yqiRl28zhGYNS+d9OcX1rcX6RkyGwanDlzvsfU85F/AsG/jIUERstjzVwXDOz8y0u/QJ3/dEQPjO6MbuBecr7/SuXjPxa8VlzqgXFjZZXXtzjf/YVED4wizDnnJ/9kRZWu1NXvO2tgvNC9DuovIuoMY07PHm5o89p6iMesHkPo2jtkH/zzIOR7VguM6nMjudfePS/9+V/YM/h82R5zqfM4+Xnj7cT3jLPtGJ6ZlT9PnO93+cuSOL+DyvdFGPQQ15D0c9Hp44/KNq4hMMZIXQIj+JPtxopGYPx1l7H066Q36ddd0+g/bnB/I//Nrf2pyWXXGn1dGcFZocAgstEZcCsqj4iBVg+MPNBUHHN/sCakrRLb6CFAhMVR8mUu/gEbmL106qmBtuIvx9C01ftEnWcE9bDEs3T8Q1/OUunH4t/m+Ye0uo0aJkuVv/VS18kf8PLYO1dnGNuq2/EgIWaBHMWV/Ly4A0Hqoh3EYSFHzjAqgVHup+IYHys0MI5ZsU88f8GZrSo3XIiBjgdFeU5uvXibG2zV51iqLjDyLJX62NTtRXgKHFc+R3xteZCWsyVSai4/Rne2VJw3PybefyKHWyd47i8Xz4EaGNVteB+lZeVKwAy9Lvr23rny86wGscC28rkoFdfB3acaGOU5yuclec5m95y1wOi2VbnXrE+GqId8v5ZsrjUwcj93vXudCnLHGIGRz4dnpvLE43T7h84whj7WIlEPvc4FfC9q26jnpQZGvu78fHuz3tUERv4FSs5c8j1Zun9VMDCKssq5P9y6vJ58j8rt1ccT8n0X+L4Ifq8Fzjcx053x8/bhfn+G9HGeO/Fzp9y9p9VjNEkcI+p5M5WXgBOzQ79nZWCsdLcJKzAG+svvJfl82R5zgnNN3V+GBnm/AHCfjKXu/cQzqN6f7VQF9xkuNcC9XPS/FPz6byPgqfiLy/veMNfZ2Prp56LTxx+VbVwLPzA2a07NW7am2+++h664tgV1e7inaH95whs0+pVJoj520hSB+44cO1G0DX1hHN3zUA/RntynH3VOekjUH3ykt7vNxDe9/XN7n6efoxatbwnuSz+POIHAGD9sN1ZUAuNdo4w2Doz/3nuh0d54TTN+oEfFlA2kBxcIn3gZ/ZgT4spDgyhER7ITaooP7hOBV18XM7Pc0G60O6ZtKqeCrMBsXrV/19g4nOvPCT3EsbWfuyX97b9EcCT6p1juv+t/vD78tTcQLWXbzKJ/iuUWTp3XcdtZpV+2dhz9XHT6+KOyjWvhB0bHM0NHOkFwAj3W7xl64dV06vv0YG8dB0kZEns4wZDrL6Sli2UOlVdcd4Ooc2Dk8vlRL1OLm9tS69s6eH245DDKgVE/drxBYIwfthsrGoHx357daLSJwNh3sdEOAACxp4fF0MD4d1H+uZJoeeahkHAo67KvCIdFpwPr/hkSGPV+kn4uOn38UdnGtYgC46hXJtGTzw4VJYdFDo5yHQfGUeMm0YDnUsUyB8CBw0aHbD/i5QkiMHZ5MJkubdZc7IdnEXs9+TS9OP510QeBMUi/uOBPthsrGoGR/dvT31CTiy6h/0joRr8aeZB+ff9Uow8AAPiDHuLUcCcD469GFYsQ+N2fg31sgZH+8Q+3rPwbffcPd72tn6Sfi04ff1S2cS2iwMih8Krrb6SOXZNEsOO2F1+dTKkvvSrqcoax/+BUr86zjMkpT7gvSTulnGFkHBTFduMmei9Jcx+8JO3SLy74k+3GilpgfGYt/foB912ttTH/vql+ZLxYw+ewRcD28SY1i87jqYl+jqFvuAEAqJke4qrDs4x6G2sx52TIcv+cEq9+34zq+zH9XHT6+KOyjWsRBUaoPwiM8cN2Y0UrMPLHNPwm8UmzXde1NxXnu2+MKFqdSXnqO/t6ZlPOxEHBP2AvOSI+g7Di2Abx2W78d0kJszZTmvLO5eLdS2nh7sBHZRRmi3f2cl8OpWO+LKGU7k7fcvePxBm/KzW5azv3TTdjV9OaOWOCx3OOk7Z0X0gYK1qXSZlb3P2Xlh9xz2P3AvGBxvyRG+67KN3AKD9uhf+4n/v1G5xOmX2aUkF5FSV17x8SlOW7L/k8+B2mYr/8xh7lTQxifXlJ8LPd+ix1QvEg7xz5zQMJzvPJHyEyLb9EfI6b2iaPBQCg00OczcItv9BgJfzVF/1cdPr4o7KNawiMMYLAGD9sN1bUAmMERHAKBCImP+Yl+A5c912FbnALhiwR7ALvMC0KvJPZfNem8i5KfudggNyHfDei+i5W91yCx1EDI/ctLnTfRSnfHcvbJoxyP8fRDZvutvzuZnWmT36MTvA8guvcz4hzPydQvlNSPH4tMMpjeutlfWzgXZ3l7jt+5XHVNtkXAECnh7iGpJ+LTh9/VLZxDYExRhAY44ftxvJDYKwIfBh0bTOMMriJj5JZtFrMnvEHHScl8syePTDybF1O7gLHNDHDmCpmJoPH4M/p4//+YQZGnmHcTBmrjyiBsQctnNibdpa7x1IDI38WYvtEOdMpw1m69xl7fK58HhlpPcQMozeDKB8r9wmE3pAZRmcfa7LSnUDsnrMaGHmGMdN5fuQ5cgBNfjFThMOkhfvEDKPapn7YLwCA6lejfjSCXMP40TgXnT7+qGzjGgJjjCAwxg/bjeWHwBipvHT3bxP1z0D0ncTAf9EI086F5of1AgCc7/TxR2Ub1xAYYwSBMX7YbqzGGBgBAOD8oY8/Ktu4hsAYIwiM8cN2YyEwAgCAn+njj8o2riEwxggCY/yw3VgIjAAA4Gf6+KOyjWsIjDHSEIGxNN/9vL7kRfui/q/Wzud3i9puLARGAADwM338UdnGtYgC4ysTJ9Hr098yPNwrxegLNatrYNyw6TujberMmUYbmxb4XDv5rlF+p2lpZRVN6+Oulx+PIt8tW7Ct3GtjReVV4h/e56W1E+96ddvTxT+bl+v43aLL+CNGKt1jyfaNc/ifybvvppUfi1Ld/x1t7Gw3FgIjAAD4mT7+qGzjWkSBsTqjx71itEHN6hoYm17VjK5r1dpb/nrdOqOPqvjwEfEZdPyRJDk93Tbvw4y1wLgmPXTbikr3H93z9u7n2TWl9PxACA2sa9/dfQeqnGHcuYiDohtOOTDKj2OZJsp23mcBxhPbjYXACAAAfqaPPyrbuFYvgbHrg8F/9yeVlJXRsNEv0JmffzbWqbLm54YsJ6f0MfqEY2thodHmZ3UNjIz/LePBI0fou4KtxjqdN6snPwtPadMDoy3MrSk8QqXb3H78Erf6kSvpWau8fcnAuGys+x9AmPxgaA6MbnC0H6Oxs91YCIwAAOBn+vijso1rEQfGS5o1p2sSWoW02QLjcScwyvqA556n3fv30wM9H6W9B4powutvUMqT/enk6dMiME7PyKDyykrR99CxY7Rk5Upq7hyjuOQEDR4+gr7fto2Wr8qjb9avp01bCkS/0vJy6t3/KbHd+PTJIjB+V1BAiXfcRRs3bzbOx2/OJTBGQn0ZmD9YOXPRBirICc4C8gc1VxcYeX3q9AVeYOSXpd2ZQnddxkT338iJ5XI3SIr2OdmBfxOHwKjfhLXR9w0AAFDf/v23vzXGH5VtXIs4MHIgkHX5N4wf5Hxk9FMDY9+nnqbczxaJcCfbz/7yi2iTM4xfrlkTsj23y1lD3mbcxNfENhw8uU2ue/PtGd5yUrL7HyEGpw43zsdvGiow1if+l2x6G9RvYAQAAIg127gWcWC86vob6fJrW4S02WYYeQZw/sJPvZlDfomaX27m8PfJosX01PND6NTZs0ZgLDpyhJZ9scqYYdy+ezdNmTGTjp04IfrJwMj759DIyz8eLaZH+j4u+urn4zeNMTCCne3GQmAEAIDGyjauRRwYbYaMHGW0Qc0QGOOH7cZCYAQAgMbKNq7VS2CEyCEwxg/bjYXACAAAjZVtXENgjBEExvhhu7HqGhj1fQMAANQ3fezR2cY1BMYYQWCMH7YbC4ERAAD86j/+eJEx/qhs4xoCY4wgMMYP242FwAgAAH6mjz8q27iGwBgjCIzxw3ZjITACAICf6eOPyjauITDGCAJj/LDdWAiMAADgZ/r4o7KNawiMMYLAGD9sNxYCIwAA+Jk+/qhs4xoCY4wgMMYP242FwAgAAH6mjz8q27iGwBgjCIzxw3ZjITACAICf6eOPyjauITDGSLQD47Utb6LN27bTtsKd1Ob2DsZ6qD+2GwuBEQAA/Ewff1S2ca1OgfHTJUvp5KnT9Opr6cY6CE80A+M1CS3pnTlzaeacOeJ/cY+f/DrdeuddRj+oH7YbC4ERAAD8TB9/VLZxLaLAeH3rNtT61tuptLxcLHNwXPbFKqMf1C6agZG3bZ7Qylu+v8cjRh8pbdU+qqiqopxR7Yx1NhVVO4y2uqioKlHqVUK/RGd57Gpak670K1kdst3w291yyco8+vCNvqL+7Lt5xv4bku3Gik5gzPaeK2aud8l1mdvKaeGQpuI5rSjMDlkHAADnN338UdnGtYgC47iJr4nyGieMcLn/0CFR8iCk92WHf/rJqx8vKxOzXeWVlWL5dKBkZWfOePU3355BXR54kBavWOG1PTNkGM3OfI9SXxhDeV+vNo5j0+uJJ402P4lWYFy0/HNRZn/8ide2Nj9flDv37TP6V+xeELrsXMvS/atEfWHODsob25SWDXbXleZPCwS4dm5oqXRDX97+ci+IyACqHyfEEGf/UzZ4y8Wr0wLHLhHhpiiwfc7uqtDA2GW8KIdkBQJi9ymBdW5wjBXbjRW1wKgFaH6uN5a4AXJaH+daBOr8XGYWVonrJwNmZqA/b5fwTIaoF+8P7C9xjNcv2TguAADEG338UdnGtYgCo256RoYobS9NpzzZX8xyvTcvWyxzYORy4ZIlosz9bBElJfeg0eNeoa2Fhd527Tt3ob0HiqhT125eG/d5Z+5cb/nD3I/pqeeHiJnO5JQ+tHn7dnGsZ4cOowHPPS/qWfNzad/BgyKkcim32b5rl9jHgcOH6aOFC43zbijRCowlp07Rl2vWUHFJiSgZh3Muqwtya/aXUPGmTErPL6d+gwdRv5lumOOwwaUIchzyuO4Elp3afjJ4G0dBjhMqnXUp3dXZykwqLSunje8F+3MfLncu7OHus7Jc9MlLaycCY5OebojlWbGQgDRgliinrpQzigO9dR2V82lothsraoExEOrktfSC+rpgaJelDIy2GUZZZmwJhkp5nH59uliODQAA8UQff1S2ce2cAuMbb70tymGjXzDWFZecECGRByJe5joHu34DB4llDnTch2cX1cB47MQJmvZOhgh/+j4Zz2qeOns2OBviBEa5rsQ5xvHSUm//cgaU6dt8v22bN9sZC9EKjENHjRbllBkzvbYlK1aIkv+uUe/Ps4Zc8qxeQk7g5eaxmaKUgbFJ+gYqrioXdQ5wPIvlbp8qyjVT3ICY3LUpLXzPnS0syDLPTdo4yy3lTKKcYRQ4MPJxtgTKkBm1ZFG2HP2RKAfMdmdTgzONsWG7saIWGC0zjKLuXDs9DNYWGDmks50rxjhtXai0MhBGj4UeAwAA4o8+/qhs41pEgXFgIMTJl6R5lo5LGQpVm7YUiHJ8+mRRyhlGiQMd//3jhNffCAmMclZQ3efr098SM5Xc9y/ffCNmC0e+PFbMnKmBkds/WbTY27/c1+79+71tvlq7VqzftW8ffbZ0Wcg5NaRoBUa2fFUe/WfTS7zlK6+7njLedUOgDc8OestdexvrbZKdbRKUZXVWMZozVEuyx4ryguZtgm0r3QAZK7YbK2qBsWwH5eQuELitusDYb3DvYGB80QmMJRvE9VL7JCU2pZ3lVbRsSGAb/hvSru5L0+axAQAgnujjj8o2rkUUGO9OeoCuuv5GKjpyRCx/ve5bejfrQ6Mf1C6agZGJGaTycvrx6FEEgCiz3VjRCYzhC/2zgKbWXwRCflHgbcSfFpj9AAAg/ujjj8o2rkUUGKVDxcUihKz4y1+MdRCeaAdGaDi2GyvWgREAAKAm+vijso1rdQqMcO4QGOOH7cZCYAQAAD/Txx+VbVxDYIwRBMb4YbuxEBgBAMDP9PFHZRvXEBhjBIExfthuLARGAADwM338UdnGNQTGGEFgjB+2GwuBEQAA/Ewff1S2cQ2BMUYQGOOH7cZCYAQAAD/Txx+VbVxDYIwRBMb4YbuxEBgBAMDP9PFHZRvXEBhjBIExfthuLARGAADwM338UdnGNQTGGKkuMHZKetir6xcX/Ml2YyEwAgCAn+njj8o2riEwxggCY/yw3VgIjAAA4Gf6+KOyjWsRB8bTFRXiv7zw/4HW10H4ohUYX3p1PH25Zo3Vh/Nzjf5w7mw3FgIjAAD4mT7+qGzjWkSB8f6ej3j19Zs20eYffjD6QHiiFRjl/42e+MabwrUtb6I/XHZFyLqQ/iWrA/U0Y50qoXt/oy2oBbXh8tI2tGTlguDyecJ2YyEwAgCAn+njj8o2rtU5MG747jtRcnDU+7HjZWVGGwRFOzDa2NbpgTFh1ALRLzWR27q4s8lp7UTJfdNW7TP20zGNQ2JTanFp00BgbErz05ONY8Ur242FwAgAAH6mjz8q27hW58BYGzUw7jt4kN6bl+21/XTyJH0wf754mfTk6dPU/bEUGv/6G8Y+4plvAmPZDsrJXeBY5S4fdssip2/CrM20bE66WB6zukSUpU57Svd2Ifvo+06eV5eBcUnueONY8cp2YyEwAgCAn+njj8o2rkUUGK+47nqv/smixcZ6lRoY9x86JMrklD4hJQfG16e/JYJM84RWxj7iWbQDo5gRDNTb3N4hZF1If22GsaLqiFcmpWWKOodEGRgXvuf2K8hS9tN9ileXgXHqgMuNY8Ur242FwAgAAH6mjz8q27gWUWBk23ftEuWps2fpqutvpLYd7zD6sNLycpq/8FOanpFhzDCe/eUX2rF7jwiMpysr6fkRI+ntWbONfcSzaAdGm5rWqfoNDv69Yr/Bg7x6ctdAW58uxjaZYzp69cufe9dYH89sNxYCIwAA+Jk+/qhs41rEgZHd0qET3Z30QJ3fKZ372SIxo3i+hURVtAIjv8FFf3e0dOk11xr94dzZbqxoBcY2nbrQrZ3vAwAAsOJxQh87bPTxR2Ub1+oUGOHcRSswQsOz3VjRCIxNr8L3BABAXVx3y+1GW6xddHVzo62+hDNe6OOPyjauITDGCAJj/LDdWNEIjAAAUDfnW2AMhz7+qGzjGgJjjCAwxg/bjYXACADgHwiMJn38UdnGNQTGGEFgjB+2GwuBEQDAPxAYTfr4o7KNawiMMYLAGD9sNxYCIwCAfyAwmvTxR2Ub1xAYYwSBMX7YbiwERgAA/0BgNOnjj8o2riEwxkh1gVGlX1zwJ9uNFW+BsesDD3n1xE53Guvh/HDnvUlGW6x17HKP+KcSXO983/0h36uynfvo20WLeny1Hmt+OpdrW7Wm3118qVfX10dDOIFRfp801DkhMEJYEBjjh+3GirfAuH33HpqV+b6oL1qxUpTqAHTRlVeLkgOFrHMp6xIP6Nt27Tb2D43D6g35NCbtVW9ZHVj1XyTkMn/v6PupL2v/ukmU/A8k+Lw2/7BDLH+5dp0on35+iCj/smatsW20bPh+s1fP37zFq9906+1eXb1f9O2j4f2c+aJc/91m+tP7WV67ek5MXjO9vb6NnTjJ+znAddkuA5v6vNWXcAKjvHYNdU4IjBAWBMb4Ybux4jEwfrb8c1HnwNj3qadFnX+IygFoy45CUfIgzgN4+7u7Uo8+fb1QwW2/vehi8QM4miECoqPTPd1CAv/q9RtEyd8DMpAsW5UnwsbQ0WOc75FnxLWP5rWWAVFf3rR1myhjERj5fuDn4+NFi71frtKnvSVm1EaNHWfcLw1xbt9t2+6FIXn8SVOminOSy3ztuByUOoIua35dVGckOZDx7O/Wnbu8cCaPz//YQ4YzXs/XkIPuyq++NvYTiXACIz8XDXlOCIwQFgTG+GG7seIxMHL50aefiUHww9xPRHDgAVoOOHKw5gGQf6DyNkwfeDp27WbsH/yPAxAPmjIwyuvObXzN5fXmwMjXnHE9moFRhi6Jvwf5fB570v33prEKjBwq+HmSgVE+N7zOdr/o+4gGntXcuKXAO776SgFfJ9leULhThEv53EWDDGQcpMdNek3U5XPEz4cMZ/xL6pKVX4jz4edU308kwg2MDXlOCIwQlmgGxptuvU3832jVvQ93N/rFWscxWZTcTGt76SOjn9/Zbqx4DYxzsj4UAw3/oOz37OBqAyOX32zIpxV/+dL7WyUJgbFxkoNji5tupsHDR4pAJAfSBx/pJf5kgQOcLTDybPPnzvcCby+/l3IWfGocI1LPDksV32f8vcezYvqMIx9r4dJlIijJNp71nDLzHVryxSqvj77fc8H3w4w5c8VL5DKUcQibOeddMTNvu1/kcyHPRT5X9YWPP/fDefTJ4qUiEL0yKV3M+PPMGa/jPvK8vlr3La388isRGOU6fv44hMsgfq7Ul3zlY+bvp7T0yfTWrD+JP33gmU6+Vlzv3f8pysr9WPTj54pncPl68zbh/r1huIGRy0jPSfbn7yn+3gr3nBAYISzRCowt2yYafzfG+KVAW2jM2V9O6S8Oop3lVcY63RhLW8aL4f3PSpslueNFOXVxHl1wVUv68CU3SAxpa/b1M9uNFW+BEUC37q+bxC8DMngB+Fk4gbGhITAGDB4+gk6dPStKfR1ELzDybKLeVtO64i/HhCyXOn36DU6ngqwelFlYRWmDBznblVOyU05zDFpxhFL7dHHajrj7LMymvJIqShX99jltabRwYn8qDhyrouQIJSU6x8nPpMwt5SHHGtPFLeenJ4tyxkr370WWvDPQOE8/s91YCIwAAP6BwGjSxx+VbVyLKDB+ve5bz1dr13ltL0+YaPRlHBi53H/oEG3evp2SknvQB/Pn0+GffhLtx8vK6L152ZSc0odOV1bS8yNG0rR3MmjvgSJKvOMuWr4qz9hnvIh2YFT/buySZu43pTUwrk4LWS7IkfspEYGR6xwIueQZxoRRC8R+vEAYCIxiW6eNt5Evg4ttxwb2e6ycKipLQo6lB8bZMjDOfj6kn9/ZbiwERgAA/0BgNOnjj8o2rkUUGF+f/pag1llySm+jL1MDI5fNE1qJILHnwAGxzEFR9pUhg/s+8cxAUe/+WIqxz3jhl8CYWVhOC+ekU3Glu06fYeQ2GQiXTRxEOburqH1iD29femDkGca8OWOoINAmA2PR6kzK2RYaGJcsfVuUExbkUcu2D1Dm6I5iue+l5uPyM9uNhcAIAOAfCIwmffxR2ca1iAJjpPTAOHrcK/Ts0GF0uqJCLMsZRp555BnGYaNfoLyvV1OJ057yZH/6Zv16Y5/xIlqBkf/QWoZv3fs5OUb/mLqqJV2uhcOmLW81+/mc7cZCYAQA8A8ERpM+/qhs41pUAyNUL1qBERqe7cZCYAQA8A8ERpM+/qhs4xoCY4wgMMYP242FwAgA4B8IjCZ9/FHZxjUExhhBYIwfthsrGoHx1s73AQBAHdzU/i6jLdZad7zbaKtP+hii08cflW1cQ2CMEQTG+GG7saIRGAEgtvw4S+VHfnye/HhOmGGEsCAwxg/bjYXACBB//Bg6/MiPz5MfzwmBEcKCwBg/bDcWAiNA/PFj6PAjPz5PfjwnBEYICwJj/FBvLONvSH5/gXEj1kTfNwD4hx9Dhx/58Xny4zkhMEJYEBjjR42B8YI/GDdiTfR9A4B/+DF0+JEfnyc/nhMCI4QFgTF+IDACnB/8GDr8yI/Pkx/PCYERwoLAGD/8GBifG/mS0QYA58aPocOP/Pg8+fGcEBghLNEOjEeOH/f+JWDJqVPGeqg/fgyMHbrcR1dcd4PRXlf3JfeisRPfFBJuMf99Y9t3zhhtquuenU8Xd+hNiXP/S2ibcZZ+e8mVon7F/S+E9L3g+tsocc4/qM20YrF8edIo0a/JhReH9Lu4/WOinfejtjd7bGqgf1Oxj8Q5fxf1i265X7T/4cZOIf0hPP0HDRY/T4aOGu218b90lfW01ybTlh9+MLaLJ34MHX7kx+fJj+eEwAhhiXZg1P+P9B8uu8LoE88u7/e20TY/O91oqw9+CYxPDHye+g0aJvDy2ElTQpbPhQyLkr7+pomF9Lsrr6cbRuRZQxzjwOjWL6Y/3tSFLusySCzf/PoBoy+7pNPjorwhdYUo284M/cWnVdoWt90Jn/q23Mbno7eJspZwC3byf9GXlpeL8t6Hu9NrU6aG9EFgBObH58mP53ReBMbikhMihLTvXHPggepFOzDqqguMFZVV1rqUV6K2taME7ley2ugXkZwdouyXaFmnKMjhsovRHo4lK2e55UdTqHPqu6J++ZAso1998EtgZC+khYbiS5pd63wvnfsPpXADo1zmcNfypfV0y1slXpsMjGrw+/3VLemPrTrTf17WjG4c9aWYTeT2i9o9RO1mVYj6FQ+McbdzAh+v537c/9qnPhDtfAyebeT23ze7yevLx+NgysdgLcdupCsffkWEWv38ITyTp02nth2CM7QIjGDjx+fJj+cUbmAs3LNHlOs25IvypbTxRp+60Mcf1TkHxo5d7jHabr2zs9HG+KWKR/o+Ln4b1depvlyzRpSnzp411kmDh48QkpJ7GOtY2Zkz1np1ej3xJB0vKzPaJT6W3lbffBMYnfC3cU47UZ821g2CFVXl1O/FTMob6wbGjBcHiV8QeN2YwDZJWTuoaF0mLdztzjawhFmbKW1Aj0DfNCo9uJoy1h1x9+l8H/QbPIhKt2R4gZH336RnNuVMHETFYptUWjNnDG0sq6KE7v1p5yKegUqznlPqYD6nfdRkyCoqzs+kzC3B82BTB3DZ11vOHM0vo3YO6VNf/BQYWYcu93r15i1bG+vrItzAeEEL9+Xq1ul7jT5uYLyY/tjyTrHMs5CXdHrC6Ndu9i+ivODaW0T/NtOOuccYvy2kn5wxbDPF/R7T1/324ivo983biONccG1bJ1iecNfNKDP6Q+2GjBxN3R9LCWlDYAQbPz5PfjyncANjtOjjj+qcA+PeooPU4e6uIhDw8q59+0Q57Z0Mo++Zn3/26hNef4NW/PnPXp3D4ciXx9Lbs2bT2vx88bcxZ3/5RQS1/O+/p2GjX6BxE18ToZPX8W+1WfNz6c23Z4jZTe73/bZt3v6/WruWnh06jFKe7O8FUA6E783LpuSUPnTy9Gmxzfbdu8U63leJs77bQ93FMcanT6bXp79F+w8dcgbDSWI99zt07Bgt+2KV93j4nHlf+mOtCz8FxiLneubsdgJbIDCKIMfrqnYEZxgDIU8GRg548uVubhN9+mSI5aIyNzDKY/D+KgqzRV0EQyUw6jOYvH3BfndWyp1hdPdjO6eCQIgtOFZOFZXBmSxWXWC8QOlTX/TAmD71bUrq2TtmgZHxTON/Nr2EUvoPNNbVxYVXXFVtWJTkDKMMjedCf0nbDY9mvwtaJBptpuDfPv7hhvaW9XCu1FnHeObH0OFHfnye/HhOcR0YZVCUM31jXkkLabcpdwIZlxz0ZJjjYMYlL+szjLyOyTDCbRz2ZGDcWlhoHIP3wTOZHALl/jgocsn95b7lrCLvS9Z5n3KdPC8ZGOU63pdsk/s/Vw0dGH9/yWVGG3NfXnaC3pZMLzDqs3nVzTAWb1tAGauDsztp68opKbGLN8NYzDOM+W6Q45e7a51h7LmA0vp0odLAsUq3cMi0zzByGwfGpIX7qGh1JuVsCw2MS1Z+5JaLs2jAjMWi3nmSW9Y3PTAe+PFQzGYY/7PppdT36edE/XcXXyr+jlHvEy08o6e3AcQTP4YOP/Lj8+THc4rrwLj/xx/pqeeH0OpvvxUvTfTu/5RonzJjptGXZ+Q46MmXpHn278ejxe5+lMD4yaLFYhZRDYw8w8hhTYa6+Z9+Zswwbty82TsW72duVpaYUbTNMNoCI5+LbYZRrudSDYz8OL5au44OHD4c8jjrKtqBkUMbvzt687btol5dYIye4AwjO+e/e4zUpS2MtpZtzLb6oAdGNnbi6zEJjAAQPX4MHX7kx+fJj+cU14Gx9a23G23hvvGFA2O4ff1o9/79ojx24oSxri4aIjCq9PVQf2yBMVYzjAAQPX4MHX7kx+fJj+cU14ER6k+0AyM0HARGgPODH0OHH/nxefLjOSEwQlgQGOMHAiPA+cGPocOP/Pg8+fGcEBghLAiM8aOhAmOzhPr5iBwAqBs/hg4/8uPz5MdzimZgbHpV7RlCH39UCIw+gsAYPxoqMLI2nboYxwAAAJB4nNDHDht9/FEhMPoIAmP8aMjACAAAUB/08UeFwOgjCIzxA4ERAAAaG338USEw+ggCY/xQb6zb7k4KCYz//tvfGjdiTfR9AwAARIM+/qgQGH0EgTF+2G4seXPpN2Ft9H0DAABEgz7+qGzjGgJjjCAwxg/bjYXACAAAfqaPPyrbuIbAGCMIjPHDdmMhMAIAgJ/p44/KNq4hMMZItAJj0eEjRpt0Pv+LwMv7vW20zc9ON9rqwnZjITACAICf6eOPyjauRRwYOXSoy0tWrjT6QO2iFRhrCoW2dRUlG6jf4DFUUb7ZWNeQ8sY2pcysaUa7qiCHy/A+X0q3ZOUst/xoCnVOfVfULx+SZfSrC9uNhcAIAAB+po8/Ktu4FlFgVMPiuvyNXn16RobRlx3+6SevfursWWO9tP/QIaMt3vknMK52SxEY06h421KxXLQ6k/IOlot6umNnYNuKsg2UsaWK2l/Yjooq3badS9NpzbHA+vISSu7q7jth1mZKG9AjcNw0Kj24mjLWuTOgFeXlTlAdRKWB/XJgrKgqoSY9syln4iAqFu2ptGbOGNpYVkUJ3fvTzkWDxH7cx+Js/2Km2I7bivIzvXModuqZW9xzl6YO4LKvt5w5+lan7BzSp65sNxYCIwAA+Jk+/qhs41pEgXHdxr969Q3ffefVN20pMPqmPNmfmie0ovfmZYtlDozJKX1o6sx3qNQJC9xWXHKCevTuQwePHBV9p8yYSSdOnTL2FY/8FhjdgOaGsSY5O7z1mdxn/1InrPVwZwETnfbEQWJfpftXi75cl/t2ZwED+mSI9qIyZd8XBsJhYba7PNY9vgyMeSXqObYT2xfsL1H27e7HDYq8DZ+r3Le7z4Jj5VRR6W4jVRcYL1D61JXtxkJgBAAAP9PHH5VtXKtzYOz+WIpXtwVGDoPHy8q8WUkOjFsLC71wwW1vvj1DlHKGkYPkjt17jH3FI98ExrIdlJO7QMzYqaFOnWFcdjgwexjYfo0TAJO696aicneZ++ZsU0OdK21dOSUldglsl0bFPMOY7/arqKyqfYax5wJK69PF61O6hQOhfYbRPaYbGNXzkZas/MgtF2fRgBmLRb3zJLc8V7YbC4ERAAD8TB9/VLZxLaLAeLqiwqurM4yLln9u9JUhcnz6ZFHKGUaecZQvVcvAePLUaTEj+cZbb4uQqe8rHkUrMO7Yvdtok2yBseEEwyiTM5sN5tIWRlvLNmZbXdhuLARGAADwM338UdnGtYgCI5MvJ0tfr/vW6AO1i1ZghIZnu7EQGAEAwM/08UdlG9ciDoxQPxAY44ftxkJgBAAAP9PHH5VtXENgjBEExvhhu7EQGAEAwM/08UdlG9cQGGMEgTF+2G4sBEYAAPAzffxR2cY1BMYYQWCMH7YbC4ERAAD8TB9/VLZxDYExRhAY44ftxkJgBAAAP9PHH5VtXENgjBEExvhhu7EQGAEAwM/08UdlG9cQGGMEgTF+2G4sBEYAAPAzffxR2cY1BMYYQWCMH7YbC4ERAAD8TB9/VLZxDYExRhAY44ftxkJgBAAAv7i1830h2t55jzH+qGzjGgJjjCAwxg/bjYXACAAAfqEHRqaPPyrbuBZRYCwpKxP/j/iduXPF8tbCQrH81dp1Rl+oWUMERr42sf3/0bGR3Cx0udf0xUaf+mS7sRAYAQDAL/SwGPXAKC1esSJkueuDDxl9oGbRDIy2kGhrk+1J3ftTRfkOY11Iv5LVohxjWSfxun5Tso32ukids0CUNR3PZsCcPFF+uDKPLmjekab2ayGWky1964vtxkJgBAAAv9DDoq8C4/GyMqONZyT1Npsv16wx2qpjO05jEO3AyAYPH0F33Zsk6mVnztDvLr7U2lfWB606IsqF+7ktjYryM2nNMa53cQLjBrGudPdSWri7XNSTsnZQap8ezj5KKHnwIJrmyCx091dRsoPScndQkjxWzg7KGO70LSuh9l17U9HSQWL74m0LKGdbibtNeTn1G5xOa9KbUl5JlbdP7pfmlBVV7nGLD26gBKfcuTSd8g5X0bTE4ONZstINmrOHuEHxw5Wfu2VaN69PfbPdWAiMAADgF3pYjHpgvL51G/p63bchgZGXqwuMb749gz6YP59KnSDQvnMX2rF7D/UfNJhOnj5Nw0a/QEdLSqjbQ93pu4ICIfGOu2jj5s20Nj9f9Dvz88/07NBhdOrsWbHPrPm53r7fm5dNvfsPEC+TN09o5a3jkCS3Ky45QSlP9qe/fPONcX6xFq3AeLqyUoTAVu1u9do6dukqAmN1s4xMruOwVlHIs4RpgXXujGHoDKO7rjgQTOW2vM4NjHJbRY47g8nbiP05x5B1ljc2eIzi1WkiMMp9ev0C+5CzjkVOn4qyfSHH0QPjfARGAAA4z+lhMeqBUQp3hpEDI9c5zHGQkzOMMgDmfb1aBJz9hw5RUjLPVFXR4NTh3gyj7KcHxuSUPiHHUdfxcWR/GWbksp9EKzAy+bg5eGd//AkdPnashhlGntUb470kXRqYxTMCY5U7+6gGRjnzVxoIdMsmmjOMPBMo9mMJjMYMoyUw8j71GUYZGAty0ynvYDnl9Aw+nuQpbkCcvTKPWt7RlyY/drmz3II6yvOIAtuNhcAIAAB+oYfFRhcYueSZRA6MPx4tpkf6Pk7bd++mTxYtFu2yH68b+fJYMSMp980zjBwyuQ/PMHLbN+vXhwRGnmHk5X0HDxrnF2vRDIzlTgjX22qaXVSps36N1eWXasttgrOt0WC7sRAYAQDAL2RIfPX1qf4LjFCzaAZGaFi2GwuBEQAA/IID4pQZs+ie7r0aJjDKlzrlS8Y8k8XLh44dM/pCzRAY44ftxkJgBAAAv+CA2M0Ji2MnTm6YwAj1B4ExfthuLARGAADwCxkS73m4gWYYof4gMMYP242FwAgAAH4hQ6JKH39UtnENgTFGEBjjh+3GQmAEAAC/0MMiAmMjgsAYP2w3FgIjAAD4hR4WERgbEQTG+GG7sRAYAQDAL/SwiMDYiCAwxg/bjYXACAAAfqGHRQTGRgSBMX7YbiwERgAA8As9LCIwNiIIjPHDdmMhMAIAgF/oYRGBsRFpiMA44sWXKX3qVKMd6pftxkJgBAAAv7ix7e0hYfGPl19ljD8q27hW58A4f+GnRhuEL9qB8eTp0179yPHjxno/GHK72Tau++VGm9/ZbiwERgAA8DN9/FHZxrWIAuPtne8W5Z4DB8S/BJzzQRb1feppox/ULpqB8c5u94lS/itHrrdo3cboxzbOckvZrzhQmtJClscY6+0Kcsw21nnS4kC9BU3o05FmLM4Ty7NXumVjYruxEBgBAMDP9PFHZRvXIgqM7HhZmSjXb9pEKU/2p30HDxp91H6l5eXGulNnzxptkZD/y7oxi2ZgZDIA6nVdRdU+atJzKSXk7BDLpfnTqKC8ivoNHkSl27KpidO+JiudZGCsOLZBlBwYk7J2UJrTr6KqXLQVrcukzC1uvaJ8H6XO2SAC47LDVZRwYRcqWpHqHffDQDBMnvJ5oO1yaumUt760wDhHv7PdWAiMAADgZ/r4o7KNaxEFxsubXyfKRcuW0yN9H6fd+/dTckpvox/jwHi6slLUk1P60NbCQlHPmp8rAuOw0S+Il025bcnKlXTg8GFRP3HqFHV7qLvoM/LlsfT2rNmU9/VqEU65D69bm59vbMdtm7YUGOfhV34JjJmFVZRX4q5Pv7AHJXH/wmyxXMDbBYIkB8aKyuB+ODB6s5GBPnyc4sJ93nqxD55h7Jou1qUmBo9rBsYWCIxNEBgBAKBh6OOPyjauRRQYr74hQZSLV6ygcRMm0clTp+nu+x8w+rGzv/xCHy1cSM0TWhmBUc4+chsvy5dO5Xou9x86JEqeTZTrZR9u07c7eOSoOB/9PPwqmoHxyuuuFyUH9rIzZ0T9dxdfavRzOUHw8CpRl4FQn2GU/bgsDYREc4axBy2c2Jt2lrvreYYxLXeHCIw7nW2Suven0nU8U+ket+XojwL1y2l2Wl+aHwiQsmxMbDcWAiMAAPiZPv6obONaRIGRbf7hBzHTyGFv6sx36GhJidGH6S9JlzvhJWfBQhH0eGZRnWH8au1a+m7rVlG3BUaeYeT+sg//DaW+nVpvDKIZGP+z6SX049Gj3vIPu3ZT0yuvNvrFWrOrzLbLLzXb/M52YyEwAgCAn+njj8o2rkUUGG/p0EmExeKSE2Jmj8Mdv2Ss94PaRTMwSstX5dGmggKjHeqX7cZCYAQAAD/Txx+VbVyLKDCq4uGNJ7HUEIERGobtxkJgBAAAP9PHH5VtXKtzYIRzg8AYP2w3FgIjAAD4mT7+qGzjGgJjjCAwxg/bjYXACAAAfqaPPyrbuIbAGCMIjPHDdmMhMAIAgJ/p44/KNq4hMMYIAmP8sN1YCIwAAOBn+vijso1rCIwxgsAYP2w3FgIjAAD4mT7+qGzjGgJjjCAwxg/bjYXACAAAfqaPPyrbuIbAGCMIjPHDdmMhMAIAgJ/p44/KNq4hMMZIXQPjb5peRf963cMQA/q1kGw3FgIjAAD4mT7+qGzjGgJjjNQ1MOohBhqOfi0k242FwAgAAH6mjz8q27iGwBgjCIyNj34tJNuNhcAIAAB+po8/Ktu4Vi+BcfS4V4w2qBkCY+OjXwvJdmMhMAIAgJ/p44/KNq7VS2Ds+uBDRltJWRkNHj6CTp4+bawDBMbGSL8Wku3GQmAEAAA/08cflW1ci1pgPO4ERi5PnnID4+nKSuo/aLAoR748lj7M/ZhOnDpFfZ96mtblb6RlX6wS/bjcvX+/qH+zfj1t37VL1EvLy2nsxEnGcRorBMbGR78Wku3GQmAEAAA/08cflW1ci3pgPHbihCj3Hzokyqz5uaI8dfasCIqFe/bQ0ZISbyayuOSE8ObbM6iiqkpITulDWwsLjWM0ZgiMjY9+LSTbjYXACAAAfqaPPyo5rrGHUx6n5q3bRS8w8ozg/IWf0pmffxbLMjCqM4y8zIFxfPpkmpuVJZY/W7qMdu3bJ+rfbd1KX61dK+oIjC49xFRn20//TUv/epgWrNtHO0/+n7EeIqdfCwmBEQAAGht9/FGpgVF1zoFxyMhRRhvULJqB8fvDfzPaVm45ZrRBZPRrISEwAgBAY6OPPyo9KNZbYITIXXtLe0FvV+kXl+khRvfYi3ONNmncu18YbRA+/VpICIwAANDY6OOPSg+KCIw+p19cpocYXcHRf3j1XaUUsk5fhsjo10JCYAQAgMZGH39UelBEYPQ5/eIyPcToZi39zmiTVhX8ZLRB+PRrISEwAgBAY6OPPyo9KCIw+px+cZkeYmyuuz9VlNlf7RS4/rtbnzD6QWT0ayEhMAIAQGOjjz8qPSgiMPqcfnGZHmJs2j02jgZMmOctd356Mj08fKbRDyKjXwsJgREAABobffxR6UERgdHn9IvL9BADDUe/FhICIwAANDb6+KPSgyICo8/pF5fpIQYajn4tJARGAABobPTxR6UHRQRGn9MvLtNDDDQc/VpICIwAANDY6OOPSg+KCIw+p19cpocYaDj6tZAQGAEAoLHRxx+VHhQRGH1Ov7hMDzHQcPRrISEwAgBAY6OPPyo9KNYpMGZ/soAqqqo87TrdafSB+qFfXKaHGGg4+rWQEBgBAKCx0ccflR4U6xQY1bAo6X3Y4OEjvHrv/k9Rckofo0/zhFZe/bOly6jbQ92NPucz/eIyPcToZu+oEuXkbVU0u6vbltvP7FffZiv1ihObjfU1mb3LPeeabF5gtjU0/VpItsB4x30PIjACAIBv6eOPSg+KdQqMM+e+G7JcXWA8dOwYte/cRdR/PFpMX65ZI+rPDBnm9eEQqQbJrPm5Xr1T127GPs83+sVleogxvUdXOmVF1WGqOJpP//reLtF+IH8Z5e49G9L36KZlNHub27byNbdtGG975iz1GjWVSrd9Rv+64ABt/mwe7TjjhrqKM8dpYNZm0e9fX9tMm7/4mO4YOpVynf5yv/w90WvUPFo/NxgGV57g8j064Bzz658C+6oKHEfs+z06umOtaN/xxbxgnzOHneNtF4Fx0dEq57ENpwN/nukdq7RoO930uLOt0++FLw4H9zthmXhMfNxXJ0ylYd+U0UOPj3X2d8DbNlL6tZDUm+nhlMe9sIjACAAAfqWPPyo9KEY1MB4vKxNBMSm5Bw0f85IIjPsPHRLr9h4oEuWE198Qs4yjx71Cp86e9QIj9+f2ISNHGfs9n+gXl+khxuboN3+ir2e6YWmHc3042MnZYBH0Ajb/dJYqKstEPSQw7vrC3Q9vu0AGrPe89VyKPq8FZxJtM4xH171nBEa3j7t/eUy3T2Cdczx5rurxxAxj8jzRPjAwc6ruw52BdPch2yqqDgSO64ZYdb91oV8LSb+hVPpNWBt93wAAANGgjz8qfSyLemD8Zv16OlRcLF6e5sB48vRpsW7ZF6tEKWcX52ZleYGRX5aWM5PnO/3iMj3E2Iigx/V+a6l008du246v6K11x0P6HVi3jD7Y4QbGihMHKNepi8BYyTOE4c0wyn2tz/2TV1cD4x1LDosZvtIyMzDyTOBAZYbRel48c/jZAREIOfze8fhkKs0P/hcbW2DUZxi5jWcY+Vi8Tm4bKf1aSPoNhcAIAAB+p48/Kn0sq1Ng/CDno5DlmgIjl58sWuwFRp415P65ny0S6z7P+zOd/eUXUVdnGA8eOeq1n8/0i8v0EBMNIX+D6M0wgn4tJP2GQmAEAAC/08cflT6W1Skwypf1EtomenW9D9QP/eIyPcRAw9GvhaTfUAiMAADgd/r4o9LHsjoFxo2bg38Px3r07mv0gfqhX1ymhxhoOPq1kPQbCoERAAD8Th9/VPpYVqfACA1Hv7hMDzHVc/9OUNVr1ASjDcKnXwtJv6EQGAEAwO/08Uelj2UIjD6nX1ymhxgbnvld+fpXor75hHxn8Hui5DerHK1027op24g2+Y7porOBbYJvoOF3HPPfM5Z6y8F3HE9ed9ir98re5dXjjX4tJP2GQmAEAAC/08cflT6WITD6nH5xmR5idPyB3aI+Kj/Q9gx9sNx9V7MIfdzWdSy99dlX4l3McruKE+5nGIp9BEp+h7UeGLmeWxQaCL/OmireVc0ftXPA6T9w4PCQ9fFCvxaSfkMhMAIAgN/p449KH8sQGH1Ov7hMDzE6/hgbLp/8yv0InQ/EZxZOUALjn8QHe/M6NTA+yeVA94Oz12c945W2wDhsnTsTKbeTH93DQXH2Z5+5+/4m+DE78UK/FpJ+QyEwAgCA3+njj0ofyxAYfU6/uEwPMTb8kvCiwEvS/BJyaVG+CIyLis6Kfxfovpx8NnSGkdssL0lf+Xp+oH8wMHr9tZekOYhOzj/u1fXzauz0ayHpNxQCIwAA+J0+/qj0sQyB0ef0i8v0EAMNR78Wkn5DITACAIDf6eOPSh/LEBh9Tr+4TA8x0HD0ayHpNxQCIwAA+J0+/qj0sQyB0ef0i8v0EAMNR78Wkn5DITACAIDf6eOPSh/LEBh9Tr+4TA8x0HD0ayHpNxQCIwAA+J0+/qj0sQyB0ef0i8v0EAMNR78WkryRuj7c03Nn0kMIjAAA4Fv6+KOyjWs3JLaPLDB+OD+X5n/6meehR3oZfdgDPR/1qO0dutxj9K3Jzbe1D6utJrPfzRSlPJ+kHj2NPpHo1LWb0RYN+sVleoixemgfJY7/JqTt/3uuPGQ5YW7o8rnS988SnvvAaGvM9GshyRvrkScGhEBgBAAAv9LHH5VtXOPQGHZgbNO+o9HWsYYAOPv9D7z6lS1uCFnX9aGHvfq9/3/7dh/aVRXHcfyfMCQ0yCIETSryKZ+dup9P059PmflcYj6jS6fmnKnbdJtuc6bOp3ShRtSKSlogCINI/whJQrGHMRqShkJqsIQmm9sf/vXtnnN37u499+d1ifqb7f3Hi3PuOeeec+dl3I/fcvZcrz84dWRg3aIV6V5/zMTJ3ljfocM0Mzd5+szAfX679h/Q7eqsDYHx4WPH6dY8mzrb/5zjp76uW3Oukbu9MHD/w2K/XMUOMYnEnDD4fPEd3X9yyXV5auQ+SSlzr2Olv0mnZddluC8wxsoapUP8rKQUnpWuhY3NezRKx7RK6RafLd1K70jntH267TC4WFLyv/Putffvn1kpXXKcPQYWy6CsE87YYekx66i8fNCdf5zZ78Iwv1gTZ8wJhEUCIwCgrbK/P353+661OjAuTn8nNKYcKPswNKaUHjqs26Jdu2XgiJjuz1u8ROa8vUD3l2eslt3NYW73gYMyZeYs3Z/+1jxvD7Vetdvf36XbvYfL9NhLfft563K3bffa+UuXycateYHnUOeods/BD3R4zC8u8cZGjp+gn02drfac9MYM3W4r2ann85y1/r2UrOxc2Vq8Q/fVc9vzD4r9chU7xCQywgmAQw42Sue+qpLoBjW3AthS8fNXGGOlv+q2i7qOu30VFPXcsas6KLr9O56Wffz7u2v6519353SFcZUe61kYrkA+bux3YZhfLPO3sbSpMwiMAIA2zf7++NnfNdNvdWA0VABUbcb6LN0OSnXDoM2EPBPolNnzF0jBDjeELVie3rKmYJsOe/Year1qN+Ru0e02514z1i9luAyJjfLu21JYJAOGjfD2N0xlUZ1nxkx/RHOV0H/26AkTvfOU5avX6HPMtfq5zbz/Z3vQ7Jer2CHG1jnTrRAqsSPXdQWwU6DCeEmeWft3sMKYIDDaFUY1ptqOzl6xsqvevcH986Xr5GLpfaj5rJ3n5Ymh30unlA2ScuT/X2FMxP4lvBd7bwAAHgb7++Nnf8vuOzDaBjRXD22b8/J1u27TZm9s2pw3JXNztmzamidzFy6WF/u8Ku9t2eqFT3WPmvOvV62ZV2vNHia0LV25SnKcwOk/a9nKDG8PdY9q1RpDna3GUkaP9dZtzi/w9jTnqWpijjNu1rjnZXjz/p+tz+Chuu01YFBg/f16+tnnQi/YDjF4dOx3Ydi/UARGAEBbZ39//Oxv2X8OjGs3bLwre21rqX+EsnzNWkl/d11orr2zXyAAAECytDow4tGyXxQAAECyEBjbKPtFAQAAJAuBsY2yXxQAAECyEBiToEeffpo97me/KAAAgGQhMCZBj959NXvcz35RAAAAyUJgbKPsFwUAAJAsBMY2yn5RAAAAyUJgBAAAQCQCIwAAACIRGAEAABCJwAgAAIBIBEYAAABEIjACAAAgEoERAAAAkQiMAAAA7dSw0WOlYEeJZOXkSo9efULzRmRgrL54Ueqbmu7KXg8AAIDHg53leg4YJD9XV4fWKZGB0Q6INnt9askZqW+4pefK08P7PSpVCZ4t0fMCAAC0R5euXNVtatp4GT4mTT4qL/fmhsRGhdbfMzCq9ouvK0JzU2bOCo35Q5nqF5yp9a6rjveS83VNUllxSurrfpHux2v0muxXsuTKt1nSPV4uP+x111b+6e5zvkG1cSeE1kpVzTVnjxVeGLyh2xJnrknOl7v3nfijSS5W18jN5jXqvit1ql+qz6qqPidVzvWJikr3GaznBwAAaA++rPgmcF28p9Tr/1NfH1rfqsCoXL7qJlHj7oEx7vXtwBioTjqB0X9fsCoY1yGyvulyYA//OhMYTxfZ57dUGNX1TScgFvjmjv1U2/IM3nkAAADtx9FPPvX6qzLX6yqjuU6UkVoVGFVpMnVcXJatzJBd+w/osUSBMbXklBfGCuLOWJH6T9S1crPhlldhPH2y0pmvDQRGFQrrG4IVP7XHId0PVhjLa5wQ+Ne15ipiMDCWV9+SKzWmwlgqN34/45zdEhhVhVG1x0+eSfiHAQAA0B74c1Da5NcCc3lFxaH1kYGxrqEhNGYsWpEeGrtfx87Vynr/2OISAh0AAMBD9PFnn+v2XtVFJTIwjp4wyasY2n68cCG0/n4dr2j5Hy2VhXu/kuyZ4XUAAAB4MDIys3See6Fnb4lPnSa3bt8OrTEiAyMAAABAYAQAAEAkAiMAAAAiERgBAAAQicAIAACASARGAAAARCIwAgAAINK/BGmvgMYcu5QAAAAASUVORK5CYII=>