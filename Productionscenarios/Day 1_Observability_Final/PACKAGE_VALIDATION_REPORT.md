# Day 1 Package — Static Validation Report

## Updated in this release

- Preserved the existing `day1/` layout and S1/S2/S3 scenario directories.
- Reworked both participant and instructor guides for a sequential start → investigate → evidence → check → reset workflow.
- Added Linux execute-permission instructions immediately after extraction.
- Added explicit service navigation and working PromQL / LogQL examples.
- Added S2 no-cache rebuild, force-recreate and container-status recovery commands using project `telemetry-d1-s2`.
- Changed scenario Compose project names to `telemetry-d1-s1`, `telemetry-d1-s2`, and `telemetry-d1-s3`; controller start stops all three projects and also cleans the legacy shared `telemetry-d1` project name to reduce port/container-name collisions when upgrading an older extracted pack.
- Added readiness failure handling and Compose model validation before start.
- Updated S2 validation to accept a runtime 32-hex Trace ID and require the same ID in the Jaeger URL and Loki query.
- Added JSON syntax validation for S1/S3 evidence and stricter placeholder checks.
- Added S2 instructor-only worked evidence using a trace URL from the observed validation screenshots.
- Added `setuptools==80.9.0` to the pinned application dependencies as used during the successful S2 image rebuild.
- Added evidence backup/reset path documentation.

## Checks performed in this build environment

- Python syntax compilation of `shared/labctl.py`.
- Bash syntax validation of all three Linux scenario wrappers.
- Regex test for S2 markdown Trace ID, Jaeger URL and matching LogQL correlation.
- YAML parse validation for all Compose/configuration YAML files.
- JSON parse validation for all JSON files and dashboard/evidence artifacts.
- ZIP integrity test after packaging.

## Runtime validation limitation

Docker Engine is not available in this build environment, so this environment cannot launch containers or claim a fresh-VM end-to-end runtime test. The participant's observed successful run and screenshots are retained as the operational reference. Before client-wide distribution, execute the packaged start/check/reset workflow once on a clean Ubuntu VM using the included guides.


## Evidence and extraction corrections in this release

- Added `EVIDENCE_PASS_EXAMPLES.md` with complete S1/S3 JSON examples and an S2 actual-runtime-Trace-ID pattern.
- Updated participant and instructor Markdown/DOCX guides to point to the evidence examples.
- Corrected extraction instructions: extract the archive into `~`; because it contains `day1/`, the resulting path is `~/day1/`.
- Validator requirements were cross-checked against `shared/labctl.py`: S1 7/7, S2 5/5, S3 5/5 expected.
- Static checks do not constitute a live Docker runtime test; the recipient must run the scenario start/check commands on the target VM.
