#!/usr/bin/env bash
# post_deploy_event.sh — records the easyTravel deployment event in Dynatrace (Day 3 Lab 3, cue T+0).
# Needs DT_ENV_URL (https://<env-id>.live.dynatrace.com) and DT_API_TOKEN (scope events.ingest) in the environment.
: "${DT_ENV_URL:?set DT_ENV_URL}"; : "${DT_API_TOKEN:?set DT_API_TOKEN}"
curl -sS -X POST "$DT_ENV_URL/api/v2/events/ingest" \
  -H "Authorization: Api-Token $DT_API_TOKEN" -H "Content-Type: application/json; charset=utf-8" \
  -d '{"eventType":"CUSTOM_DEPLOYMENT","title":"easyTravel Checkout Service v2.4.1 Rollout","entitySelector":"type(HOST),entityName.equals(\"ip-172-30-0-220\")","properties":{"deployment.name":"easyTravel Checkout Service v2.4.1 Rollout","deployment.version":"v2.4.1","source":"instructor-runbook"}}'
echo; date '+%H:%M:%S %Z  ANNOUNCE: Deploy easyTravel Checkout Service v2.4.1 recorded'
