#!/usr/bin/env bash
# Read-only Day 3 check.
cd "$(dirname "$0")"; P=0; F=0
pass(){ echo "  PASS  $*"; P=$((P+1)); }; fail(){ echo "  FAIL  $*"; F=$((F+1)); }; warn(){ echo "  WARN  $*"; }
[ "$(ls day3/web-*.log 2>/dev/null | wc -l)" -ge 2 ] && pass "Splunk dataset files present (day3/)" || fail "dataset missing - run: cd day3 && python3 gen-day3.py"
[ -f day3/load-day3.sh ] && pass "load-day3.sh present" || fail "load-day3.sh missing"
ls day3/monitors/mon-a.json day3/monitors/mon-b.json >/dev/null 2>&1 && pass "Datadog monitor JSON files present" || fail "monitor JSON files missing"
[ -f otel/collector-dynatrace-d3.yaml ] && pass "Dynatrace Day 3 collector config present" || fail "otel/collector-dynatrace-d3.yaml missing"
[ "$(cat control/fault 2>/dev/null)" = "none" ] && pass "fault switch = none" || warn "fault switch = '$(cat control/fault 2>/dev/null)'"
for k in DT_ENV_URL DT_API_TOKEN DT_CLASSIC_TOKEN DD_API_KEY DD_APP_KEY; do grep -q "^$k=<" .env 2>/dev/null && warn "$k still a placeholder (only needed for its own lab)"; done
if [ -n "${SPLUNK_AUTH:-}" ] && [ -x "${SPLUNK_HOME:-/opt/splunk}/bin/splunk" ]; then
  "${SPLUNK_HOME:-/opt/splunk}/bin/splunk" list index -auth "$SPLUNK_AUTH" 2>/dev/null | grep -c '^d3_' | xargs -I{} echo "  INFO  Splunk d3_* indexes found: {} (expected 4 after load-day3.sh)"; fi
for v in dynatrace-d3 datadog; do cmp -s otel/collector.yaml otel/collector-$v.yaml && echo "  INFO  active collector: $v"; done
echo "Result: $P passed, $F failed"; [ $F -eq 0 ]
