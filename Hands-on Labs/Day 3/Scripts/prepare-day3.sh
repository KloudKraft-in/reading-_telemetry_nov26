#!/usr/bin/env bash
# Day 3 pre-lab: unzip this kit on top of the Day 2 kit (same ~/obs-lab folder), then run: bash prepare-day3.sh
cd "$(dirname "$0")"
ok(){ echo "  [ OK ] $*"; }; warn(){ echo "  [WARN] $*"; }; die(){ echo "  [FAIL] $*"; exit 1; }
[ -f docker-compose.day2.yml ] && [ -f docker-compose.yml ] || die "Day 2 kit not found in $(pwd) - unzip obs-lab-day2-kit.zip first"
[ -f .env ] || { cp .env.example .env 2>/dev/null && chmod 600 .env && warn ".env created - fill in your vendor keys"; }
mkdir -p day3/monitors
echo none > control/fault; ok "fault switch = none"
# keys that only Day 3 needs (placeholders; fill the ones for the labs you do)
grep -q '^DT_CLASSIC_TOKEN=' .env || echo 'DT_CLASSIC_TOKEN=<dynatrace-classic-token-with-events.ingest>' >> .env
grep -q '^DD_APP_KEY=' .env || echo 'DD_APP_KEY=<datadog-application-key>' >> .env
ok ".env has DT_CLASSIC_TOKEN and DD_APP_KEY entries (Labs 3 and 5)"
if [ -z "$(ls day3/web-*.log 2>/dev/null)" ]; then (cd day3 && python3 gen-day3.py) && ok "Splunk dataset generated"; else ok "Splunk dataset present ($(ls day3/*.log day3/*.json day3/*.csv 2>/dev/null | wc -l) files)"; fi
if [ -d "${SPLUNK_HOME:-/opt/splunk}" ]; then ok "Splunk found at ${SPLUNK_HOME:-/opt/splunk}  -> Lab 1: export SPLUNK_HOME=${SPLUNK_HOME:-/opt/splunk} SPLUNK_AUTH='admin:<password>'; cd day3; bash load-day3.sh"; else warn "Splunk not found at /opt/splunk (needed for Labs 1-2; installed in Day 2 Lab 3)"; fi
bash ./check-day3.sh
