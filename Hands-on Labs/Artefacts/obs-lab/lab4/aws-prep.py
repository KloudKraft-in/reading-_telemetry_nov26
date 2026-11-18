#!/usr/bin/env python3
"""Prepares input files for the AWS part of Day 2 Lab 4."""

import json, os, random, time
from datetime import datetime

lines = open(os.path.expanduser("~/obs-lab/logs/shop.log")).read().splitlines()[-200:]

events = sorted(
    ({"timestamp": int(datetime.fromisoformat(json.loads(l)["ts"]).timestamp() * 1000), "message": l} for l in lines),
    key=lambda e: e["timestamp"]
)

json.dump(events, open("cw-events.json", "w"))

def hexid(n):
    return "%0*x" % (n, random.getrandbits(n * 4))

def trace(t0, fail):
    tid = "1-%08x-%s" % (int(t0), hexid(24))
    fe, ck, pay, sub_ck, sub_pay = (hexid(16) for _ in range(5))
    dur_pay = 3.0 if fail else 0.12
    end = t0 + 0.03 + dur_pay

    def seg(name, sid, parent, start, stop, status, subs=None, fault=False):
        s = {"name": name, "id": sid, "trace_id": tid, "start_time": start, "end_time": stop,
             "http": {"response": {"status": status}}}
        if parent:
            s["parent_id"] = parent
        if fault:
            s["fault"] = True
        if subs:
            s["subsegments"] = subs
        return json.dumps(s)

    remote = lambda name, sid, start, stop, fault: {
        "name": name, "id": sid, "start_time": start, "end_time": stop,
        "namespace": "remote", **({"fault": True} if fault else {})
    }

    return [
        seg("frontend", fe, None, t0, end + 0.01, 504 if fail else 201,
            [remote("checkout", sub_ck, t0 + 0.005, end, fail)], fail),
        seg("checkout", ck, sub_ck, t0 + 0.006, end, 504 if fail else 201,
            [remote("payment", sub_pay, t0 + 0.02, t0 + 0.02 + dur_pay, fail)], fail),
        seg("payment", pay, sub_pay, t0 + 0.021, t0 + 0.02 + dur_pay,
            504 if fail else 200, None, fail)
    ], tid

now = time.time() - 60
ok, tid_ok = trace(now, False)
bad, tid_bad = trace(now + 5, True)

json.dump({"TraceSegmentDocuments": ok + bad}, open("xray-input.json", "w"), indent=1)

print(f"cw-events.json: {len(events)} events | xray-input.json: 6 segments, traces {tid_ok} (ok) and {tid_bad} (failed)")
