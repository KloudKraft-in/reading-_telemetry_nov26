#!/usr/bin/env python3
"""Shop simulator for Day 6 Labs 2 and 4 - runs every minute on the lab EC2 instance (cron).
Publishes CloudWatch custom metrics (namespace from NAMESPACE) and writes JSON app log lines and system log lines that the
CloudWatch agent ships to CloudWatch Logs. SYNTHETIC data. With --backfill it first creates the last 3 hours of history."""
import json, os, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shopmodel import minute_stats, is_bad
SEAT = os.environ.get("SEAT", "u00"); REGION = os.environ.get("AWS_DEFAULT_REGION", ""); NS = os.environ.get("NAMESPACE", "ShopLab")
def stamp(ts): return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(ts))
def metric(name, v, unit, ts):
    return {"MetricName": name, "Dimensions": [{"Name": "Service", "Value": "checkout"}], "Timestamp": stamp(ts) + "Z", "Value": v, "Unit": unit}
def minute(ts, host):
    m = time.gmtime(ts).tm_min; req, err, p95, disk = minute_stats(m); base = ts - ts % 60; app, sysl = [], []
    for i in range(3): app.append(json.dumps({"ts": stamp(base + 5 + i * 15), "level": "INFO", "service": "checkout", "message": "Order completed"}))
    for i in range(err):
        msg = "Order write failed: No space left on device (/data/orders)" if is_bad(m) else "Order write retry succeeded"
        app.append(json.dumps({"ts": stamp(base + min(59, int(i * 59 / max(err, 1)))), "level": "ERROR", "service": "checkout", "status": 503, "message": msg}))
    sysl.append("%s %s systemd[1]: Started shop-sim.service" % (stamp(base + 1), host))
    if is_bad(m): sysl.append("%s %s kernel: XFS (nvme1n1): metadata I/O error: No space left on device (data volume at %d%%)" % (stamp(base + 10), host, disk))
    md = [metric("RequestCount", req, "Count", base), metric("Errors5xx", err, "Count", base), metric("LatencyP95Ms", p95, "Milliseconds", base), metric("DataDiskUsedPercent", disk, "Percent", base)]
    return md, app, sysl
def put(md):
    for i in range(0, len(md), 80):
        subprocess.run(["aws", "cloudwatch", "put-metric-data", "--namespace", NS, "--metric-data", json.dumps(md[i:i + 80]), "--region", REGION], check=False)
os.makedirs("/var/log/shop", exist_ok=True); host = os.uname()[1]; now = time.time()
if "--backfill" in sys.argv:
    allm, apps, syss = [], [], []
    for k in range(180, 0, -1):
        md, a, s = minute(now - k * 60, host); allm += md; apps += a; syss += s
    put(allm); open("/var/log/shop/app.log", "a").write("\n".join(apps) + "\n"); open("/var/log/shop/system.log", "a").write("\n".join(syss) + "\n")
md, a, s = minute(now, host); put(md)
open("/var/log/shop/app.log", "a").write("\n".join(a) + "\n"); open("/var/log/shop/system.log", "a").write("\n".join(s) + "\n")
