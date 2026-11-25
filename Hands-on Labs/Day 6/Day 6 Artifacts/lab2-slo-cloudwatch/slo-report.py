#!/usr/bin/env python3
"""Day 6 Lab 2 - SLO and error-budget report.  Usage: python3 slo-report.py [availability_objective] [latency_objective]  (defaults 0.995 0.99)"""
import csv, os, sys
from datetime import datetime
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
A = float(sys.argv[1]) if len(sys.argv) > 1 else 0.995
Lo = float(sys.argv[2]) if len(sys.argv) > 2 else 0.99
rows = list(csv.DictReader(open(os.path.join(D, "sli-history.csv"))))
total = sum(int(r["RequestCount"]) for r in rows); err = sum(int(r["HTTPCode_Target_5XX_Count"]) for r in rows); slow = sum(int(r["requests_over_500ms"]) for r in rows)
def rep(name, bad, obj):
    sli, allowed = 1 - bad / total, total * (1 - obj)
    print("%-13s SLI %.4f%%  objective %.2f%%  bad %s of %s  budget %.0f  consumed %.1f%%  remaining %.1f%%  %s" % (name, sli * 100, obj * 100, format(bad, ","), format(total, ","), allowed, 100 * bad / allowed, 100 * (1 - bad / allowed), "MET" if sli >= obj else "MISSED"))
print("Window %s .. %s (%d days), ALB checkout target group (CloudWatch)" % (rows[0]["date"], rows[-1]["date"], len(rows)))
rep("Availability", err, A); rep("Latency<0.5s", slow, Lo)
allowed = total * (1 - A)
print("\nWorst days (share of the 28-day availability budget used that day):")
for r in sorted(rows, key=lambda r: -int(r["HTTPCode_Target_5XX_Count"]))[:3]:
    print("  %s errors %s = %.1f%%" % (r["date"], format(int(r["HTTPCode_Target_5XX_Count"]), ","), 100 * int(r["HTTPCode_Target_5XX_Count"]) / allowed))
inc = list(csv.DictReader(open(os.path.join(D, "incidents.csv"))))
t = lambda s: datetime.strptime(s, "%Y-%m-%d %H:%M")
ttd = [(t(i["detected"]) - t(i["started"])).seconds / 60 for i in inc]; ttr = [(t(i["resolved"]) - t(i["started"])).seconds / 60 for i in inc]
print("\nOperational KPIs: incidents %d | MTTD %.1f min | MTTR %.1f min | incident share of budget %.1f%%" % (len(inc), sum(ttd) / len(ttd), sum(ttr) / len(ttr), 100 * sum(int(i["bad_requests"]) for i in inc) / allowed))
