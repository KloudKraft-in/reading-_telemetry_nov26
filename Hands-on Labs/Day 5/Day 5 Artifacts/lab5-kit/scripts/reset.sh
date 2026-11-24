#!/usr/bin/env bash
# Day 5 Lab 5 — back to the starting state: noisy rules removed, starting Alertmanager config restored, volumes deleted.
cd "$(dirname "$0")/.."
echo none > control/fault
rm -f prometheus/rules/noisy-rules.yml prometheus/rules/tuned-rules.yml prometheus/rules/tuned-rules.test.yml
[ -f prometheus/rules/alerts.yml ] || cp work/alerts-baseline.yml prometheus/rules/alerts.yml 2>/dev/null || true
cp work/alertmanager-start.yml alertmanager/alertmanager.yml
docker compose down -v && ./scripts/setup.sh
