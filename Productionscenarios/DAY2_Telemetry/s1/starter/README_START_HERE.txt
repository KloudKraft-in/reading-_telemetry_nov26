TEL-D2-201: Davis Opened a Problem: Find the Root Cause
===============================================================================
BROWSER-ONLY SCENARIO. No terminal, no Docker, no local ports.

HOW TO START:
1. Your instructor starts the incident and announces the start time (UTC/IST).
   Write it in starter/evidence/evidence_D2_1.md (copy provided as Word/Google Doc).
2. Open: Dynatrace Problems app, Smartscape, PurePaths. Set the time range to Last 2 hours.
3. Shared environment rules: read-only; never close/mute/edit shared problems,
   monitors, dashboards or alert rules. Name anything you create with u<seat>_.

YOUR MISSION:
1. Open https://qcw66226.live.dynatrace.com (group Cohort-40) > Problems, timeframe Last 2 hours.
2. Open the Davis problem on easyTravel; record title, start time and the Root cause entity.
3. Follow the flow in Smartscape/Services frontend -> backend -> credit-card check.
4. Open Distributed traces/PurePaths filtered by failed requests; open one.
5. Isolate the failing span or exception (expected: CreditCardCheckError500).

SUBMISSION & EVIDENCE:
1. Fill every <<FILL_...>> field in starter/evidence/evidence_D2_1.md
   (paste exact queries / screen paths / links; add one screenshot per platform).
2. Call your instructor for sign-off. The instructor checks your evidence in the
   browser against the 5 rules in the Participant Guide.
===============================================================================
