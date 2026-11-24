#!/usr/bin/env bash
# Day 5 Lab 4 — switch the ShopSim fault: ./scripts/fault.sh db-pool | payment-slow | none
cd "$(dirname "$0")/.."
case "${1:-}" in none|db-pool|payment-slow) echo "$1" > control/fault; echo "fault = $1";; *) echo "usage: $0 none|db-pool|payment-slow"; exit 1;; esac
