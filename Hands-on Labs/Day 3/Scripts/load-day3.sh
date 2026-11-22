#!/usr/bin/env bash
# Loads the Day 3 dataset into Splunk. Needs SPLUNK_HOME and SPLUNK_AUTH (user:password).
set -e
S="$SPLUNK_HOME/bin/splunk"
for idx in d3_web d3_app d3_db d3_infra; do
  "$S" add index "$idx" -auth "$SPLUNK_AUTH" || echo "(index $idx may already exist)"
done
for h in web-01 web-02; do
  "$S" add oneshot "$PWD/web-$h.log" -index d3_web -sourcetype access_combined -host "$h" -auth "$SPLUNK_AUTH"; done
for h in app-01 app-02 app-03; do
  "$S" add oneshot "$PWD/app-$h.json" -index d3_app -sourcetype _json -host "$h" -auth "$SPLUNK_AUTH"; done
"$S" add oneshot "$PWD/db-db-01.log" -index d3_db -sourcetype postgresql_lab -host db-01 -auth "$SPLUNK_AUTH"
for h in app-01 app-02 app-03 db-01; do
  "$S" add oneshot "$PWD/syslog-$h.log" -index d3_infra -sourcetype syslog -host "$h" -auth "$SPLUNK_AUTH"; done
# File-based lookups (usable by file name: | lookup host_inventory.csv …, | inputlookup itsi_kpis.csv)
cp host_inventory.csv service_owners.csv itsi_kpis.csv itsi_health.csv "$SPLUNK_HOME/etc/apps/search/lookups/" \
  || sudo cp host_inventory.csv service_owners.csv itsi_kpis.csv itsi_health.csv "$SPLUNK_HOME/etc/apps/search/lookups/"
echo "Loaded. Wait ~30 s, then: index=d3_* earliest=0 | stats count by index, sourcetype, host"
