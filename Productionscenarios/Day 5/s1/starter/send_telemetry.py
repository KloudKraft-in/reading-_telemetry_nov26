#!/usr/bin/env python3
"""TEL-D5-501 — sends one hour of ShopNow telemetry (requests, dependencies, exceptions) to YOUR Application Insights resource.
Run in Azure Cloud Shell (Bash) — nothing to install:
  export APPLICATIONINSIGHTS_CONNECTION_STRING='InstrumentationKey=<key>;IngestionEndpoint=https://<region>.in.applicationinsights.azure.com/;...'
  python3 send_telemetry.py              # send
  python3 send_telemetry.py --dry-run    # only write telemetry.jsonl (no network, no key needed)
Fixed seed: every participant gets the same counts; only the clock times differ (the hour ends 10 minutes before you run it).
Story: the third-party fraud-check API (api.external-fraud.io) times out (HTTP 504) from minute 15 of the hour; every checkout calls it."""
import json, os, random, sys, urllib.error, urllib.request, uuid
from datetime import datetime, timedelta, timezone

random.seed(4242)
DRY = "--dry-run" in sys.argv
cs = dict(p.split("=", 1) for p in os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING", "").split(";") if "=" in p)
IKEY = cs.get("InstrumentationKey", "00000000-0000-0000-0000-000000000000")
ENDPOINT = cs.get("IngestionEndpoint", "https://dc.services.visualstudio.com/").rstrip("/") + "/v2/track"
if not DRY and "InstrumentationKey" not in cs:
    sys.exit("Set APPLICATIONINSIGHTS_CONNECTION_STRING first (Application Insights -> Overview -> Connection String).")

now = datetime.now(timezone.utc).replace(second=0, microsecond=0)
T0 = now - timedelta(minutes=70)                       # the hour is 70 ... 10 minutes ago
PFX = "Microsoft.ApplicationInsights." + IKEY.replace("-", "") + "."
FRAUD, PAY, SHIP, INV = "api.external-fraud.io", "api.paymentgw.example", "api.shiprates.example", "inventory-svc"
SQL, REDIS = "sql-shop.database.windows.net | shopdb", "redis-shop.cache:6380"
N_CHECKOUT, N_FRAUD_FAIL, N_PAY_FAIL, N_SHIP_FAIL = 500, 212, 3, 2      # 212 / 500 = 42.4 %

def hid(n): return "".join(random.choice("0123456789abcdef") for _ in range(n))
def iso(t): return t.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
def span(ms): return "%02d:%02d:%02d.%06d" % (ms // 3600000, ms // 60000 % 60, ms // 1000 % 60, int(ms * 1000) % 1000000)
def env(kind, t, base_type, data, op, parent=None, name=None):
    tags = {"ai.operation.id": op, "ai.cloud.role": "shop-api", "ai.cloud.roleInstance": "shop-api-1"}
    if parent: tags["ai.operation.parentId"] = parent
    if name: tags["ai.operation.name"] = name
    return {"ver": 1, "name": PFX + kind, "time": iso(t), "sampleRate": 100, "iKey": IKEY, "tags": tags,
            "data": {"baseType": base_type, "baseData": {"ver": 2, **data}}}

# request mix (1 500 requests, one every 2.4 s)
mix = ["GET /api/products"] * 600 + ["GET /api/products/{id}"] * 300 + ["POST /api/checkout"] * N_CHECKOUT + ["GET /health"] * 100
random.shuffle(mix)
co_idx = [i for i, n in enumerate(mix) if n == "POST /api/checkout"]
late = [i for i in co_idx if i >= len(mix) * 15 // 60]                      # fraud API fails only from minute 15
fraud_fail = set(random.sample(late, N_FRAUD_FAIL))
rest = [i for i in co_idx if i not in fraud_fail]
pay_fail, ship_fail = set(random.sample(rest, N_PAY_FAIL)), set(random.sample(rest, N_SHIP_FAIL))

items = []
for i, name in enumerate(mix):
    t = T0 + timedelta(seconds=2.4 * i)
    op, rid = uuid.UUID(int=random.getrandbits(128)).hex, hid(16)
    dur, code, ok = 0.0, 200, True
    def dep(dname, target, dtype, d, rc, success, off):
        items.append(env("RemoteDependency", t + timedelta(milliseconds=off), "RemoteDependencyData",
                         {"id": hid(16), "name": dname, "data": dname, "target": target, "type": dtype, "resultCode": rc,
                          "success": success, "duration": span(round(d, 1))}, op, rid, name))
    def exc(off, typ, msg, problem):
        items.append(env("Exception", t + timedelta(milliseconds=off), "ExceptionData",
                         {"exceptions": [{"typeName": typ, "message": msg, "hasFullStack": False}], "severityLevel": 3, "problemId": problem}, op, rid, name))
    if name == "GET /health":
        dur = random.uniform(1, 3)
    elif name == "GET /api/products":
        c = random.uniform(1, 4); dep("GET cache", REDIS, "Redis", c, "", True, 1)
        s = random.uniform(8, 30); dep("SELECT shopdb", SQL, "SQL", s, "0", True, 5)
        dur = c + s + random.uniform(5, 15)
    elif name == "GET /api/products/{id}":
        missing = random.random() < 0.12                 # unknown product id: expected 404, not an outage
        d = random.uniform(10, 25)
        dep("GET /inventory/items/{id}", INV, "HTTP", d, "404" if missing else "200", not missing, 2)
        dur = d + random.uniform(3, 8); code = 404 if missing else 200; ok = not missing
    else:  # checkout: fraud check -> payment -> shipping rates -> order insert
        if i in fraud_fail:
            p = random.uniform(10000, 10040)
            dep("POST /v1/score", FRAUD, "HTTP", p, "504", False, 4)
            code, ok, dur = 504, False, p + 12
            exc(p + 8, "System.Threading.Tasks.TaskCanceledException",
                f"The request to {FRAUD} was canceled: HttpClient.Timeout of 10 seconds elapsed (HTTP 504 Gateway Timeout)",
                "TaskCanceledException at FraudClient.Score")
        else:
            f = random.uniform(80, 220); dep("POST /v1/score", FRAUD, "HTTP", f, "200", True, 4)
            if i in pay_fail:
                p = random.uniform(300, 900); dep("POST /v1/charge", PAY, "HTTP", p, "503", False, int(f) + 6)
                code, ok, dur = 502, False, f + p + 15
                exc(f + p + 10, "Shop.Payments.PaymentGatewayException", f"{PAY} returned 503 Service Unavailable", "PaymentGatewayException at PaymentClient.Charge")
            else:
                p = random.uniform(150, 400); dep("POST /v1/charge", PAY, "HTTP", p, "201", True, int(f) + 6)
                sh = random.uniform(30, 90)
                dep("GET /v1/rates", SHIP, "HTTP", sh, "500" if i in ship_fail else "200", i not in ship_fail, int(f + p) + 8)   # handled: cached rate used
                s = random.uniform(10, 40); dep("INSERT shopdb", SQL, "SQL", s, "0", True, int(f + p + sh) + 10)
                code, dur = 201, f + p + sh + s + 20
    items.append(env("Request", t, "RequestData",
                     {"id": rid, "name": name, "duration": span(round(dur, 1)), "success": ok, "responseCode": str(code),
                      "url": "https://shop.example.com" + name.split()[1].replace("{id}", str(random.randint(1, 500)))}, op, None, name))

counts = {k: sum(1 for x in items if x["data"]["baseType"] == k) for k in ("RequestData", "RemoteDependencyData", "ExceptionData")}
print(f"telemetry: {counts['RequestData']} requests | {counts['RemoteDependencyData']} dependencies | {counts['ExceptionData']} exceptions")
print(f"hour of data: {iso(T0)} -> {iso(T0 + timedelta(hours=1))}")
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
print(f"accepted {sent} of {len(items)} items - it takes 2-5 minutes until they appear in Logs")
sys.exit(0 if sent == len(items) else 1)
