#!/usr/bin/env python3
"""Day 6 Lab 3 - head vs tail sampling simulator over data/traces-sample.csv.
  python3 sample_sim.py            (head 10 % and tail: keep errors + slow + 10 % of the rest)"""
import csv, os, random
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
def run(path=None):
    rows = list(csv.DictReader(open(path or os.path.join(D, "traces-sample.csv"))))
    n = len(rows); E = sum(int(r["has_error"]) for r in rows); S = sum(int(r["slow_over_1s"]) for r in rows)
    rh = random.Random(1); rt = random.Random(2)
    head = [r for r in rows if rh.random() < 0.10]
    tail = [r for r in rows if int(r["has_error"]) or int(r["slow_over_1s"]) or rt.random() < 0.10]
    return dict(n=n, errors=E, slow=S, head_kept=len(head), head_err=sum(int(r["has_error"]) for r in head), head_slow=sum(int(r["slow_over_1s"]) for r in head),
                tail_kept=len(tail), tail_err=sum(int(r["has_error"]) for r in tail), tail_slow=sum(int(r["slow_over_1s"]) for r in tail))
if __name__ == "__main__":
    r = run()
    print("traces %d | errors %d | slow %d" % (r["n"], r["errors"], r["slow"]))
    print("HEAD 10%%  kept %d (%.1f%%)  errors kept %d of %d  slow kept %d of %d" % (r["head_kept"], 100 * r["head_kept"] / r["n"], r["head_err"], r["errors"], r["head_slow"], r["slow"]))
    print("TAIL      kept %d (%.1f%%)  errors kept %d of %d  slow kept %d of %d" % (r["tail_kept"], 100 * r["tail_kept"] / r["n"], r["tail_err"], r["errors"], r["tail_slow"], r["slow"]))
