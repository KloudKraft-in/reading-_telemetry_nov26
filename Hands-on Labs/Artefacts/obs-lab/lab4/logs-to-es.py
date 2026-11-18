#!/usr/bin/env python3

import json
import os
import sys
import urllib.request
from datetime import datetime, timedelta, timezone

minutes = int(sys.argv[1]) if len(sys.argv) > 1 else 15
since = datetime.now(timezone.utc) - timedelta(minutes=minutes)

docs = []

with open(os.path.expanduser("~/obs-lab/logs/shop.log")) as f:
    for line in f:
        e = json.loads(line)
        timestamp = datetime.fromisoformat(e["ts"])

        if timestamp < since:
            continue

        d = {
            "@timestamp": e["ts"],
            "log": {"level": e["level"]},
            "service": {"name": e["service"]},
            "trace": {"id": e["trace_id"]},
            "span": {"id": e["span_id"]},
            "message": e["message"]
        }

        if "http_status" in e:
            d["http"] = {"response": {"status_code": e["http_status"]}}

        if "exception" in e:
            d["error"] = {"type": e["exception"]}

        docs.append(d)

levels = {}
for d in docs:
    level = d["log"]["level"]
    levels[level] = levels.get(level, 0) + 1

print(f"{len(docs)} log events from the last {minutes} min: {levels}")

if not docs:
    sys.exit("No recent logs found. Generate fresh ShopSim traffic and retry.")

body = "".join(
    json.dumps({"index": {"_index": "shop-logs"}}) + "\n"
    + json.dumps(d) + "\n"
    for d in docs
)

req = urllib.request.Request(
    "http://localhost:9200/_bulk?refresh=true",
    body.encode(),
    method="POST",
    headers={"Content-Type": "application/x-ndjson"}
)

with urllib.request.urlopen(req) as response:
    result = json.load(response)

print(f"errors={result['errors']} items={len(result['items'])}")
