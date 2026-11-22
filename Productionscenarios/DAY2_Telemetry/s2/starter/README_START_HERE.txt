TEL-D2-202: Datadog Monitor Fires: Find the Cause
===============================================================================
BROWSER-ONLY, SINGLE-PLATFORM SCENARIO (Datadog). No terminal, no Docker, no local ports.

HOW TO START:
1. Your instructor starts the incident and announces the start time (UTC/IST).
   Write it in starter/evidence/evidence_D2_2.md (copy provided as Word/Google Doc).
2. Open Datadog. Set the time range to Last 2 hours.
3. Shared environment rules: read-only; never close/mute/edit shared problems,
   monitors, dashboards or alert rules. Name anything you create with u<seat>_.

YOUR MISSION:
1. Open https://app.datadoghq.com > Monitors; open the easyTravel (env:cohort) composite or [SHARED] error-rate monitor; record time and thresholds.
2. APM > Traces: env:cohort service:easytravel-backend status:error; open a failed trace and copy its trace ID.
3. Logs > Explorer: env:cohort status:error @trace_id:<your-trace-id>; read the matching log lines.
4. Isolate the failing component and error signature (expected: CreditCardCheckError500).
5. State whether the monitor, trace and log views agree.

SUBMISSION & EVIDENCE:
1. Fill every <<FILL_...>> field in starter/evidence/evidence_D2_2.md
   (paste exact queries / screen paths / links; add screenshots).
2. Call your instructor for sign-off against the 5 rules in the Participant Guide.
===============================================================================
