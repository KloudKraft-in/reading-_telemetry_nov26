#!/usr/bin/env python3
"""Day 5 Lab 5 — writes alert-history.csv: 7 days of alert notifications of the shop (17-23 Oct 2026), seed 7007.
Columns: fired_at, resolved_at, alertname, service, severity, duration_min, acknowledged, incident"""
import csv, random
from datetime import datetime, timedelta, timezone
random.seed(7007)
T0 = datetime(2026, 10, 17, tzinfo=timezone.utc)
rows = []
def add(t, name, svc, sev, dur, ack=False, inc=""):
    rows.append([t, t + timedelta(minutes=dur), name, svc, sev, dur, "yes" if ack else "no", inc])
def when(): return T0 + timedelta(seconds=random.randint(0, 7 * 86400 - 3600))
for svc, n in (("checkout", 112), ("frontend", 44)):                      # CPU above 25 % flaps all week
    for _ in range(n): add(when(), "HighCPU", svc, "critical", random.randint(1, 6))
incidents = [(T0 + timedelta(days=1, hours=14, minutes=20), "INC-4101", 18), (T0 + timedelta(days=3, hours=9, minutes=5), "INC-4117", 25),
             (T0 + timedelta(days=5, hours=20, minutes=40), "INC-4130", 12)]
for t, inc, dur in incidents:                                            # three real DB-pool incidents
    add(t, "DbPoolSaturated", "inventory", "critical", dur, True, inc)
    add(t + timedelta(seconds=40), "AnyServerError", "frontend", "critical", dur - 1, True, inc)
    add(t + timedelta(seconds=70), "CheckoutSlow", "frontend", "warning", dur - 2, True, inc)
    add(t + timedelta(seconds=95), "CheckoutLatencyP95", "checkout", "warning", dur - 2, False, inc)
for _ in range(81): add(when(), "AnyServerError", "frontend", "critical", random.randint(1, 2))   # single 5xx responses
for _ in range(59):                                                      # p95 slightly above 0.2 s, two rules for the same symptom
    t, d = when(), random.randint(2, 15)
    add(t, "CheckoutSlow", "frontend", "warning", d); add(t + timedelta(seconds=random.randint(5, 50)), "CheckoutLatencyP95", "checkout", "warning", d)
add(T0 + timedelta(days=4, hours=2, minutes=12), "ShopSimDown", "shopsim", "critical", 4, True, "INC-4122")
rows.sort(key=lambda r: r[0])
with open("alert-history.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["fired_at", "resolved_at", "alertname", "service", "severity", "duration_min", "acknowledged", "incident"])
    for r in rows: w.writerow([r[0].strftime("%Y-%m-%dT%H:%M:%SZ"), r[1].strftime("%Y-%m-%dT%H:%M:%SZ")] + r[2:])
print(f"alert-history.csv: {len(rows)} notifications, {len({r[7] for r in rows if r[7]})} incidents")
