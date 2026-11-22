#!/usr/bin/env bash
# faultctl.sh — switch the easyTravel CreditCardCheckError500 fault ON/OFF (run on the EC2 host ip-172-30-0-220).
# Usage: ./faultctl.sh on|off
set -e
case "${1:?usage: faultctl.sh on|off}" in on) v=true;; off) v=false;; *) echo "use on|off"; exit 1;; esac
curl -s "http://localhost:8091/services/ConfigurationService/setPluginEnabled?name=CreditCardCheckError500&enabled=$v" >/dev/null
echo "$(date '+%H:%M:%S %Z')  ANNOUNCE: CreditCardCheckError500 fault is now $( [ $v = true ] && echo ON || echo OFF )"
