TEL-D3-303: The Error Monitor That Never Fires
===============================================================================
BROWSER-ONLY, SINGLE-PLATFORM SCENARIO (Datadog, easyTravel). No terminal, no Docker, no
local ports. Independent of S1 and S2: it needs only the Datadog organisation and the
instructor's easyTravel host.

HOW TO START:
1. Your instructor switches on the easyTravel fault CreditCardCheckError500 and announces
   the start time (UTC/IST). Write it in starter/evidence/evidence_D3_3.json.
2. Open https://app.datadoghq.com, set the time range to Past 1 Hour.
3. Shared environment rules: never edit or mute [SHARED] monitors. Name everything you create
   [u<seat>] with tags lab:d3-303 and u<seat>. Notify nobody (or only your own e-mail).

OBSERVED FAILURE:
   Checkout on easyTravel is failing (CreditCardCheckError500 in the logs), yet the shared
   monitor [SHARED][BROKEN] easyTravel Backend Errors (TEL-D3-303) stays green / No Data.

YOUR MISSION:
1. Monitors > Manage Monitors > open [SHARED][BROKEN] easyTravel Backend Errors (TEL-D3-303).
   Record its query (see conf/datadog_monitor_broken.json) and status.
2. Find the two defects: (1) the wrong environment tag, (2) an average of a raw error count
   instead of an error ratio. Prove (1) in Metrics Explorer: graph the broken query, then
   the same query with env:cohort.
3. Create monitor A in the UI (Monitors > New Monitor > Metric > Source toggle): error ratio
   sum(last_5m): errors / hits * 100 > 5 on env:cohort, service:easytravel-backend.
4. Create monitor B (Logs): CreditCardCheckError500 count > 10 in 5 minutes.
5. Create a composite monitor "A && B". Read the states of A, B and the composite while the fault is on.
6. Fill starter/evidence/evidence_D3_3.json. Delete your three monitors at the end (composite first).

SUBMISSION & EVIDENCE:
1. Fill every <<FILL_...>> field (paste exact queries, IDs, states, screenshots).
2. Call your instructor for sign-off against the 5 rules in the Participant Guide.
===============================================================================
