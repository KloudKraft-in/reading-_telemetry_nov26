#!/usr/bin/env bash
# Day 5 Lab 4 — check the starting state (expected: all OK). Needs curl; jq is optional.
cd "$(dirname "$0")/.."
. ./.env 2>/dev/null || true; PW="${GRAFANA_PASSWORD:-admin}"
ok(){ printf '  OK    %s\n' "$1"; }; bad(){ printf '  FAIL  %s\n' "$1"; rc=1; }; rc=0
q(){ curl -s --get localhost:9090/api/v1/query --data-urlencode "query=$1" | python3 -c 'import sys,json;r=json.load(sys.stdin)["data"]["result"];print(r[0]["value"][1] if r else "")'; }
[ "$(curl -s -o /dev/null -w '%{http_code}' localhost:9090/-/ready)" = 200 ] && ok "Prometheus ready (http://localhost:9090)" || bad "Prometheus not ready"
[ "$(curl -s -o /dev/null -w '%{http_code}' localhost:3000/api/health)" = 200 ] && ok "Grafana healthy (http://localhost:3000)" || bad "Grafana not healthy"
r=$(q 'sum(rate(http_server_requests_total{env="lab",service="frontend"}[1m]))'); [ -n "$r" ] && ok "ShopSim traffic ≈ ${r:0:5} req/s (expected ≈ 8)" || bad "no ShopSim metrics yet (wait 30 s and retry)"
c=$(curl -s -u "admin:$PW" localhost:3000/api/search?query=Shop | python3 -c 'import sys,json;print(" ".join(x["uid"] for x in json.load(sys.stdin)))' 2>/dev/null); case "$c" in *shop-overview*) ok "Shop Overview provisioned (uid shop-overview)";; *) bad "Shop Overview missing or wrong Grafana password (.env GRAFANA_PASSWORD)";; esac
[ "$(curl -s -o /dev/null -w '%{http_code}' localhost:9095/runbooks/RB-CHK-002.html)" = 200 ] && ok "Runbook server (http://localhost:9095/runbooks/RB-CHK-002.html)" || bad "Runbook server not reachable"
[ "$(cat control/fault)" = none ] && ok "Fault switch: none" || bad "Fault switch is not 'none'"
exit $rc
