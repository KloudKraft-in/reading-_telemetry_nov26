#!/usr/bin/env bash
# Day 5 Lab 5 — check the starting state (expected: all OK). Needs curl and python3.
cd "$(dirname "$0")/.."
ok(){ printf '  OK    %s\n' "$1"; }; bad(){ printf '  FAIL  %s\n' "$1"; rc=1; }; rc=0
[ "$(curl -s -o /dev/null -w '%{http_code}' localhost:9090/-/ready)" = 200 ] && ok "Prometheus ready (http://localhost:9090)" || bad "Prometheus not ready"
[ "$(curl -s -o /dev/null -w '%{http_code}' localhost:9093/-/ready)" = 200 ] && ok "Alertmanager ready (http://localhost:9093)" || bad "Alertmanager not ready"
[ "$(curl -s -o /dev/null -w '%{http_code}' localhost:9095/runbooks/RB-DB-003.html)" = 200 ] && ok "Webhook sink and runbook server (http://localhost:9095)" || bad "webhook-sink not reachable"
n=$(curl -s --get localhost:9090/api/v1/query --data-urlencode 'query=sum(rate(http_server_requests_total{env="lab",service="frontend"}[1m]))' | python3 -c 'import sys,json;r=json.load(sys.stdin)["data"]["result"];print(r[0]["value"][1][:5] if r else "")')
[ -n "$n" ] && ok "ShopSim traffic ≈ $n req/s (expected ≈ 8)" || bad "no ShopSim metrics yet (wait 30 s and retry)"
f=$(curl -s localhost:9090/api/v1/alerts | python3 -c 'import sys,json;print(sum(a["state"]=="firing" for a in json.load(sys.stdin)["data"]["alerts"]))')
echo "  INFO  firing alerts now: $f (0 at the start; 4–5 after you load noisy-rules.yml in Task 1)"
[ "$(cat control/fault)" = none ] && ok "Fault switch: none" || bad "Fault switch is not 'none'"
exit $rc
