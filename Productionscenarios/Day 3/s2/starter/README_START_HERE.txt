TEL-D3-302: Which App Is Failing? Ask Grail
===============================================================================
BROWSER-ONLY, SINGLE-PLATFORM SCENARIO (Dynatrace, easyTravel). No terminal, no Docker, no
local ports. Independent of S1 and S3: it needs only the shared Dynatrace tenant and the
instructor's easyTravel host.

HOW TO START:
1. Your instructor switches on the easyTravel fault CreditCardCheckError500 and announces
   the start time (UTC/IST). Write it in starter/evidence/evidence_D3_2.md.
2. Open https://xiz79164.apps.dynatrace.com and sign in.
3. Shared environment rules: read-only for shared objects; never close problems or edit other
   people's Notebooks. Name your Notebook u<seat>_TEL-D3-302. Always use a time filter.

OBSERVED FAILURE:
   Checkout fails on easyTravel and several processes log errors at the same time. Plain
   log search does not tell you WHICH process fails or WHAT error type dominates.

YOUR MISSION:
1. Apps > Notebooks > New notebook > name it u<seat>_TEL-D3-302. Add a DQL section.
2. Start from conf/grail_query_starter.dql and complete the summarize step (ErrorCount by
   process and error type).
3. Identify the top failing process and the dominant error type (CreditCardCheckError500).
4. Count failed requests by service (spans) and chart failures over time (timeseries).
5. Cross-check the CreditCardCheckError500 count in the Logs app with a content filter
   (same time range) and record both numbers.
6. Fill starter/evidence/evidence_D3_2.md.

SUBMISSION & EVIDENCE:
1. Fill every <<FILL_...>> field in starter/evidence/evidence_D3_2.md (paste exact queries, counts, screenshots).
2. Call your instructor for sign-off against the 5 rules in the Participant Guide.
===============================================================================
