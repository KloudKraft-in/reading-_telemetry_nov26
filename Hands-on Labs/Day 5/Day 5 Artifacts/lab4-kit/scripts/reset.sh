#!/usr/bin/env bash
# Day 5 Lab 4 — back to the starting state (deletes your Grafana changes and Prometheus data). Run: ./scripts/reset.sh
cd "$(dirname "$0")/.."
echo none > control/fault
docker compose down -v && ./scripts/setup.sh
