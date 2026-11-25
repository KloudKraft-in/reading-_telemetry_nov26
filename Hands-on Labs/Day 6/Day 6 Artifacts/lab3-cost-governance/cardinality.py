#!/usr/bin/env python3
"""Day 6 Lab 3 - cardinality counter for data/series.txt.  python3 cardinality.py  -> distinct values per label and series per endpoint value."""
import os, re, collections
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
vals = collections.defaultdict(set); per = collections.Counter(); total = 0
for line in open(os.path.join(D, "series.txt")):
    if line.startswith("#") or "{" not in line: continue
    total += 1
    labels = dict(re.findall(r'(\w+)="([^"]*)"', line.split("{", 1)[1])); name = line.split("{")[0]
    for k, v in labels.items(): vals[k].add(v)
    per[labels.get("endpoint")] += 1
print("series in file:", total)
for k, v in sorted(vals.items(), key=lambda kv: -len(kv[1])): print("%-9s distinct values: %d" % (k, len(v)))
ex = next(iter(per)); print("series created by ONE endpoint value (%s): %d" % (ex, per[ex]))
