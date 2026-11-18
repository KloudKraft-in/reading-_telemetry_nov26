#!/usr/bin/env python3
"""Rough monthly observability cost model for Day 2 Lab 5.
The UNIT PRICES BELOW ARE EXAMPLE ASSUMPTIONS for the exercise, not any vendor's price list.
Replace them with your contract prices before using the numbers for decisions."""
import json, sys


PRICE = {"log_ingest_per_gb": 0.50, "log_retained_per_gb_month": 0.10,        # example only
         "span_ingest_per_million": 1.50, "span_retained_per_million_month": 0.20,
         "metric_series_per_1000_month": 5.00}
cfg = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else {}
S = {"log_gb_per_day": 40, "log_retention_days": 30, "spans_million_per_day": 120, "span_retention_days": 15,
     "active_series": 250000, **cfg}


def monthly(s):
    logs_ingest = s["log_gb_per_day"] * 30 * PRICE["log_ingest_per_gb"]
    logs_store = s["log_gb_per_day"] * s["log_retention_days"] * PRICE["log_retained_per_gb_month"]
    spans_ingest = s["spans_million_per_day"] * 30 * PRICE["span_ingest_per_million"]
    spans_store = s["spans_million_per_day"] * s["span_retention_days"] * PRICE["span_retained_per_million_month"]
    metrics = s["active_series"] / 1000 * PRICE["metric_series_per_1000_month"]
    return {"logs": logs_ingest + logs_store, "traces": spans_ingest + spans_store, "metrics": metrics}


def show(name, s):
    m = monthly(s); total = sum(m.values())
    print(f"{name:<36} logs {m['logs']:>9,.0f}   traces {m['traces']:>9,.0f}   metrics {m['metrics']:>9,.0f}   TOTAL {total:>10,.0f}")
    return total


print("Monthly cost estimate (example unit prices — currency units)")
base = show("Baseline", S)
scen = {
  "A: drop DEBUG logs (-40% GB)": {**S, "log_gb_per_day": S["log_gb_per_day"] * 0.6},
  "B: log retention 30 -> 7 days": {**S, "log_retention_days": 7},
  "C: trace sampling 100% -> 10%": {**S, "spans_million_per_day": S["spans_million_per_day"] * 0.1},
  "D: drop 2 unused labels (-30% series)": {**S, "active_series": S["active_series"] * 0.7},
  "E: add user_id label (x50 series)": {**S, "active_series": S["active_series"] * 50},
}
for name, s in scen.items():
    t = show(name, s)
    print(f"{'':<36} change vs baseline: {t - base:+,.0f} ({(t - base) / base * 100:+.0f}%)")
