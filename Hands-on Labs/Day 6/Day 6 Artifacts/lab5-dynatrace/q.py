#!/usr/bin/env python3
"""Tiny query helper for the Day 6 incident bundle in ./data  (stdlib only).
  python3 q.py events
  python3 q.py metrics [--service checkout] [--from 10:00] [--to 10:30]
  python3 q.py logs [--service S] [--level ERROR] [--contains TEXT] [--from HH:MM] [--to HH:MM] [--count] [--limit 20]
  python3 q.py trace <trace_id>
  python3 q.py traces                (list trace ids in traces.json)"""
import argparse, csv, json, os, sys
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
def main():
    p = argparse.ArgumentParser(); p.add_argument("cmd"); p.add_argument("arg", nargs="?")
    for a in ("service", "level", "contains", "from", "to"): p.add_argument("--" + a)
    p.add_argument("--count", action="store_true"); p.add_argument("--limit", type=int, default=20)
    a = p.parse_args(); fr, to = getattr(a, "from"), a.to
    inr = lambda t: (not fr or t[:5] >= fr) and (not to or t[:5] <= to)
    if a.cmd == "events":
        print(open(os.path.join(D, "events.log")).read(), end="")
    elif a.cmd == "metrics":
        print("minute service requests error_pct p95_ms db_pool_used_pct errors")
        for r in csv.DictReader(open(os.path.join(D, "metrics.csv"))):
            if (not a.service or r["service"] == a.service) and inr(r["minute"]):
                print(r["minute"], r["service"].ljust(9), r["requests"].rjust(4), r["error_pct"].rjust(6), r["p95_ms"].rjust(5), r["db_pool_used_pct"].rjust(4), r["errors"].rjust(4))
    elif a.cmd == "logs":
        rows = [r for r in map(json.loads, open(os.path.join(D, "logs.jsonl")))
                if (not a.service or r["service"] == a.service) and (not a.level or r["level"] == a.level.upper())
                and (not a.contains or a.contains.lower() in r["message"].lower()) and inr(r["ts"])]
        if a.count: print(len(rows))
        else:
            for r in rows[:a.limit]: print(r["ts"], r["service"], r["level"], r["trace_id"], r["message"])
            if len(rows) > a.limit: print("... %d more (use --count or --limit)" % (len(rows) - a.limit))
    elif a.cmd == "traces":
        for t in json.load(open(os.path.join(D, "traces.json"))): print(t["trace_id"])
    elif a.cmd == "trace":
        for t in json.load(open(os.path.join(D, "traces.json"))):
            if t["trace_id"] == a.arg:
                for s in t["spans"]: print("%-9s %-20s %5d ms  %s" % (s["service"], s["operation"], s["duration_ms"], s["status"]))
                return
        print("trace not found (only the sampled traces are stored: python3 q.py traces)"); sys.exit(1)
    else: p.error("unknown command")
main()
