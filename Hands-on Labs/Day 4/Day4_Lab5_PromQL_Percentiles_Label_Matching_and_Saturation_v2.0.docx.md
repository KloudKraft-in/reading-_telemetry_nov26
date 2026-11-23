

| NIIT TRAINING DIVISION  \|  LTM \- iRUN Full Stack Engineering |
| ----- |
|  **TRAINING LAB GUIDE****LAB EXERCISE \- 5****PromQL Percentiles, Label Matching and Saturation — histogram\_quantile(), on/ignoring/group\_left, USE Saturation Analysis and Recording Rules SOP**Build p50/p95/p99 Latency Queries  ·  Compare Percentiles, Averages and SLO Ratios  ·  Match Vectors with ignoring, on and group\_left  ·  Enrich Metrics with Ownership  ·  Analyse Saturation During Two Faults  ·  Record Rules for Fast Dashboards |

| Module Series | Observability & Incident Triage — Day 4: New Relic, Grafana, Loki & Prometheus |
| :---- | :---- |
| **Lab Type** | Guided Hands-On SOP — Query Language (PromQL, Advanced) |
| **Duration** | 48 minutes (28 min tasks \+ 8 min validation \+ 7 min debrief \+ 5 min start-up check) |
| **Difficulty** | ⭐⭐⭐⭐ Intermediate — Guided, Build-and-Analyse |
| **Platform** | 100% browser-only: read-only Prometheus web UI (http\://\<ec2-public-ip\>:9090) and shared Grafana Explore, monitoring easyTravel on the instructor's EC2 host ip-172-30-0-220 with node\_exporter and the info metric easytravel\_service\_info. No VM, Docker, curl, jq or promtool. |
| **Document Version** | v2.0  \|  IT Training Division  \|  2026 |
| **Learner Name** | \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ |
| **Date & Batch** | \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ |
| **Prerequisite Lab Completed** | ☐  Day 4 Lab 4 (PromQL Fundamentals) — signed off; Prometheus web UI reachable |
| **Instructor Sign-Off** | \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ |

# 

# 1\. LAB OVERVIEW

## 1.1  Why This Lab Exists

Latency SLOs, capacity alerts and team dashboards all depend on three advanced PromQL skills: computing percentiles from histogram buckets with histogram\_quantile(), combining two sets of series with vector matching (on, ignoring, group\_left), and reading saturation metrics — pools, queues, in-flight requests, CPU — to find the resource that limits the service.  
In this lab you work only in your browser. You build p50/p95/p99 latency queries per route and service and compare them with averages and an SLO ratio, use vector matching to calculate per-status shares and to attach team ownership from an info metric, check host saturation with and without the instructor's CreditCardCheckError500 fault, and read and use four recording rules for fast dashboards and alerts.

| 🎯  NIIT iRUN Alignment |
| :---- |
| INCIDENT OWNERSHIP: You can show latency percentiles per route with the owning team attached. |
|  |
| TROUBLESHOOTING EXCELLENCE: Saturation metrics tell you which resource limits the service in each fault. |
|  |
| OPERATIONAL READINESS: Recording rules make dashboards and alerts fast and consistent. |

## 1.2  Lab Scenario

| 📢  Incident Briefing — Percentiles, Owners and Bottlenecks |
| :---- |
| TIME: 15:00  │  PRIORITY: HIGH  │  ASSIGNED TO: You |
|  |
| REQUEST RECEIVED: "We need latency percentiles per route for the SLO, every chart must show the owning team, and when checkout fails or is slow we want to see at once whether a resource is saturated. Make the queries fast enough for a wall dashboard." |
|  |
| CONTEXT: Prometheus scrapes easyTravel (env="cohort") and node\_exporter on ip-172-30-0-220. easyTravel exposes request-duration histograms; node\_exporter exposes CPU, load and memory and publishes the info metric easytravel\_service\_info{service, team, tier} from a text file. The instructor switches the CreditCardCheckError500 fault ON and OFF (cues C1, C2) and has loaded four recording rules. |
|  |
| YOUR MISSION: Build percentile queries, use vector matching for ratios and ownership, check saturation with and without the fault, and read and use recording rules. You have 28 minutes for the core tasks. |

*Figure: Day 4 Lab 5 — Starting Environment: Browser → Read-Only Prometheus UI and Grafana ← Prometheus Scraping easyTravel and node\_exporter (Textfile easytravel\_service\_info) on ip-172-30-0-220; Four Instructor-Loaded Recording Rules*

## 1.3  Conceptual Foundation

Three tools for advanced questions: percentiles from buckets, matching two vectors, and saturation signals.  
*Figure: histogram\_quantile(φ, sum by (le, …) (rate(x\_bucket\[5m\]))) — Cumulative Buckets le=0.05 … \+Inf → Interpolated Percentile; Vector Matching: left / on(labels) group\_left(extra) right*

| Tool | Syntax | Example | Answers |
| :---- | :---- | :---- | :---- |
| histogram\_quantile() | histogram\_quantile(φ, sum by (le, l) (rate(x\_bucket\[w\]))) | p95 by route | How slow are the slowest φ of requests? |
| ignoring / on | a / ignoring(status) group\_left b | Share of each status per route | Match series with different label sets |
| group\_left(labels) | a \* on(service) group\_left(team) info | Attach team and tier | Enrich metrics with metadata |
| Saturation gauges | active/max · pending · in-flight · CPU | DB pool 10/10, 38 waiting | Which resource limits the service? |

*Figure: Saturation Check — CreditCardCheckError500 Raises Errors on /checkout While Host CPU, Load and Memory Stay Flat (an Application Fault, Not a Capacity Fault)*

## 1.4  Learning Objectives

* Build latency percentile queries with histogram\_quantile() and explain the role of le  
* Compare percentiles with averages and calculate an SLO ratio from buckets  
* Use vector matching with ignoring and group\_left for many-to-one ratios  
* Enrich metrics with an info metric using on() group\_left()  
* Analyse service saturation metrics to find the limiting resource  
* Create and use recording rules

## 1.5  What You Will NOT Do

| 🚫  Hard Stops — Absolute Prohibitions for This Lab |
| :---- |
| ✗  NEVER drop le before histogram\_quantile() — the result becomes empty or wrong |
| ✗  NEVER average percentiles across routes or instances — aggregate buckets, then compute the quantile |
| ✗  NEVER add high-cardinality labels to info metrics |
| ✗  NEVER ask for changes to the shared Prometheus rules during the lab — rules are loaded and checked by the instructor |
| ✗  NEVER switch faults — the instructor announces every cue (C1 ON, C2 OFF) |

# 

# 2\. PREREQUISITES & SETUP

## 2.1  Knowledge Prerequisites

| Prerequisite | Where Covered | Verified? |
| :---- | :---- | :---- |
| rate(), ratios, aggregations | Day 4 Lab 4 | ☐ |
| histogram\_quantile() and buckets | Day 4 Theory — PromQL Histograms | ☐ |
| Label matching: on, ignoring, group\_left | Day 4 Theory — Vector Matching | ☐ |
| USE method and saturation | Observability Day 1 Lab 2 | ☐ |
| Recording rules (read in Status → Rules) | Day 4 Theory — Prometheus Rules | ☐ |

## 2.2  Tools & Access Required

| ⌨  Pre-Lab — Browser Start-Up Check (2 Minutes) |
| :---- |
|  |
| \# 1\. Open the read-only Prometheus web UI: http\://\<ec2-public-ip\>:9090 in Chrome or Firefox (no login) |
| \# 2\. Graph page → run  easytravel\_service\_info  → Table tab → read service, team and tier of each series |
| \# 3\. Status → Rules → find the group easytravel-recording (loaded by the instructor) — look, do not edit |
| \# Browser only — no Docker, curl, jq or promtool: the instructor loads the rules and the info metric. |

## 2.3  Pre-Lab Environment State Verification

Run all checks below and confirm the output matches expectations before starting the timed tasks:

| ⌨  Pre-Lab — Verify starting state |
| :---- |
|  |
| \# 1\. The info metric is scraped |
| \# Expected: two series, value 1 — easytravel-frontend web-platform · easytravel-backend payments |
| \# 2\. The recording-rule group exists |
| \# Expected: group easytravel-recording with four rules (health ok) |
| **PRE-LAB: Record the services and teams from easytravel\_service\_info. This is your BASELINE.**  Answer: easytravel-frontend → team web-platform; easytravel-backend → team payments (read the tier label as well); both series have the value 1\. |

# 

# 3\. CONCEPT DEEP-DIVE BEFORE STARTING

## 3.1  How histogram\_quantile() Works

A Prometheus histogram has cumulative buckets: x\_bucket{le="0.1"} counts requests that took at most 0.1 s, up to le="+Inf" (all requests). rate() turns each bucket into a per-second rate; sum by (le, …) adds buckets of the same bound across series you want to combine; histogram\_quantile(0.95, …) finds the bucket that contains the 95th percentile and interpolates linearly inside it. The answer is an estimate whose precision depends on the bucket bounds — with bounds 0.1 and 0.25, a p95 of "0.243" really means "between 0.1 and 0.25".

| 💡  Why This Matters Operationally |
| :---- |
| Because buckets can be summed, you can compute an exact-in-principle percentile for any combination of routes, services or instances — something averages of percentiles cannot do. |
|  |
| An SLO ratio from a bucket (requests ≤ 0.25 s / all requests) is exact at the bucket bound and is often a better alerting signal than a percentile. |

## 3.2  The Critical Distinction: One-to-One vs Many-to-One Matching

Binary operators match series with identical label sets (one-to-one). When the left side has more series per group than the right — for example one series per status on the left and one total per route on the right — you must say which labels to ignore (or match on) and allow many-to-one with group\_left. group\_left(team) additionally copies the team label from the right side, which is how info metrics enrich other metrics.

| ⚠️  Most Common Mistake With Advanced PromQL |
| :---- |
| An engineer computes avg(histogram\_quantile(0.95, rate(x\_bucket\[5m\]))) across instances and reports it as the service p95 — the number is mathematically meaningless and hides the slow instance. |
|  |
| REASON: Percentiles cannot be averaged; only the underlying buckets can be summed. |
|  |
| YOU MUST aggregate buckets first — histogram\_quantile(0.95, sum by (le) (rate(x\_bucket\[5m\]))) — and compute the quantile last. |

## 3.3  Saturation Signals for easyTravel

| Resource | Utilisation | Saturation | Errors |
| :---- | :---- | :---- | :---- |
| Host CPU | 1 \- avg(rate(node\_cpu\_seconds\_total{mode="idle"}\[5m\])) | node\_load1 / CPU count | — |
| Host memory | 1 \- node\_memory\_MemAvailable\_bytes / node\_memory\_MemTotal\_bytes | rate(node\_vmstat\_pgmajfault\[5m\]) | rate(node\_vmstat\_oom\_kill\[5m\]) |
| Root disk | 1 \- node\_filesystem\_avail\_bytes{mountpoint="/"} / node\_filesystem\_size\_bytes{mountpoint="/"} | rate(node\_disk\_io\_time\_weighted\_seconds\_total\[5m\]) | — |
| Credit-card check (application) | — | p95 latency of /checkout | 5xx ratio of /checkout |

| 📝  How to Decide Which Percentile to Use |
| :---- |
| Ask: "Who is the user, and how many slow requests are acceptable?" p50 shows the typical experience, p95 the slow tail most SLOs use, p99 the worst regular experience (needs enough traffic to be stable). For alerting, prefer an SLO ratio from a bucket bound you control (≤ 0.25 s) or p95 over 5 minutes; avoid p99 on low traffic. |

# 

# 4\. LAB TASKS

*Figure: Day 4 Lab 5 — Four-Task PromQL Percentiles, Label Matching & Saturation SOP Workflow*  
*Figure: Expected Result — p50/p95/p99 per Route and Service; Share per Status with group\_left; Error Rate with Team Labels; Host Saturation Before vs During the Fault; Four Recording Rules Healthy*

| TASK 1 — PERCENTILES: histogram\_quantile() and SLO Ratios |
| :---- |

| 1 | Build Latency Percentile Queries*PromQL Percentiles, Label Matching & Saturation SOP — Day 4 — Lab 5* | ⏱ 7 min |
| :---: | :---- | :---: |

You compute p50, p95 and p99 per route from the bucket rates, see what happens when le is dropped, compare a percentile with the average, and calculate the share of requests faster than 0.25 s — an SLO-style ratio — directly from one bucket.

| ⌨  Task 1 — Percentiles (healthy easyTravel) |
| :---- |
|  |
| \# Step 1: p50 / p95 / p99 per route (Table tab) |
| histogram\_quantile(0.50, sum by (le, route) (rate(http\_server\_request\_duration\_seconds\_bucket{env="cohort",service="easytravel-frontend"}\[5m\]))) |
| histogram\_quantile(0.95, sum by (le, route) (rate(http\_server\_request\_duration\_seconds\_bucket{env="cohort",service="easytravel-frontend"}\[5m\]))) |
| histogram\_quantile(0.99, sum by (le, route) (rate(http\_server\_request\_duration\_seconds\_bucket{env="cohort",service="easytravel-frontend"}\[5m\]))) |
| \# Step 2: the classic mistake — le dropped |
| histogram\_quantile(0.95, sum by (route) (rate(http\_server\_request\_duration\_seconds\_bucket{env="cohort",service="easytravel-frontend"}\[5m\]))) |
| \# Step 3: average (sum/count) vs p95, and an SLO ratio (share ≤ 0.25 s) |
| sum by (route) (rate(http\_server\_request\_duration\_seconds\_sum{env="cohort",service="easytravel-frontend"}\[5m\])) / sum by (route) (rate(http\_server\_request\_duration\_seconds\_count{env="cohort",service="easytravel-frontend"}\[5m\])) |
| sum by (route) (rate(http\_server\_request\_duration\_seconds\_bucket{env="cohort",service="easytravel-frontend",le="0.25"}\[5m\])) / sum by (route) (rate(http\_server\_request\_duration\_seconds\_count{env="cohort",service="easytravel-frontend"}\[5m\])) |
| \# Step 4: p95 per service (all routes of each service combined) |
| histogram\_quantile(0.95, sum by (le, service) (rate(http\_server\_request\_duration\_seconds\_bucket{env="cohort"}\[5m\]))) |
| **📟  Expected Output** |
| Step 1: one value per route; p50 ≤ p95 ≤ p99; the checkout route has the largest values |
| Step 2: empty result (no le label, no quantile) |
| Step 3: average below p95; share ≤ 0.25 s close to 1 (100 %) for fast routes and lower for the slowest route |
| Step 4: one p95 per service (easytravel-frontend, easytravel-backend) |
| **1.A  Why are checkout p95 and p99 (0.243 and 0.249) so close? What does that tell you about bucket resolution?**  Answer: Both percentiles fall into the same histogram bucket, so the interpolation gives close values. The result can only be as precise as the bucket bounds; finer buckets give a better estimate. |
| **1.B  Explain why Step 2 returns nothing and why Step 4 is allowed to sum buckets of different routes.**  Answer: Step 2 returns nothing because histogram\_quantile() needs the le label to know the bucket bounds. Step 4 may sum the buckets of different routes because buckets are cumulative counters with the same bounds, so adding them gives a valid combined histogram. |

# 

| TASK 2 — LABEL MATCHING: ignoring, on, group\_left |
| :---- |

| 2 | Use Vector Matching for Ratios and Ownership*PromQL Percentiles, Label Matching & Saturation SOP — Day 4 — Lab 5* | ⏱ 7 min |
| :---: | :---- | :---: |

Vector matching combines two vectors whose label sets differ. You calculate the share of each status per route (many-to-one with ignoring and group\_left), see the empty result when matching is not specified, and attach the owning team and tier from the info metric with on(service) group\_left.

| ⌨  Task 2 — Matching (run after cue C1 so that 5xx exist) |
| :---- |
|  |
| \# CUE C1 — the instructor announces "CreditCardCheckError500 ON"; write the time down and wait 2 minutes before the queries below |
| \# Step 1: share of each status per route — many-to-one |
| sum by (route, status) (rate(http\_server\_requests\_total{env="cohort",service="easytravel-frontend"}\[2m\])) / ignoring(status) group\_left sum by (route) (rate(http\_server\_requests\_total{env="cohort",service="easytravel-frontend"}\[2m\])) |
| \# Step 2: the same without matching instructions |
| sum by (route, status) (rate(http\_server\_requests\_total{env="cohort",service="easytravel-frontend"}\[2m\])) / sum by (route) (rate(http\_server\_requests\_total{env="cohort",service="easytravel-frontend"}\[2m\])) |
| \# Step 3: 5xx rate per service with the owning team (info metric) |
| sum by (service) (rate(http\_server\_requests\_total{env="cohort",status=\~"5.."}\[2m\])) \* on(service) group\_left(team, tier) easytravel\_service\_info |
| **📟  Expected Output** |
| Step 1: per route the shares sum to 1; /checkout shows a 5xx share clearly above 0, other routes only 200 |
| Step 2: empty result (label sets differ: {route,status} vs {route}) |
| Step 3: the services with 5xx, each with team and tier labels (errors per second) |
| **2.A  Explain ignoring(status) and group\_left in Step 1\. Which side has "many" series per group?**  Answer: ignoring(status) matches series on all labels except status, so every status series of a route finds its route total. group\_left allows many (left) to one (right) matching and keeps the extra labels of the left side. |
| **2.B  Why does the info metric have value 1, and why must it never contain IDs such as pod or request IDs?**  Answer: The info metric carries metadata as labels, so its value is always 1 and can be multiplied without changing the other value. It must never contain IDs such as pod or request IDs, because every new value creates new series (cardinality explosion).  |

| ⚠️  STOP CHECK — Keep the Fault ON for the Saturation Analysis |
| :---- |
| Before moving to Task 3, confirm Step 1 shows a 5xx share for /checkout. Do not ask for the fault to be switched OFF — Task 3 compares the fault window with a healthy baseline. The instructor announces cue C2 at the end of Task 3\. |
|  |
| If in doubt — show your instructor Step 1 and Step 3 before proceeding to Task 3\. |

# 

| TASK 3 — SATURATION: Which Resource Limits the Service? |
| :---- |

| 3 | Analyse Service Saturation Metrics During Two Faults*PromQL Percentiles, Label Matching & Saturation SOP — Day 4 — Lab 5* | ⏱ 8 min |
| :---: | :---- | :---: |

Saturation metrics show how full a resource is and how much work is waiting. You read host CPU, load and memory in the healthy baseline and while the fault is ON — the checkout symptom is errors, and the saturation data tells you whether a resource is the cause.

| ⌨  Task 3 — Saturation with and without the fault |
| :---- |
|  |
| \# Step 1: fault window (fault still ON) — host saturation now |
| 1 \- avg(rate(node\_cpu\_seconds\_total{mode="idle"}\[2m\])) |
| node\_load1 / count(count by (cpu) (node\_cpu\_seconds\_total{mode="idle"})) |
| 1 \- node\_memory\_MemAvailable\_bytes / node\_memory\_MemTotal\_bytes |
| sum(rate(http\_server\_requests\_total{env="cohort",service="easytravel-frontend",route="/checkout",status=\~"5.."}\[2m\])) / sum(rate(http\_server\_requests\_total{env="cohort",service="easytravel-frontend",route="/checkout"}\[2m\])) |
| histogram\_quantile(0.95, sum by (le) (rate(http\_server\_request\_duration\_seconds\_bucket{env="cohort",service="easytravel-frontend",route="/checkout"}\[2m\]))) |
| \# Step 2: healthy baseline — the same five queries with  offset 20m  (copy each query and append offset 20m to the selector or the whole expression where needed) |
| 1 \- avg(rate(node\_cpu\_seconds\_total{mode="idle"}\[2m\] offset 20m)) |
| sum(rate(http\_server\_requests\_total{env="cohort",service="easytravel-frontend",route="/checkout",status=\~"5.."}\[2m\] offset 20m)) / sum(rate(http\_server\_requests\_total{env="cohort",service="easytravel-frontend",route="/checkout"}\[2m\] offset 20m)) |
| \# Step 3 (worksheet, no query): for a database connection-pool exhaustion and for a slow external payment provider, write the saturation metric you would expect to rise first |
| \# CUE C2 — at the end of this task the instructor announces "CreditCardCheckError500 OFF"; write the time down |
| **📟  Expected Output** |
| Step 1: host CPU, load per CPU and memory utilisation about the same as in the baseline; checkout 5xx ratio clearly above 0 |
| Step 2: baseline 5xx ratio ≈ 0; CPU and load the same level as in Step 1 → no resource is saturated |
| Step 3: pool exhaustion → pool utilisation 100 % and pending threads; slow provider → in-flight outgoing calls and p95 latency rise first |
| **3.A  Fill a table: period (baseline, fault window) × (host CPU, load per CPU, memory, checkout 5xx ratio, checkout p95). Is any resource limiting?**   Answer:  Baseline vs fault: CPU, load per CPU and memory are about equal in both periods, while the checkout 5xx ratio rises from about 0 to a clear value. No resource is limiting — the fault is in the application or its credit-card check, not in capacity. |
| **3.B  Why did the other routes stay healthy during the fault, and what does that tell you about the blast radius?**  Answer: Only the credit-card check of the checkout route fails, so the other routes keep returning 200 and show no extra errors or latency. The fault is isolated to one dependency path rather than shared capacity.   |

# 

| TASK 4 — RECORDING RULES: Fast, Consistent Queries |
| :---- |

| 4 | Read and Use Recording Rules for the Key Queries*PromQL Percentiles, Label Matching & Saturation SOP — Day 4 — Lab 5* | ⏱ 6 min |
| :---: | :---- | :---: |

Recording rules evaluate expensive queries on a schedule and store the result as new series. Dashboards and alerts then read the cheap recorded series. You read the four rules the instructor loaded (naming convention level:metric:operation), check their health in Status → Rules, and query the recorded series.

| ⌨  Task 4 — Read the rules, check them, use them |
| :---- |
|  |
| \# Step 1: read the rules the instructor loaded (shown here for reference) — Prometheus UI → Status → Rules → group easytravel-recording |
| \#   record: route:http\_requests:rate5m           expr: sum by (service, route) (rate(http\_server\_requests\_total{env="cohort"}\[5m\])) |
| \#   record: route:http\_errors:ratio\_rate5m       expr: sum by (service, route) (rate(…{status=\~"5.."}\[5m\])) / sum by (service, route) (rate(…\[5m\])) |
| \#   record: route:http\_latency\_seconds:p95\_5m    expr: histogram\_quantile(0.95, sum by (le, service, route) (rate(http\_server\_request\_duration\_seconds\_bucket{env="cohort"}\[5m\]))) |
| \#   record: service:host\_cpu:utilization         expr: 1 \- avg(rate(node\_cpu\_seconds\_total{mode="idle"}\[5m\])) |
| \# Step 2: Graph page → query the recorded series |
| route:http\_latency\_seconds:p95\_5m{service="easytravel-frontend"} |
| route:http\_requests:rate5m \* on(service) group\_left(team) easytravel\_service\_info |
| \# Step 3 (worksheet): write a fifth rule, service:host\_memory:utilization, and name its level, metric and operation |
| **📟  Expected Output** |
| Step 1: Status → Rules shows the four rules with health ok and a last evaluation time |
| Step 2: p95 per frontend route from the recorded series; request rates per service and route with team labels (web-platform, payments) |
| **4.A  Explain the name route:http\_latency\_seconds:p95\_5m (level, metric, operation). Why use recording rules for wall dashboards?**   Answer: route is the aggregation level, http\_latency\_seconds the metric (with its unit), p95\_5m the operation (95th percentile over 5 minutes). Wall dashboards read the cheap recorded series instead of evaluating an expensive histogram query for every viewer and refresh. |
| **4.B  Which of your Lab 5 queries would you also turn into an alert rule, with which threshold?**   Answer: I would create an alert for the checkout p95 latency when it exceeds 0.25 seconds for 5 minutes. I would also alert when the HTTP error ratio exceeds 5%.  |

# 

# 5\. VALIDATION — CONFIRM FULL READINESS

Do not close the incident or call for instructor sign-off until ALL 8 validation steps below are completed and recorded.  
*Figure: Day 4 — Lab 5 — PromQL Percentiles, Label Matching & Saturation SOP Validation Checklist*

## 5.1  Validation Task Set

Validation Check 1 — Percentiles

| ⌨  Validation 1 |
| :---- |
|  |
| Review Task 1 Step 1 (Table tab output) |
| \# PASS criterion: one value per route; checkout the highest when healthy |
| **V1: Do your percentile queries return one value per route?**  Answer: Yes. The p95 query returns one value per frontend route, and the checkout route is the highest.  |

Validation Check 2 — le explained

| ⌨  Validation 2 |
| :---- |
|  |
| Review answer 1.B |
| \# PASS criterion: le must be kept; buckets summed before the quantile |
| **V2: Can you explain the role of le?**  Answer: le represents the histogram bucket's upper boundary. It must be retained when summing buckets before applying histogram\_quantile(). |

Validation Check 3 — SLO ratio

| ⌨  Validation 3 |
| :---- |
|  |
| Review Task 1 Step 3 |
| \# PASS criterion: share ≤ 0.25 s per route (close to 100 % on fast routes) |
| **V3: Did you calculate an SLO ratio from a bucket?**  Answer: Yes. The ratio was calculated from the le="0.25" bucket divided by the request count; fast routes returned close to 100 %.  |

Validation Check 4 — Many-to-one matching

| ⌨  Validation 4 |
| :---- |
|  |
| Review Task 2 Steps 1–2 |
| \# PASS criterion: shares per status sum to 1 per route; plain division empty |
| **V4: Did ignoring/group\_left produce the per-status shares?**  Answer: Yes. The query calculated the proportion of each HTTP status per route. The shares sum to approximately 1 per route, while plain division returned no data. |

Validation Check 5 — Info metric join

| ⌨  Validation 5 |
| :---- |
|  |
| Review Task 2 Step 3 |
| \# PASS criterion: both services (easytravel-frontend, easytravel-backend) carry team and tier labels |
| **V5: Did the join attach team labels?**  Answer: Yes. The join attached the team labels: easytravel-frontend – web-platform, easytravel-backend – payments.  |

Validation Check 6 — Saturation analysis

| ⌨  Validation 6 |
| :---- |
|  |
| Review answer 3.A |
| \# PASS criterion: baseline and fault window compared; conclusion "no saturated resource — application fault" |
| **V6: Did you decide from the saturation data whether a resource was limiting?**  Answer: Yes. CPU, load and memory were about equal in the baseline and the fault window while the checkout 5xx ratio rose, so no resource was saturated and the fault is in the application.  |

Validation Check 7 — Recording rules

| ⌨  Validation 7 |
| :---- |
|  |
| Status → Rules → group easytravel-recording; cue C2 time |
| \# PASS criterion: four rules with health ok; C2 time recorded |
| **V7: Are the four recording rules healthy and was the fault announced OFF?**  Answer: Yes. The four recording rules show health ok in Status → Rules, and the instructor announced the fault OFF (cue C2). |

Validation Check 8 — Full lab record complete

| ⌨  Validation 8 — Final completeness check |
| :---- |
|  |
| \# Confirm every answer box (Pre-Lab, 1.A through 4.B) is completed |
| \# Nothing to stop or clean up — everything ran on the instructor's shared stack |
| **V8: Confirm all answer boxes are complete and your evidence is ready to show your instructor.**  Answer: Yes. All Pre-Lab and Task 1–4 answers are completed, and command outputs are available as evidence.  |

**✅  STOP HERE — Show your completed validation record to your instructor before proceeding to Section 7\.**

# 

# 6\. TROUBLESHOOTING — COMMON ISSUES & FIXES

| Issue / Error | Cause | Diagnosis | Fix |
| :---- | :---- | :---- | :---- |
| histogram\_quantile returns \[\] | le missing in the by clause | Run the inner sum alone and check for le | sum by (le, …) |
| Percentile equals a bucket bound (e.g. 5\) | Most requests fall in the highest finite bucket | Inspect bucket rates | Expected with coarse buckets; add buckets in the application |
| easytravel\_service\_info missing | Textfile not mounted or node\_exporter not restarted by the instructor | Graph: count(easytravel\_service\_info) | Tell the instructor (Appendix A step 2\) |
| "many-to-many matching not allowed" | Info metric duplicated (several instances) or group\_left on the wrong side | count by (service) (easytravel\_service\_info) | Use max by (service, team, tier) (easytravel\_service\_info) on the right side |
| Rules page shows health "err" | Rule expression error or a missing source metric | Status → Rules → error text | Tell the instructor; test the source query in the Graph page first |
| Recorded series empty | Rules not yet evaluated, or no source data | Status → Rules → last evaluation | Wait one evaluation interval (about a minute) |

# 

# 7\. INSTRUCTOR DEBRIEF — 7 MINUTES

## 7.1  Discussion Questions

| Discussion 1 — Percentiles from Buckets |
| :---- |
| Without notes: write the p95 per service query and explain each part. |
| Why can you not average p95s from several instances? |
|  |
| Key answer to explore: sum by (le, service) of bucket rates, then histogram\_quantile; averages of quantiles are not quantiles. |
| **Discussion 2 — Matching** |
| When do you need group\_left, and when is "on" enough? |
| How did the info metric replace a lookup table? |
|  |
| Key insight: many-to-one needs group\_left; info metrics carry metadata as labels with value 1 — PromQL's lookup. |
| **Discussion 3 — Same Symptom, Different Saturation** |
| The fault raised errors but not CPU. Which panels would you put next to the error panel so that on-call sees whether a resource is saturated? |
| What is the leading indicator for a capacity problem, and what does an application fault look like? |
|  |
| Key answer: for capacity problems saturation (CPU, load, memory, pool) rises before errors; for an application or dependency fault saturation stays flat while errors rise. |
| **Discussion 4 — Recording Rules** |
| Which queries from this week would you record, and which would you leave ad hoc? |
| What naming and review rules would your team need? |
|  |
| Answer: record what dashboards and alerts use repeatedly; follow level:metric:operation and review rules like code. |

## 7.2  Common Mistakes — Learn From These

| Mistake | Why It Happens | Consequence | Prevention |
| :---- | :---- | :---- | :---- |
| Dropping le | Copying sum by (route) | Empty or wrong percentiles | sum by (le, route) |
| Averaging percentiles | Seems natural | Meaningless numbers | Sum buckets, then quantile |
| Plain division of different label sets | Forgetting matching | Empty results | ignoring/on \+ group\_left |
| Info metrics with IDs | More detail | Cardinality explosion | Only bounded metadata |
| Recording everything | Speed everywhere | More series, harder maintenance | Record what is used repeatedly |

# 8\. EXTENSION TASKS (Advanced Learners)

| Extension A — Apdex from Buckets |
| :---- |
| Apdex(T=0.25) \= (satisfied \+ tolerating/2) / total with satisfied le="0.25", tolerating le="1" minus le="0.25". |
| Write the PromQL per route and compare with the NRQL apdex() from Lab 1\. |
| Key question: why does it need two buckets? |
| **Extension B — Alert on the SLO Ratio** |
| Write an alert rule: share of /checkout requests ≤ 0.25 s below 0.9 for 5 minutes (paper only). |
| Mark on your Task 3 chart where it would have fired during cues C1–C2. |
| Compare with the p95 alert from Day 1 Lab 5\. |
| **Extension C — Saturation Panel Row** |
| Add a row "Saturation" to u\<seat\>\_easyTravel\_Dev using service:host\_cpu:utilization and node\_load1. |
| Add thresholds at 0.7 and 0.9 for the CPU. |
| Explain why saturation panels belong next to latency. |

# 

# 9\. LAB COMPLETION & SIGN-OFF

## 9.1  Submission Checklist

| ✓ | Completion Criterion | Status |
| :---- | :---- | :---- |
| ☐ | p50/p95/p99 queries built; le explained; average and SLO ratio compared | ☐ Pass / ☐ Fail |
| ☐ | Many-to-one matching with ignoring/group\_left; info metric join with on/group\_left | ☐ Pass / ☐ Fail |
| ☐ | Host saturation compared between baseline and fault window; conclusion stated | ☐ Pass / ☐ Fail |
| ☐ | Four recording rules read, checked in Status → Rules and queried | ☐ Pass / ☐ Fail |
| ☐ | Fault OFF cue (C2) observed | ☐ Pass / ☐ Fail |
| ☐ | All 8 validation checks completed and all answer boxes filled in | ☐ Pass / ☐ Fail |

## 9.2  Grading Criteria

| Assessment Area | Criteria | Marks | Weight |
| :---- | :---- | :---- | :---- |
| Task 1 — Percentiles | Correct percentile queries and explanations | 25 | 25% |
| Task 2 — Label Matching | Per-status shares and ownership join | 25 | 25% |
| Task 3 — Saturation Analysis | Baseline vs fault comparison; conclusion backed by data | 20 | 20% |
| Task 4 — Recording Rules | Rules read, health checked, recorded series used; naming explained | 20 | 20% |
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

# 10\. QUICK REFERENCE — PROMQL PERCENTILES, MATCHING & SATURATION COMMAND CARD

Bookmark this page. Every command you need in SOP order.

| Category | Command | Purpose |
| :---- | :---- | :---- |
| Percentile | histogram\_quantile(0.95, sum by (le, route) (rate(x\_bucket\[5m\]))) | p95 |
| Average | rate(x\_sum\[5m\]) / rate(x\_count\[5m\]) | Mean |
| SLO ratio | rate(x\_bucket{le="0.25"}\[5m\]) / rate(x\_count\[5m\]) | Share fast |
| Ignore labels | a / ignoring(status) group\_left b | Many-to-one |
| Match on | a \* on(service) group\_left(team) info | Enrich |
| Info metric | easytravel\_service\_info{service, team, tier} 1 | Metadata |
| Host CPU utilisation | 1 \- avg(rate(node\_cpu\_seconds\_total{mode="idle"}\[5m\])) | USE: U |
| Load per CPU | node\_load1 / count(count by (cpu) (node\_cpu\_seconds\_total)) | USE: S |
| Memory utilisation | 1 \- node\_memory\_MemAvailable\_bytes / node\_memory\_MemTotal\_bytes | USE: U |
| Rule check | Prometheus UI → Status → Rules | Health ok |
| Reload | Instructor only (learners never reload) | Apply rules |
| Naming | level:metric:operations | route:http\_requests:rate5m |

# APPENDIX A — INSTRUCTOR PRE-CLASS RUNBOOK (INSTRUCTOR ONLY)

INSTRUCTOR ONLY — learners never run these commands. Do this once, at least 30 minutes before the cohort. Commands run on the EC2 host ip-172-30-0-220.  
1\. Prometheus web UI on port 9090 read-only (no \--web.enable-admin-api, no \--web.enable-lifecycle for learners) and reachable from the training network. The metric contract of Lab 4 applies: http\_server\_requests\_total and the duration histogram with env="cohort", service and route labels, default bucket bounds (including 0.25), and node\_exporter metrics.  
2\. Info metric: write the text file for the node\_exporter textfile collector, then check easytravel\_service\_info in the Graph page (two series, value 1).

| ⌨  Instructor — info metric, rules and cues |
| :---- |
|  |
| \# 1\. info metric (textfile collector directory as configured for node\_exporter) |
| printf 'easytravel\_service\_info{service="easytravel-frontend",team="web-platform",tier="1"} 1\\neasytravel\_service\_info{service="easytravel-backend",team="payments",tier="1"} 1\\n' \> /var/lib/node\_exporter/textfile/easytravel\_service\_info.prom |
| \# 2\. recording rules: copy the file from the setup note (prometheus/rules/easytravel-recording.yml), check and reload |
| promtool check rules prometheus/rules/easytravel-recording.yml |
| kill \-HUP "\$(pgrep \-x prometheus)" |
| \# C1  start of Task 2 (about T+8): announce "CreditCardCheckError500 ON" and the time |
| ./faultctl.sh on |
| \# C2  end of Task 3 (about T+23): announce "OFF" and the time |
| ./faultctl.sh off |

3\. Reload with SIGHUP (kill \-HUP), not the HTTP reload endpoint, so that \--web.enable-lifecycle stays off and learners cannot reload or change the configuration. At the end confirm the fault is OFF.

| *Official Lab Guide — Day 4 — Lab 5: PromQL Percentiles, Label Matching & Saturation SOP  \|  IT Training Division  \|  NIIT iRUN Framework  \|  Version 2.0  \|  Classification: Internal Training* |
| :---: |

*IT Training Division  \|  NIIT iRUN Framework  \|  Confidential — For Training Use Only  \|  Do Not Distribute*