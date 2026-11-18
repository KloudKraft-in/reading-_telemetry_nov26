#!/usr/bin/env python3

"""Creates 3 hours of 'production' shop metrics (env="prod") ending NOW, in OpenMetrics format,
for backfilling into Prometheus with: promtool tsdb create-blocks-from openmetrics history.om <data dir>
Timeline (minutes before the end):  -150..-120 marketing campaign (double traffic, healthy)
                                     -75..-55   incident (DB connection pool exhausted)"""

import math, time

STEP, MINUTES = 30, 180

end = int(time.time()) // 60 * 60

start = end - MINUTES * 60

LE = [0.05, 0.1, 0.25, 0.5, 1, 2.5, 5]

ROUTES = {"/api/products": ("GET", 6.0), "/api/cart": ("GET", 3.0), "/api/checkout": ("POST", 1.5)}

# cumulative share of requests at or below each bucket bound, and mean duration (s)
LAT = {("/api/products", "ok"): ([.55, .95, 1, 1, 1, 1, 1], 0.055), ("/api/products", "inc"): ([.30, .45, .50, .55, .70, 1, 1], 0.62),
       ("/api/cart", "ok"): ([.80, .98, 1, 1, 1, 1, 1], 0.035),     ("/api/cart", "inc"): ([.80, .98, 1, 1, 1, 1, 1], 0.035),
       ("/api/checkout", "ok"): ([0, .05, .90, .99, 1, 1, 1], 0.21), ("/api/checkout", "inc"): ([0, 0, .20, .30, .40, .97, 1], 1.35)}

def phase(m):            # m = minutes before end (positive)
    if 120 < m <= 150: return "surge"
    if 55 < m <= 75: return "inc"
    return "ok"

series = {}              # (family, labels) -> list of (ts, value)
cum = {}

def add(family, labels, ts, value, counter=False):
    key = (family, labels)
    if counter:
        cum[key] = cum.get(key, 0) + value; value = cum[key]
    series.setdefault(key, []).append((ts, round(value, 6)))

for i in range(MINUTES * 60 // STEP + 1):
    ts = start + i * STEP
    m = (end - ts) / 60
    ph = phase(m)
    wave = 1 + 0.08 * math.sin(i / 9)
    for route, (method, rps) in ROUTES.items():
        n = rps * STEP * wave * (2 if ph == "surge" else 1)
        err = 0.30 if (ph == "inc" and route == "/api/checkout") else 0
        e4 = 0.03 if route == "/api/cart" else 0
        ok_status = "201" if method == "POST" else "200"
        add("http_server_requests_total", f'service="frontend",route="{route}",method="{method}",status="{ok_status}"', ts, round(n * (1 - err - e4)), True)
        add("http_server_requests_total", f'service="frontend",route="{route}",method="{method}",status="503"', ts, round(n * err), True)
        if e4: add("http_server_requests_total", f'service="frontend",route="{route}",method="{method}",status="401"', ts, round(n * e4), True)
        shares, mean = LAT[(route, "inc" if ph == "inc" else "ok")]
        cnt = round(n)
        for le, sh in zip(LE, shares):
            add("http_server_request_duration_seconds_bucket", f'service="frontend",route="{route}",le="{le}"', ts, round(cnt * sh), True)
        add("http_server_request_duration_seconds_bucket", f'service="frontend",route="{route}",le="+Inf"', ts, cnt, True)
        add("http_server_request_duration_seconds_sum", f'service="frontend",route="{route}"', ts, cnt * mean, True)
        add("http_server_request_duration_seconds_count", f'service="frontend",route="{route}"', ts, cnt, True)
    add("db_pool_connections_max", 'service="inventory"', ts, 10)
    add("db_pool_connections_active", 'service="inventory"', ts, 10 if ph == "inc" else (6 if ph == "surge" else 3))
    add("db_pool_pending_threads", 'service="inventory"', ts, 30 if ph == "inc" else 0)
    for svc, base in (("frontend", .22), ("checkout", .30), ("inventory", .18), ("payment", .12)):
        u = base * (1.8 if ph == "surge" else 1) + (0.5 if ph == "inc" and svc == "inventory" else 0)
        add("process_cpu_utilization_ratio", f'service="{svc}"', ts, min(u, 0.97))

COMMON = 'env="prod",job="shop-history",instance="prod-replay"'
with open("history.om", "w") as f:
    for family in dict.fromkeys(k[0] for k in series):
        for (fam, labels), points in series.items():
            if fam != family: continue
            for ts, v in points:
                f.write(f"{fam}{{{COMMON},{labels}}} {v} {ts}\n")
    f.write("# EOF\n")

print(f"history.om: {len(series)} series x {MINUTES * 60 // STEP + 1} points, "
      f"{time.strftime('%H:%M', time.localtime(start))} -> {time.strftime('%H:%M', time.localtime(end))} (local time)")
