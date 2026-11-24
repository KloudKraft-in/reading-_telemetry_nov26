#!/usr/bin/env python3
"""Day 5 Lab 3 — sends one hour of shop telemetry (requests, dependencies, exceptions) to YOUR Application Insights resource.
Usage (Azure Cloud Shell, Bash):
  export APPLICATIONINSIGHTS_CONNECTION_STRING='InstrumentationKey=<key>;IngestionEndpoint=https://<region>.in.applicationinsights.azure.com/;...'
  python3 appinsights-gen.py            # send    |    python3 appinsights-gen.py --dry-run   # only write telemetry.jsonl
Fixed seed 5150: every learner gets the same 1 800 requests; only the clock times differ (the hour ends 10 minutes before you run it).
Story: the external payment provider (psp.example.com) returns 503 / times out from minute 20 to minute 35 of the hour;
inventory-svc returns 404 for unknown products all hour (expected, not an outage); a few SQL deadlocks."""
import json, os, random, sys, urllib.request, uuid
from datetime import datetime, timedelta, timezone

random.seed(5150)
DRY = "--dry-run" in sys.argv
cs = dict(p.split("=", 1) for p in os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING", "").split(";") if "=" in p)
IKEY = cs.get("InstrumentationKey", "00000000-0000-0000-0000-000000000000")
ENDPOINT = cs.get("IngestionEndpoint", "https://dc.services.visualstudio.com/").rstrip("/") + "/v2/track"
if not DRY and "InstrumentationKey" not in cs:
    sys.exit("Set APPLICATIONINSIGHTS_CONNECTION_STRING first (Application Insights → Overview → Connection String).")

now = datetime.now(timezone.utc).replace(second=0, microsecond=0)
T0 = now - timedelta(minutes=70)                       # the hour is 70 … 10 minutes ago
INC0, INC1 = T0 + timedelta(minutes=20), T0 + timedelta(minutes=35)
PFX = "Microsoft.ApplicationInsights." + IKEY.replace("-", "") + "."

def hid(n): return "".join(random.choice("0123456789abcdef") for _ in range(n))
def iso(t): return t.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
def span(ms): return "%02d:%02d:%02d.%06d" % (ms // 3600000, ms // 60000 % 60, ms // 1000 % 60, int(ms * 1000) % 1000000)
def env(kind, t, base_type, data, op, parent=None, name=None):
    tags = {"ai.operation.id": op, "ai.cloud.role": "shop-api", "ai.cloud.roleInstance": "shop-api-1"}
    if parent: tags["ai.operation.parentId"] = parent
    if name: tags["ai.operation.name"] = name
    return {"ver": 1, "name": PFX + kind, "time": iso(t), "sampleRate": 100, "iKey": IKEY, "tags": tags,
            "data": {"baseType": base_type, "baseData": {"ver": 2, **data}}}

REQ = [("GET /api/products", 0.40), ("GET /api/products/{id}", 0.20), ("GET /api/cart", 0.15), ("POST /api/checkout", 0.20), ("GET /health", 0.05)]
items = []
for i in range(1800):
    t = T0 + timedelta(seconds=2 * i)
    name = random.choices([r[0] for r in REQ], [r[1] for r in REQ])[0]
    op, rid = uuid.UUID(int=random.getrandbits(128)).hex, hid(16)
    dur, code, ok = 0.0, 200, True
    def dep(dname, target, dtype, d, rc, success, off):
        items.append(env("RemoteDependency", t + timedelta(milliseconds=off), "RemoteDependencyData",
                         {"id": hid(16), "name": dname, "data": dname, "target": target, "type": dtype, "resultCode": rc,
                          "success": success, "duration": span(round(d, 1))}, op, rid, name))
    if name == "GET /health":
        dur = random.uniform(1, 3)
    elif name in ("GET /api/products", "GET /api/cart"):
        c = random.uniform(1, 4); dep("GET cache", "redis-shop.cache:6380", "Redis", c, "", True, 1)
        s = random.uniform(8, 30); dep("SELECT shopdb", "sql-shop.database.windows.net | shopdb", "SQL", s, "0", True, 5)
        dur = c + s + random.uniform(5, 15)
    elif name == "GET /api/products/{id}":
        missing = random.random() < 0.12
        d = random.uniform(10, 25)
        dep("GET /inventory/items/{id}", "inventory-svc", "HTTP", d, "404" if missing else "200", not missing, 2)
        dur = d + random.uniform(3, 8); code = 404 if missing else 200; ok = not missing
    else:  # checkout
        s = random.uniform(10, 40)
        deadlock = random.random() < 0.01
        dep("INSERT shopdb", "sql-shop.database.windows.net | shopdb", "SQL", s, "1205" if deadlock else "0", not deadlock, 3)
        if deadlock:
            code, ok, dur = 500, False, s + 20
            items.append(env("Exception", t + timedelta(milliseconds=s + 10), "ExceptionData",
                             {"exceptions": [{"typeName": "System.Data.SqlClient.SqlException", "message": "Transaction (Process ID 63) was deadlocked on lock resources", "hasFullStack": False}],
                              "severityLevel": 3, "problemId": "System.Data.SqlClient.SqlException at OrderRepository.Insert"}, op, rid, name))
        else:
            incident = INC0 <= t < INC1
            if incident and random.random() < 0.55:
                timeout = random.random() < 0.5
                p = 5000.0 if timeout else random.uniform(200, 900)
                dep("POST /v2/charges", "psp.example.com", "HTTP", p, "" if timeout else "503", False, int(s) + 5)
                code, ok, dur = 502, False, s + p + 15
                et = "Shop.Payments.PaymentTimeoutException" if timeout else "Shop.Payments.PaymentProviderException"
                msg = "PSP call timed out after 5000 ms" if timeout else "PSP returned 503 Service Unavailable"
                items.append(env("Exception", t + timedelta(milliseconds=dur - 5), "ExceptionData",
                                 {"exceptions": [{"typeName": et, "message": msg, "hasFullStack": False}], "severityLevel": 3,
                                  "problemId": et + " at PaymentClient.Charge"}, op, rid, name))
            else:
                p = random.uniform(1200, 2500) if incident else random.uniform(150, 400)
                dep("POST /v2/charges", "psp.example.com", "HTTP", p, "201", True, int(s) + 5)
                code, dur = 201, s + p + 15
    items.append(env("Request", t, "RequestData",
                     {"id": rid, "name": name, "duration": span(round(dur, 1)), "success": ok, "responseCode": str(code),
                      "url": "https://shop.example.com" + name.split()[1].replace("{id}", str(random.randint(1, 500)))}, op, None, name))

counts = {k: sum(1 for x in items if x["data"]["baseType"] == k) for k in ("RequestData", "RemoteDependencyData", "ExceptionData")}
print(f"telemetry: {counts['RequestData']} requests | {counts['RemoteDependencyData']} dependencies | {counts['ExceptionData']} exceptions")
print(f"hour of data: {iso(T0)} → {iso(T0 + timedelta(hours=1))}   incident window (for your answers): {iso(INC0)} → {iso(INC1)}")
if DRY:
    with open("telemetry.jsonl", "w") as f:
        for x in items: f.write(json.dumps(x) + "\n")
    print("dry run: telemetry.jsonl written, nothing sent"); sys.exit(0)

sent = 0
for i in range(0, len(items), 500):
    batch = items[i:i + 500]
    req = urllib.request.Request(ENDPOINT, json.dumps(batch).encode(), {"Content-Type": "application/json"})
    try:
        r = json.load(urllib.request.urlopen(req, timeout=60))
    except urllib.error.HTTPError as e:
        r = json.loads(e.read() or b"{}") or {"itemsAccepted": 0, "errors": [{"message": f"HTTP {e.code}"}]}
    sent += r.get("itemsAccepted", 0)
    if r.get("errors"): print("  errors:", r["errors"][:2])
print(f"accepted {sent} of {len(items)} items — it takes 2-5 minutes until they appear in Logs")
sys.exit(0 if sent == len(items) else 1)
