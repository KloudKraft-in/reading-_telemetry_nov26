#!/usr/bin/env python3
"""Day 6 Lab 4 (AWS) - models two CloudWatch alarms on the metric-math error ratio (100 * HTTPCode_Target_5XX_Count / RequestCount) joined by a composite alarm: ALARM(Long) AND ALARM(Short). Replays three error scenarios through (a) the OLD threshold alert and (b) YOUR burn-rate alert from alert.conf.
  python3 replay_alert.py        (SLO 99.5 % -> error budget 0.5 %)"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); BUDGET = 0.005
def scenarios():
    spike = [0.0] * 20 + [0.30] * 2 + [0.0] * 98                   # 2-minute blip, 120 min
    outage = [0.0] * 20 + [0.40] * 60 + [0.0] * 40                 # real outage from minute 20
    leak = [0.012] * 360                                           # slow leak 1.2 % for 6 h
    return {"A brief spike (2 min)": (spike, None), "B real outage (starts minute 20)": (outage, 20), "C slow leak (6 h at 1.2 %)": (leak, None)}
def conf():
    c = {}
    for l in open(os.path.join(HERE, "alert.conf")):
        l = l.split("#")[0].strip()
        if "=" in l:
            k, v = l.split("=", 1); c[k.strip()] = v.strip()
    return dict(long_period_min=int(c["long_period_min"]), short_period_min=int(c["short_period_min"]), burn_threshold=float(c["burn_threshold"]), for_min=int(c.get("for_min", 0)))
def avg(s, i, w): return sum(s[max(0, i - w + 1):i + 1]) / w     # before the data starts the ratio counts as 0
def old_first_page(s):                        # old rule: error ratio > 1 % for 1 minute
    return next((i for i, v in enumerate(s) if v > 0.01), None)
def new_first_page(s, c):
    run = 0
    for i in range(len(s)):
        if avg(s, i, c["long_period_min"]) / BUDGET >= c["burn_threshold"] and avg(s, i, c["short_period_min"]) / BUDGET >= c["burn_threshold"]:
            run += 1
            if run > c["for_min"]: return i
        else: run = 0
    return None
def results():
    c = conf(); out = {}
    for name, (s, start) in scenarios().items(): out[name] = (old_first_page(s), new_first_page(s, c), start)
    return out
if __name__ == "__main__":
    c = conf(); print("your rule: burn >= %.1f over %d min AND %d min, for %d min\n" % (c["burn_threshold"], c["long_period_min"], c["short_period_min"], c["for_min"]))
    for name, (o, n, st) in results().items():
        print("%-34s old threshold alert: %-22s your burn-rate alert: %s" % (name, "PAGE at min %d" % o if o is not None else "no page", "PAGE at min %d" % n if n is not None else "no page"))
