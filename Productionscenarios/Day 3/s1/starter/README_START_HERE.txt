TEL-D3-301: Error Spike on One Host After a Release
===============================================================================
LOCAL DOCKER SCENARIO (Splunk). Self-contained: it needs only Docker. It does not
depend on S2 or S3 and no shared server.

SETUP (once, about 5-10 minutes; first run downloads the Splunk image, about 1 GB):
  Requirements : Docker + Docker Compose v2, 4 GB free RAM, 6 GB free disk, port 8000 free
  Ubuntu/macOS : ./validation_script.sh start
  Windows      : .\validation_script.ps1 start
  Then open    : http://localhost:8000   (user admin, password printed by the script)
  Verify       : index=retail_* earliest=-4h | stats count by index
                 -> retail_checkout 3000, retail_web 2400 (wait about 1 minute after start)

OBSERVED FAILURE:
  Post-deployment error rate surges to 8.4%. Standard log searches fail to extract
  unstructured error codes from application logs on host web-prod-04.

YOUR MISSION:
1. Host breakdown: (index=retail_web OR index=retail_checkout) earliest=-4h | stats count by host, sourcetype | sort -count
2. Isolate the culprit host (web-prod-04, about 92% of errors).
3. Extract error codes: rex field=_raw "status_code=(?<err_code>ERR-[0-9]{4})"
4. Chart them: timechart span=15m count by err_code
5. Group sessions: index=retail_checkout earliest=-4h | transaction session_id maxspan=30m | where duration > 10 | table session_id, duration, eventcount
6. Fill starter/evidence/evidence_D3_1.md.

SUBMISSION & EVIDENCE:
1. Fill every <<FILL_...>> field in starter/evidence/evidence_D3_1.md
2. Self-check:  ./validation_script.sh check   (Windows: .\validation_script.ps1 check)
3. Call your instructor for sign-off against the 5 rules in the Participant Guide.
4. Clean up when done: ./validation_script.sh reset   (Windows: .\validation_script.ps1 reset)

Troubleshooting: "docker logs tel-d3-301-splunk | tail -30"; if port 8000 is busy, stop the
other program; if Splunk keeps restarting, give Docker at least 4 GB RAM.
===============================================================================
