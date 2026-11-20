DAY 1 — READING TELEMETRY & OBSERVABILITY
FINAL VALIDATION RELEASE

CONTENTS
- Participant_Guide_day1.docx / .md
- Instructor_Solution_Guide_day1.docx / .md (INSTRUCTOR ONLY)
- s1, s2, s3 scenario stacks, starter files, baseline files and validation wrappers
- shared/labctl.py and shared/app simulator source/dependencies
- instructor/reference_answers/S2_REFERENCE_EVIDENCE_TEL-D1-102.md (INSTRUCTOR ONLY)

START HERE
1. Extract this ZIP into your home directory (~), not into an existing ~/day1 directory. The archive already contains day1/, so the result is ~/day1/.
2. Verify Docker, Compose v2, Python 3 and curl: docker info; docker compose version; python3 --version; curl --version.
3. On Linux, from the day1 folder run:
   chmod +x s1/validation_script.sh s2/validation_script.sh s3/validation_script.sh shared/labctl.py
4. Open the Participant Guide and EVIDENCE_PASS_EXAMPLES.md. The evidence guide shows exactly what to enter for all three scenarios and what the validators require. Run one scenario at a time from its own folder.
5. Standard commands: ./validation_script.sh start | check | reset
6. Reset each scenario before moving to the next. `start` also stops other Day 1 scenario projects as a safety measure.

S2 TRACE-ID NOTE
Trace IDs are runtime values. Capture the 32-character ID from the Jaeger browser URL and use the same value in the evidence Jaeger URL and Loki LogQL query. Do not rely on a fixed trace ID.

S2 RECOVERY NOTE
Only if the S2 build/containers fail, from ~/day1/s2 run the three recovery commands shown in the Participant Guide: build --no-cache; up -d --force-recreate; ps.

EVIDENCE AND RESET
Participants edit only files under each scenario's starter/ folder. The controller restores from lab/baseline/. Before restore, modified starter files are backed up beside the file with a .bak-<timestamp> suffix. Preserve those backups before reset if required.

SECURITY / SAFETY
All data and services are synthetic and local to the lab. Do not connect to production systems. S3 /pg_stat_activity is a simulator; do not kill real database processes. Instructor guide and instructor/reference_answers are not participant handouts.
