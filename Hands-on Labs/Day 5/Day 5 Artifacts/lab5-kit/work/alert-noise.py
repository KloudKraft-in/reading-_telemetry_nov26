#!/usr/bin/env python3
"""Day 5 Lab 5 — alert noise report from alert-history.csv: volume, flapping, actionability and duplicates per alert."""
import csv, statistics, sys
from collections import defaultdict
from datetime import datetime
rows = list(csv.DictReader(open(sys.argv[1] if len(sys.argv) > 1 else "alert-history.csv")))
ts = lambda s: datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")
by = defaultdict(list)
for r in rows: by[r["alertname"]].append(r)
fires = {a: sorted(ts(r["fired_at"]) for r in rs) for a, rs in by.items()}
def dup_of(a):                         # another alert that fires within 2 minutes of >= 80 % of this alert's notifications
    best = ("", 0.0)
    for b in fires:
        if b == a: continue
        hit = sum(any(abs((t - u).total_seconds()) <= 120 for u in fires[b]) for t in fires[a]) / len(fires[a])
        if hit > best[1]: best = (b, hit)
    return f"{best[0]} ({best[1]:.0%})" if best[1] >= 0.8 else "-"
print(f"{'alert':<20}{'sev':<9}{'fires':>6}{'/day':>6}{'median min':>11}{'<5 min':>8}{'acked':>7}{'incidents':>10}  duplicate of")
for a, rs in sorted(by.items(), key=lambda kv: -len(kv[1])):
    d = [int(r["duration_min"]) for r in rs]
    print(f"{a:<20}{rs[0]['severity']:<9}{len(rs):>6}{len(rs) / 7:>6.1f}{statistics.median(d):>11.0f}{sum(x < 5 for x in d) / len(d):>8.0%}"
          f"{sum(r['acknowledged'] == 'yes' for r in rs) / len(rs):>7.0%}{len({r['incident'] for r in rs if r['incident']}):>10}  {dup_of(a)}")
act = sum(r["incident"] != "" for r in rows)
print(f"\nTOTAL {len(rows)} notifications in 7 days ({len(rows) / 7:.0f}/day) · linked to an incident: {act} ({act / len(rows):.1%}) · incidents: {len({r['incident'] for r in rows if r['incident']})}")
