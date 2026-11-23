

| NIIT TRAINING DIVISION  \|  LTM \- iRUN Full Stack Engineering |
| ----- |
|  **TRAINING LAB GUIDE****LAB EXERCISE \- 4****PromQL Fundamentals — Instant and Range Vectors, Label Selectors, rate() and increase(), Counter Resets, Error Rate and Aggregation Operators SOP**Read Instant and Range Vectors  ·  Select Series with \= \!= \=\~ \!\~  ·  Turn Counters into Rates  ·  See What a Counter Reset Does  ·  Calculate the Error Rate  ·  Aggregate with sum, avg, max, count, topk, by and without |

| Module Series | Observability & Incident Triage — Day 4: New Relic, Grafana, Loki & Prometheus |
| :---- | :---- |
| **Lab Type** | Guided Hands-On SOP — Query Language (PromQL) |
| **Duration** | 48 minutes (28 min tasks \+ 8 min validation \+ 7 min debrief \+ 5 min start-up check) |
| **Difficulty** | ⭐⭐⭐ Beginner-Intermediate — Guided, Build-a-Query |
| **Platform** | 100% browser-only: read-only Prometheus web UI (http\://\<ec2-public-ip\>:9090) and shared Grafana Explore, monitoring the instructor's EC2 host ip-172-30-0-220 that runs easyTravel. No VM, Docker, curl or jq. |
| **Document Version** | v2.0  \|  IT Training Division  \|  2026 |
| **Learner Name** | \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ |
| **Date & Batch** | \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ |
| **Prerequisite Lab Completed** | ☐  Day 4 Lab 3 (Loki LogQL) — signed off; Prometheus web UI reachable (http\://\<ec2-public-ip\>:9090) and scraping easyTravel (env="cohort") |
| **Instructor Sign-Off** | \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ |

# 

# 1\. LAB OVERVIEW

## 1.1  Why This Lab Exists

PromQL is the query language of Prometheus and of every tool that speaks it (Grafana, Thanos, Mimir, Google and Amazon managed Prometheus). Its core ideas are few but strict: a selector returns an instant vector (one value per series) or a range vector (several samples per series); counters only grow and must be turned into rates; aggregation operators combine series by labels. Most wrong PromQL answers come from mixing these up.  
In this lab you read instant and range vectors, use every label-matching operator, compare rate() and increase() and watch what a counter reset does to raw values, rate(), increase() and delta(), calculate the error rate of easyTravel during a fault, and aggregate with sum, avg, max, count and topk using by and without.

| 🎯  NIIT iRUN Alignment |
| :---- |
| INCIDENT OWNERSHIP: You can write the PromQL that answers "how many, how fast, how often failing" without guessing. |
|  |
| TROUBLESHOOTING EXCELLENCE: You will recognise and avoid the classic counter and vector-type mistakes. |
|  |
| OPERATIONAL READINESS: Your error-rate query is the basis of the alert and recording rules in Lab 5\. |

## 1.2  Lab Scenario

| 📢  Incident Briefing — PromQL Without Guessing |
| :---- |
| TIME: 13:30  │  PRIORITY: MEDIUM  │  ASSIGNED TO: You |
|  |
| REQUEST RECEIVED: "We copy PromQL from the internet and are never sure it is right. Show the team what instant and range vectors are, why we need rate(), what happens when a service restarts, how to calculate the easyTravel error rate, and how to aggregate by the labels we care about." |
|  |
| CONTEXT: Prometheus scrapes easyTravel's metrics every 5 seconds (env="cohort", services easytravel-frontend and easytravel-backend). You query in the read-only Prometheus web UI; the instructor restarts the metrics exporter (cue R1) to reset counters and switches the CreditCardCheckError500 fault ON and OFF (cues C1, C2) to create errors. |
|  |
| YOUR MISSION: Run and explain each query type, then build the error rate and aggregations. You have 28 minutes for the core tasks. |

*Figure: Day 4 Lab 4 — Starting Environment: Browser → Read-Only Prometheus UI and Grafana Explore ← Prometheus Scraping easyTravel on ip-172-30-0-220 Every 5 s*

## 1.3  Conceptual Foundation

Every PromQL expression evaluates to one of four types. Functions and operators accept only certain types.  
*Figure: PromQL Types — Instant Vector (one sample per series at time t) · Range Vector (samples per series in \[window\]) · Scalar · String; rate()/increase() Take a Range Vector and Return an Instant Vector; Aggregations Need Instant Vectors*

| Concept | Example | Returns | Typical Use |
| :---- | :---- | :---- | :---- |
| Instant vector selector | http\_server\_requests\_total{service="frontend"} | Latest value of each matching series | Gauges, current state |
| Range vector selector | …{…}\[1m\] | All samples in the last minute per series | Input for rate(), increase(), \*\_over\_time() |
| rate() / increase() | rate(x\[5m\]) · increase(x\[5m\]) | Per-second rate / total increase, reset-safe | Counters |
| Aggregation | sum by (route) (…) · topk(2, …) | Fewer series, grouped by labels | Totals, rankings |

*Figure: Counter Reset — Raw Counter Drops to 0 on Restart; rate() and increase() Detect the Drop and Continue Correctly; delta() Does Not (Negative Result)*

## 1.4  Learning Objectives

* Explain instant vs range vectors and when each is required  
* Use label matchers \=, \!=, \=\~ and \!\~  
* Use rate() and increase() on counters and explain the difference  
* Explain counter resets and their effect on raw values, rate(), increase() and delta()  
* Calculate an error rate (ratio) correctly  
* Aggregate with sum, avg, max, count and topk using by and without

## 1.5  What You Will NOT Do

| 🚫  Hard Stops — Absolute Prohibitions for This Lab |
| :---- |
| ✗  NEVER graph raw counter values as "requests" — use rate() or increase() |
| ✗  NEVER use delta() on counters — it ignores resets |
| ✗  NEVER sum before rate (rate(sum(…))) — it breaks reset handling |
| ✗  NEVER use a rate window shorter than about 4 × the scrape interval |
| ✗  NEVER switch faults or restart exporters — the instructor announces every cue (R1, C1, C2) |

# 

# 2\. PREREQUISITES & SETUP

## 2.1  Knowledge Prerequisites

| Prerequisite | Where Covered | Verified? |
| :---- | :---- | :---- |
| Prometheus metric types and RED queries | Observability Day 1 Lab 2 | ☐ |
| Instant vs range vectors, rate(), increase() | Day 4 Theory — PromQL Fundamentals | ☐ |
| Label matching and aggregations | Day 4 Theory — PromQL Operators | ☐ |
| Grafana Explore | Day 4 Lab 2 | ☐ |
| Instructor cues R1 (counter reset), C1 / C2 (fault ON / OFF) | Lab admin / instructor | ☐ |

## 2.2  Tools & Access Required

| ⌨  Pre-Lab — Browser Start-Up Check (2 Minutes) |
| :---- |
|  |
| \# 1\. Open the read-only Prometheus web UI: http\://\<ec2-public-ip\>:9090 in Chrome or Firefox (no login) |
| \# 2\. Status → Targets → confirm the easyTravel and node targets are UP (look, do not edit) |
| \# 3\. Status → Configuration → find scrape\_interval for the easyTravel job (or in Targets, the column "Last scrape") |
| \# Queries below run on the Graph page (Query box → Execute → Table tab for instant values, Graph tab for a range). Browser only — no curl, jq or Docker. |

## 2.3  Pre-Lab Environment State Verification

Run all checks below and confirm the output matches expectations before starting the timed tasks:

| ⌨  Pre-Lab — Verify starting state |
| :---- |
|  |
| \# 1\. Scrape interval and targets |
| \# Expected: easyTravel up · node up · prometheus up; scrape interval 5s |
| \# 2\. Write down the fault phase the instructor announces (expected: OFF) |
| **PRE-LAB: Record the scrape interval you read in Status → Configuration. What is the shortest sensible rate() window for it?**  Answer: The scrape interval is 5 seconds (as read in Status → Configuration). The shortest sensible rate() window is about 20 seconds (4 × the interval), in practice \[1m\]. |

# 

# 3\. CONCEPT DEEP-DIVE BEFORE STARTING

## 3.1  Counters Need rate()

A counter only increases while a process runs and starts again at 0 when it restarts. Its raw value ("2,535 requests since start") says little; what you want is how fast it grows. rate(x\[5m\]) calculates the per-second increase over the last five minutes, increase(x\[5m\]) the total increase over that window (rate × 300). Both detect resets (a value lower than the previous one) and compensate, and both extrapolate slightly to the window edges, so increase() can return non-integers.

| 💡  Why This Matters Operationally |
| :---- |
| Restarts happen during incidents. Queries that use rate()/increase() keep working; queries that subtract raw values or use delta() produce negative or nonsense numbers exactly when you need them. |
|  |
| Label matchers and aggregations decide which series end up in your answer — a missing route filter or a wrong "by" clause is the most common silent error. |

## 3.2  The Critical Distinction: rate() vs increase() vs irate()

rate() is the average per-second rate over the window — smooth and right for dashboards and alerts. increase() is the same value multiplied by the window length — right for "how many in the last 5 minutes". irate() uses only the last two samples — very spiky, useful only for fast-moving high-resolution graphs. Apply them to counters only; for gauges use avg\_over\_time(), max\_over\_time() or deriv().

| ⚠️  Most Common Mistake With PromQL |
| :---- |
| An engineer writes sum(http\_server\_requests\_total) and plots it as "traffic". After a restart the graph drops to zero, and during the incident review the numbers make no sense. |
|  |
| REASON: Raw counters show the total since the process started; the sum of raw counters mixes start times and resets. |
|  |
| YOU MUST apply rate() or increase() to each counter series first and aggregate afterwards: sum by (route) (rate(x\[5m\])). |

## 3.3  Label Matchers and Aggregation Modifiers

| Syntax | Meaning | Example | Result |
| :---- | :---- | :---- | :---- |
| \= / \!= | Equal / not equal | status\!="200" | All non-200 series |
| \=\~ / \!\~ | Regex match / no match (fully anchored) | route=\~"/(checkout\|search)" | Two routes |
| sum by (l) / sum without (l) | Keep only l / drop only l | sum without (method, status) (…) | Per route and service |
| topk(k, …) / count / avg / max | Ranking and statistics across series | topk(2, sum by (route) (…)) | Two busiest routes |

| 📝  How to Decide the Rate Window |
| :---- |
| Ask: "How often is the data scraped, and how fast must the graph react?" The window must contain at least two samples, and in practice about four scrape intervals or more: with 5 s scraping, \[1m\] reacts quickly and \[5m\] is smoother. Alerts usually use \[5m\]; Grafana panels use \$\_\_rate\_interval, which adapts to the scrape interval and the zoom level. |

# 

# 4\. LAB TASKS

*Figure: Day 4 Lab 4 — Four-Task PromQL Fundamentals SOP Workflow*  
*Figure: Expected Result — Instant vs Range Vector Output Compared; Matchers Selecting the Right Series; rate/increase Correct Across a Counter Reset While delta Goes Negative; Checkout Error Rate Clearly Above the Others During the Fault Window; Aggregations by Route and Service*

| TASK 1 — VECTORS & SELECTORS: Instant vs Range, Label Matchers |
| :---- |

| 1 | Read Instant and Range Vectors and Use Label Matchers*PromQL Fundamentals SOP — Day 4 — Lab 4* | ⏱ 7 min |
| :---: | :---- | :---: |

The same selector returns an instant vector or, with \[window\], a range vector. You compare their outputs, provoke the type error that appears when a range vector is used where an instant vector is needed, and practise the four label matchers.

| ⌨  Task 1 — Vectors and matchers |
| :---- |
|  |
| \# Step 1: Instant vector — one value per series (Graph page → Table tab) |
| http\_server\_requests\_total{env="cohort",service="easytravel-frontend"} |
| \# Step 2: Range vector — samples per series in the last minute (5 s scrape → about 12\) |
| http\_server\_requests\_total{env="cohort",service="easytravel-frontend",route="/checkout"}\[1m\] |
| \# Step 3: The type error |
| sum(http\_server\_requests\_total{env="cohort",service="easytravel-frontend"}\[1m\]) |
| \# Step 4: Matchers |
| count(http\_server\_requests\_total{env="cohort",service="easytravel-frontend",route=\~"/(checkout\|search)"}) |
| count(http\_server\_requests\_total{env="cohort",service="easytravel-frontend",status\!\~"2.."}) |
| count(http\_server\_requests\_total{env="cohort",service\!="easytravel-frontend"}) |
| **📟  Expected Output** |
| Step 1: one row per route/status series with the counter value (a large, only-growing number) |
| Step 2: one row per status series of /checkout, each with about 12 samples @timestamp |
| Step 3: Error executing query: expected type instant vector in aggregation expression, got range vector |
| Step 4: the number of /checkout and /search series · the number of non-2xx series (0 while healthy) · the number of backend series |
| **1.A  In your own words: what is the difference between Step 1 and Step 2, and which functions need Step 2's type?**  Answer: Step 1 returns an instant vector: the latest value of each matching series. Step 2 returns a range vector: all samples of each series in the last minute. rate(), increase(), resets() and \*\_over\_time() need the range-vector type. |
| **1.B  Why are PromQL regex matchers "fully anchored", and how would you match any route that contains "cart"?**  Answer:  Regex matchers are fully anchored: the pattern must match the entire label value, as if it started with ^ and ended with \$. To match any route containing "cart" you write route=\~".\*cart.\*". |

# 

| TASK 2 — RATES: rate(), increase() and Counter Resets |
| :---- |

| 2 | Use rate() and increase() and Observe a Counter Reset*PromQL Fundamentals SOP — Day 4 — Lab 4* | ⏱ 8 min |
| :---: | :---- | :---: |

rate() and increase() turn counters into useful numbers and survive restarts. You compare them, use the instructor's exporter restart (cue R1) to reset all counters, and compare raw values, increase(), delta() and resets() for the same series.

| ⌨  Task 2 — Rates and resets |
| :---- |
|  |
| \# Step 1: per-second rate (1m and 5m windows) and total increase per route |
| sum by (route) (rate(http\_server\_requests\_total{env="cohort",service="easytravel-frontend"}\[1m\])) |
| sum by (route) (increase(http\_server\_requests\_total{env="cohort",service="easytravel-frontend"}\[5m\])) |
| \# Step 2: CUE R1 — the instructor restarts the metrics exporter, so all counters start again at 0; write the time down and wait 45 s |
| \# Step 3: one series, four views (Table tab) |
| http\_server\_requests\_total{env="cohort",service="easytravel-frontend",route="/checkout",status="200"} |
| resets(http\_server\_requests\_total{env="cohort",service="easytravel-frontend",route="/checkout",status="200"}\[10m\]) |
| increase(http\_server\_requests\_total{env="cohort",service="easytravel-frontend",route="/checkout",status="200"}\[10m\]) |
| delta(http\_server\_requests\_total{env="cohort",service="easytravel-frontend",route="/checkout",status="200"}\[10m\]) |
| **📟  Expected Output** |
| Step 1: req/s per route (note the busiest route) · increase over 5 min ≈ rate × 300 |
| Step 3: raw value small again after cue R1 · resets \= 1 |
|         increase \= all requests of the last 10 min (reset handled) · delta can be NEGATIVE |
| **2.A  Record the four Step 3 values. Explain why increase() is right and delta() is wrong for counters.**  Answer: Record the raw counter, resets, increase and delta. increase() detects the reset and adds the counter value after it, so it stays positive; delta() just subtracts last minus first sample and goes negative after a reset, so it must not be used on counters. |
| **2.B  Why is increase(…\[5m\]) ≈ rate(…\[5m\]) × 300, and why can increase() return a non-integer?**  Answer:  5 minutes are 300 seconds, so increase ≈ per-second rate × 300\. increase() extrapolates to the window edges, so it can return a non-integer value even though counters count whole requests. |

# 

| TASK 3 — ERROR RATE: Ratio of Rates During a Fault |
| :---- |

| 3 | Calculate the Error Rate Using PromQL*PromQL Fundamentals SOP — Day 4 — Lab 4* | ⏱ 7 min |
| :---: | :---- | :---: |

An error rate is a ratio of two rates: failed requests per second divided by all requests per second, aggregated the same way on both sides. You build it overall and per route, make it return 0 instead of "no data", and watch it during the instructor's CreditCardCheckError500 cue.

| ⌨  Task 3 — Error rate |
| :---- |
|  |
| \# Step 1: CUE C1 — the instructor announces "CreditCardCheckError500 ON"; write the time down and wait 2 minutes |
| \# Step 2: overall error rate (share of 5xx responses) |
| sum(rate(http\_server\_requests\_total{env="cohort",service="easytravel-frontend",status=\~"5.."}\[2m\])) / sum(rate(http\_server\_requests\_total{env="cohort",service="easytravel-frontend"}\[2m\])) |
| \# Step 3: per route — "or … \* 0" turns missing 5xx series into 0 |
| (sum by (route) (rate(http\_server\_requests\_total{env="cohort",service="easytravel-frontend",status=\~"5.."}\[2m\])) or sum by (route) (rate(http\_server\_requests\_total{env="cohort",service="easytravel-frontend"}\[2m\])) \* 0\) / sum by (route) (rate(http\_server\_requests\_total{env="cohort",service="easytravel-frontend"}\[2m\])) |
| \# Step 4: number of failed requests in the last 2 minutes, per route |
| sum by (route) (increase(http\_server\_requests\_total{env="cohort",service="easytravel-frontend",status=\~"5.."}\[2m\])) |
| \# Step 5: CUE C2 — the instructor announces "OFF"; write the time down |
| **📟  Expected Output** |
| Step 2: a small overall ratio (a few per cent of all frontend requests) |
| Step 3: /checkout clearly higher (tens of per cent) · other routes 0 |
| Step 4: failed requests only on /checkout (a few dozen in 2 minutes) |
| **3.A  Overall ≈ 7 % but checkout ≈ 35 %. Which number would you alert on, and why?**   Answer: The overall figure is diluted by healthy routes; the checkout route is the one customers cannot use. I would alert on the per-route (checkout) error ratio, because it shows the real impact and names the affected route. |
| **3.B  What happens to Step 3 without "or … \* 0" when a route has no 5xx series?**   Answer: A route without any 5xx series returns no data instead of 0, so it disappears from the result. "or … \* 0" creates a zero series for every route, so every route is shown. |

| ⚠️  STOP CHECK — The Fault Must Be OFF Before Aggregations |
| :---- |
| Before moving to Task 4, confirm the instructor announced cue C2 (fault OFF) and that your Step 3 result shows the checkout route higher than the others. Task 4 compares healthy traffic across routes and services. |
|  |
| If in doubt — show your instructor the Step 3 result before proceeding to Task 4\. |

# 

| TASK 4 — AGGREGATIONS: sum, avg, max, count, topk, by, without |
| :---- |

| 4 | Aggregate Series with Aggregation Operators*PromQL Fundamentals SOP — Day 4 — Lab 4* | ⏱ 6 min |
| :---: | :---- | :---: |

Aggregation operators combine many series into fewer. by keeps the listed labels, without removes them. You count series per service, find the busiest routes, compare by and without, and use avg and max over the services' CPU gauge.

| ⌨  Task 4 — Aggregations |
| :---- |
|  |
| count by (service) (http\_server\_requests\_total{env="cohort"}) |
| topk(2, sum by (route) (rate(http\_server\_requests\_total{env="cohort",service="easytravel-frontend"}\[5m\]))) |
| sum without (method, status) (rate(http\_server\_requests\_total{env="cohort",service="easytravel-frontend"}\[5m\])) |
| avg(rate(node\_cpu\_seconds\_total{mode="idle"}\[5m\])) |
| max by (mode) (rate(node\_cpu\_seconds\_total\[5m\])) |
| sum by (service) (rate(http\_server\_requests\_total{env="cohort"}\[5m\])) |
| **📟  Expected Output** |
| count by service: easytravel-frontend and easytravel-backend with a number of series each (one per route/status combination seen) |
| topk(2): the two busiest frontend routes with their req/s |
| without: one series per route (and other remaining labels) — the labels method and status are gone |
| avg idle: a value between 0 and 1 (share of idle CPU time per CPU, averaged) · max by mode: the largest per-CPU rate per CPU mode |
| requests per service: frontend higher than or similar to backend, because every frontend request calls the backend at most once |
| **4.A  Explain the difference between "sum by (route)" and "sum without (method, status)" using your output.**   Answer: sum by (route) keeps only the route label and drops all others. sum without (method, status) drops only those two labels and keeps every other label (service, job, instance …), which is safer when new labels appear. |
| **4.B  Why is the backend request rate similar to the frontend /checkout rate for checkout calls?**  Answer: Each frontend checkout request makes one call to the backend booking/payment service, so the backend rate for those calls follows the frontend /checkout rate; retries or other callers cause small differences. |

# 

# 5\. VALIDATION — CONFIRM FULL READINESS

Do not close the incident or call for instructor sign-off until ALL 8 validation steps below are completed and recorded.  
*Figure: Day 4 — Lab 4 — PromQL Fundamentals SOP Validation Checklist*

## 5.1  Validation Task Set

Validation Check 1 — Vectors explained

| ⌨  Validation 1 |
| :---- |
|  |
| Review Task 1 Steps 1–3 (Table and Graph tab output) |
| \# PASS criterion: instant vs range output and the type error explained |
| **V1: Can you explain instant and range vectors with your own output?**   Answer: Instant vectors return the latest value of each matching series, while range vectors return multiple samples over a specified time window. The range vector is used by functions like rate() and increase().  |

Validation Check 2 — Matchers

| ⌨  Validation 2 |
| :---- |
|  |
| Review Task 1 Step 4 |
| \# PASS criterion: correct counts for \=\~, \!\~ and \!= |
| **V2: Did your label matchers select the expected series?**   Answer: Yes. The regex matcher selected 2 routes, the status exclusion selected 1 series, and the service exclusion selected 3 series.  |

Validation Check 3 — rate() and increase()

| ⌨  Validation 3 |
| :---- |
|  |
| Graph page → run the Task 2 Step 1 rate query |
| \# PASS criterion: a steady req/s figure per route; the sum matches the frontend total |
| **V3: Do your rate queries return the easyTravel throughput?**   Answer: Yes — the per-route rates add up to the frontend total (record the req/s you read). |

Validation Check 4 — Counter reset

| ⌨  Validation 4 |
| :---- |
|  |
| Review answer 2.A |
| \# PASS criterion: resets ≥ 1 after cue R1, increase positive, delta negative, explanation correct |
| **V4: Did you observe and explain the counter reset?**   Answer: Yes — after cue R1 the counter started again at a small value; resets() detected it, increase() handled it and delta() gave a negative value.  |

Validation Check 5 — Error rate

| ⌨  Validation 5 |
| :---- |
|  |
| Review Task 3 |
| \# PASS criterion: small overall ratio and a clearly higher checkout ratio during the fault; 0 for other routes |
| **V5: Is your error rate correct overall and per route?**   Answer: Yes — during the fault the overall ratio was a few per cent while the checkout route was much higher; the other routes were about 0\.  |

Validation Check 6 — Aggregations

| ⌨  Validation 6 |
| :---- |
|  |
| Review Task 4 |
| \# PASS criterion: count, topk, by/without, avg/max interpreted correctly |
| **V6: Did you use the aggregation operators correctly?**   Answer: Yes. The count, topk, sum, avg, max, by and without operators executed successfully and returned the expected aggregations. |

Validation Check 7 — Fault off

| ⌨  Validation 7 |
| :---- |
|  |
| Write the three cue times next to your answers |
| \# PASS criterion: R1, C1 and C2 times recorded; fault announced OFF |
| **V7: Did you record the cues R1, C1 and C2?**  Answer: Yes — I wrote down the times of R1 (counter reset), C1 (fault ON) and C2 (fault OFF). |

Validation Check 8 — Full lab record complete

| ⌨  Validation 8 — Final completeness check |
| :---- |
|  |
| \# Confirm every answer box (Pre-Lab, 1.A through 4.B) is completed |
| \# Keep your Task 3 error-rate query for Lab 5 |
| **V8: Confirm all answer boxes are complete and your evidence is ready to show your instructor.**  Answer: Yes. All Pre-Lab and Task 1–4 answer sections have been completed, and the command outputs are available as evidence. |

**✅  STOP HERE — Show your completed validation record to your instructor before proceeding to Section 7\.**

# 

# 6\. TROUBLESHOOTING — COMMON ISSUES & FIXES

| Issue / Error | Cause | Diagnosis | Fix |
| :---- | :---- | :---- | :---- |
| Empty result for a matcher | Label value differs (case, slash) | Run the selector without that matcher | Copy label values from the Table tab |
| rate() returns nothing after cue R1 | Fewer than two samples in the window | Wait 30 s or use a longer window | Windows ≥ 4 × scrape interval |
| Error rate shows only checkout | 5xx series exist only for checkout | Run the numerator alone | Use the "or … \* 0" form |
| increase() not an integer | Extrapolation to window edges | Compare with rate × window | Expected behaviour; round for display |
| Prometheus UI does not open | Wrong IP or port, or the host is not reachable from your network | Re-check the URL http\://\<ec2-public-ip\>:9090/graph | Copy the URL again from the instructor |
| "Error executing query" in the UI | Parse error or a range vector where an instant vector is needed | Read the message under the query box | Fix quotes, braces and the vector type |

# 

# 7\. INSTRUCTOR DEBRIEF — 7 MINUTES

## 7.1  Discussion Questions

| Discussion 1 — Types First |
| :---- |
| Without notes: which of these return instant vectors: x, x\[5m\], rate(x\[5m\]), sum(rate(x\[5m\]))? |
| Why can you not graph x\[5m\] directly? |
|  |
| Key answer to explore: x, rate(), sum(rate()) are instant vectors; x\[5m\] is a range vector used as function input. |
| **Discussion 2 — Restarts** |
| What would a dashboard built on raw counters have shown after your restart? |
| Which other functions handle resets (rate, irate, increase) and which do not (delta, deriv)? |
|  |
| Key insight: counter functions handle resets; gauge functions do not and must not be used on counters. |
| **Discussion 3 — Ratios** |
| Why must numerator and denominator be aggregated with the same "by" clause? |
| Where else do you need ratios (cache hit rate, saturation)? |
|  |
| Key answer: matching labels on both sides; otherwise the division finds no partners or mixes groups. |
| **Discussion 4 — by vs without** |
| When is "without" safer than "by"? |
| What happens to dashboards when a new label is added to a metric? |
|  |
| Answer: without keeps unknown/new labels (e.g. instance) automatically; by drops everything not listed — choose deliberately. |

## 7.2  Common Mistakes — Learn From These

| Mistake | Why It Happens | Consequence | Prevention |
| :---- | :---- | :---- | :---- |
| Raw counters on graphs | They look like traffic | Meaningless, reset drops | rate() / increase() |
| delta() on counters | Name sounds right | Negative values after restarts | increase() |
| rate(sum(x)) | Aggregating first | Resets mis-handled | sum(rate(x)) |
| Different by on ratio sides | Copy-paste | Empty or wrong ratios | Same aggregation both sides |
| Too short windows | Want fast graphs | Gaps and noise | ≥ 4 × scrape interval; \$\_\_rate\_interval |

# 8\. EXTENSION TASKS (Advanced Learners)

| Extension A — irate vs rate |
| :---- |
| Graph irate(http\_server\_requests\_total{env="cohort",service="easytravel-frontend",route="/checkout"}\[1m\]) next to rate(…\[1m\]) and rate(…\[5m\]). |
| Describe the differences. |
| Key question: which would you alert on? |
| **Extension B — Gauges Over Time** |
| Query max\_over\_time(node\_load1\[10m\]) and avg\_over\_time(node\_memory\_MemAvailable\_bytes\[5m\]). |
| Why are \*\_over\_time functions right for gauges? |
| Compare with rate() on a gauge (what goes wrong?). |
| **Extension C — offset** |
| Compare sum(rate(http\_server\_requests\_total{env="cohort",service="easytravel-frontend"}\[5m\])) with the same query "offset 10m". |
| Build a "change vs 10 minutes ago" ratio. |
| Relate this to COMPARE WITH in NRQL. |

# 

# 9\. LAB COMPLETION & SIGN-OFF

## 9.1  Submission Checklist

| ✓ | Completion Criterion | Status |
| :---- | :---- | :---- |
| ☐ | Instant and range vectors read and the type error explained | ☐ Pass / ☐ Fail |
| ☐ | Label matchers \=, \!=, \=\~, \!\~ used | ☐ Pass / ☐ Fail |
| ☐ | rate() and increase() used; counter reset observed with resets(), increase() and delta() after cue R1 | ☐ Pass / ☐ Fail |
| ☐ | Error rate calculated overall and per route during the fault window (C1–C2) | ☐ Pass / ☐ Fail |
| ☐ | Aggregations with sum, avg, max, count, topk, by and without | ☐ Pass / ☐ Fail |
| ☐ | All 8 validation checks completed and all answer boxes filled in | ☐ Pass / ☐ Fail |

## 9.2  Grading Criteria

| Assessment Area | Criteria | Marks | Weight |
| :---- | :---- | :---- | :---- |
| Task 1 — Vectors & Matchers | Types and matchers explained | 20 | 20% |
| Task 2 — Rates & Resets | rate/increase correct; reset explained | 25 | 25% |
| Task 3 — Error Rate | Correct ratios; or-0 form; interpretation | 25 | 25% |
| Task 4 — Aggregations | Operators and by/without correct | 20 | 20% |
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

# 10\. QUICK REFERENCE — PROMQL FUNDAMENTALS COMMAND CARD

Bookmark this page. Every command you need in SOP order.

| Category | Command | Purpose |
| :---- | :---- | :---- |
| Instant vector | metric{label="v"} | Latest value per series |
| Range vector | metric{…}\[5m\] | Samples in window |
| Matchers | \= \!= \=\~ \!\~ (regex anchored) | Select series |
| Rate | rate(counter\[5m\]) | Per second, reset-safe |
| Increase | increase(counter\[5m\]) | Total in window |
| Resets | resets(counter\[10m\]) | Number of restarts |
| Error rate | sum(rate(x{status=\~"5.."}\[5m\])) / sum(rate(x\[5m\])) | Ratio |
| Zero instead of empty | (A or B \* 0\) / B | Missing series |
| by / without | sum by (route) (…) · sum without (method) (…) | Grouping |
| Ranking | topk(3, …) · bottomk(3, …) | Top / bottom |
| Statistics | avg · max · min · count · stddev | Across series |
| Gauges | avg\_over\_time / max\_over\_time(g\[5m\]) | Not rate() |

# APPENDIX A — INSTRUCTOR PRE-CLASS RUNBOOK (INSTRUCTOR ONLY)

INSTRUCTOR ONLY — learners never run these commands. Do this once, at least 30 minutes before the cohort. Commands run on the EC2 host ip-172-30-0-220.  
1\. Prometheus: the web UI on port 9090 must be reachable from the learners' network and read-only (start without \--web.enable-admin-api and \--web.enable-lifecycle). Open the security group for port 9090 only to the training network. Check Status → Targets: easyTravel, node and prometheus are UP and the scrape interval for easyTravel is 5s.  
2\. Metric contract: http\_server\_requests\_total{env="cohort",service,route,status} for easytravel-frontend and easytravel-backend (routes include /checkout and /search), and node\_exporter metrics (node\_cpu\_seconds\_total, node\_load1, node\_memory\_\*). Check with count by (service, route) (http\_server\_requests\_total) and fix the relabelling if the labels differ.

| ⌨  Instructor — cues (run on the EC2 host) |
| :---- |
|  |
| \# R1  start of Task 2 Step 2 (about T+14): restart the metrics exporter so counters reset; announce the time (container name as in your setup) |
| docker restart \<metrics-exporter-container\>; date \+%T |
| \# C1  start of Task 3 (about T+19): announce "CreditCardCheckError500 ON" and the time |
| ./faultctl.sh on |
| \# C2  end of Task 3 (about T+24): announce "OFF" and the time |
| ./faultctl.sh off |

3\. If the exporter cannot be restarted, skip cue R1 and show learners a prepared screenshot of resets() on a restarted series; mark this in the debrief. At the end confirm the fault is OFF.

| *Official Lab Guide — Day 4 — Lab 4: PromQL Fundamentals SOP  \|  IT Training Division  \|  NIIT iRUN Framework  \|  Version 2.0  \|  Classification: Internal Training* |
| :---: |

*IT Training Division  \|  NIIT iRUN Framework  \|  Confidential — For Training Use Only  \|  Do Not Distribute*