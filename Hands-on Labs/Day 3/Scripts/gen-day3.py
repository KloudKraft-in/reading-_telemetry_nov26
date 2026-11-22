#!/usr/bin/env python3
"""Day 3 Splunk dataset — INC-9120 (22 Oct 2026, 10:00-11:00 IST), seed 9120.
  web.log      nginx (access_combined + rt= upstream= req_id=), hosts web-01, web-02     -> index d3_web
  app.json     JSON request START/END events and app messages, hosts app-01..03       -> index d3_app (_json)
  db.log       PostgreSQL log, host db-01                                              -> index d3_db
  syslog.log   Linux syslog of app-01..03 and db-01                                    -> index d3_infra (syslog)
  host_inventory.csv / service_owners.csv  lookup files
Story: app-02 leaks memory (GC pauses from 10:24), is OOM-killed at 10:30:58 and only restarts at 10:37:20.
       Requests the load balancer sends to app-02 are slow (10:24-10:30) and then fail with 502 (10:31-10:37).
       Red herring: slow queries on db-01 at 10:10-10:12."""
import csv, json, random
from datetime import datetime, timedelta, timezone

random.seed(9120)
IST = timezone(timedelta(hours=5, minutes=30))
T0 = datetime(2026, 10, 22, 10, 0, tzinfo=IST)
SLOW, DOWN, UP = T0 + timedelta(minutes=24), T0 + timedelta(minutes=30, seconds=58), T0 + timedelta(minutes=37, seconds=20)
IPS = ["203.0.113.%d" % i for i in range(10, 60)]
PATHS = [("GET", "/api/products", 0.45), ("GET", "/api/cart", 0.25), ("POST", "/api/orders", 0.20), ("GET", "/api/products/missing", 0.02), ("GET", "/health", 0.08)]
web, app, db, sysl = [], [], [], []

def ngx(t): return t.strftime("%d/%b/%Y:%H:%M:%S +0530")
def iso(t): return t.isoformat(timespec="milliseconds")
def sl(t): return t.isoformat(timespec="seconds")        # rsyslog file format with offset

for i in range(2400):                                  # one request every 1.5 s
    t = T0 + timedelta(seconds=i * 1.5)
    method, path, _ = random.choices(PATHS, [p[2] for p in PATHS])[0]
    upstream = f"app-0{i % 3 + 1}"
    whost = "web-01" if random.random() < 0.5 else "web-02"
    rid = f"r-{100000 + i}"
    if path == "/api/products/missing":
        status, dur = 404, random.uniform(0.004, 0.012)
    else:
        status = 201 if method == "POST" else 200
        dur = {"/api/products": random.uniform(0.03, 0.09), "/api/cart": random.uniform(0.02, 0.06),
               "/api/orders": random.uniform(0.15, 0.35), "/health": random.uniform(0.001, 0.003)}[path]
    reached_app = True
    if upstream == "app-02" and SLOW <= t < DOWN and path != "/health":
        dur += random.uniform(0.8, 2.4)                # GC pauses
    if upstream == "app-02" and DOWN <= t < UP:
        status, dur, reached_app = 502, random.uniform(0.001, 0.003), False
    size = random.randint(300, 4000) if status < 400 else random.randint(150, 600)
    web.append((t, f'{random.choice(IPS)} - - [{ngx(t)}] "{method} {path} HTTP/1.1" {status} {size} "-" "shop-mobile/5.2" '
                   f'rt={dur:.3f} upstream={upstream}:8080 req_id={rid}', whost))
    if reached_app:
        app_dur = max(1, int((dur - 0.002) * 1000))
        app.append((t, {"ts": iso(t), "level": "INFO", "service": "shop-api", "msg": "START", "req_id": rid, "path": path}, upstream))
        app.append((t + timedelta(milliseconds=app_dur), {"ts": iso(t + timedelta(milliseconds=app_dur)), "level": "INFO", "service": "shop-api",
                    "msg": "END", "req_id": rid, "path": path, "status": status, "duration_ms": app_dur}, upstream))

t = SLOW
while t < DOWN:                                        # GC warnings on app-02
    heap = min(99, 88 + int((t - SLOW).total_seconds() // 60))
    app.append((t, {"ts": iso(t), "level": "WARN", "service": "shop-api", "msg": f"GC overhead high: pause {random.randint(900, 2400)} ms, heap {heap}%"}, "app-02"))
    t += timedelta(seconds=30)
app.append((DOWN - timedelta(seconds=2), {"ts": iso(DOWN - timedelta(seconds=2)), "level": "ERROR", "service": "shop-api",
            "msg": "java.lang.OutOfMemoryError: Java heap space", "exception": "java.lang.OutOfMemoryError"}, "app-02"))
app.append((UP + timedelta(seconds=40), {"ts": iso(UP + timedelta(seconds=40)), "level": "INFO", "service": "shop-api",
            "msg": "Application started in 39.8 s"}, "app-02"))
for m in range(0, 60, 15):                             # routine payment declines (business errors, not an outage)
    tt = T0 + timedelta(minutes=m, seconds=7)
    app.append((tt, {"ts": iso(tt), "level": "ERROR", "service": "shop-api", "msg": "Payment declined by issuer (code 05)",
                     "exception": "com.shop.PaymentDeclinedException"}, f"app-0{m // 15 % 3 + 1}"))

def utc(t): return t.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + " UTC"
for m in range(0, 60, 5):
    tt = T0 + timedelta(minutes=m)
    db.append((tt, f"{utc(tt)} [811] LOG:  checkpoint complete: wrote {random.randint(200, 900)} buffers"))
for k in range(6):
    tt = T0 + timedelta(minutes=10, seconds=10 + k * 20)
    db.append((tt, f"{utc(tt)} [4410] report_user@shopdb LOG:  duration: {random.uniform(1800, 2600):.1f} ms  statement: SELECT * FROM orders WHERE created_at > now() - interval '90 days'"))

for h in ["app-01", "app-02", "app-03", "db-01"]:
    for m in range(0, 60, 5):
        tt = T0 + timedelta(minutes=m, seconds=1)
        sysl.append((tt, f"{sl(tt)} {h} CRON[{random.randint(2000, 9000)}]: (root) CMD (/usr/lib/sysstat/sa1 1 1)", h))
oom = [(DOWN, "kernel: [884213.442] Out of memory: Killed process 2211 (java) total-vm:6120344kB, anon-rss:3981220kB"),
       (DOWN + timedelta(seconds=1), "systemd[1]: shop-api.service: Main process exited, code=killed, status=9/KILL"),
       (DOWN + timedelta(seconds=1), "systemd[1]: shop-api.service: Failed with result 'oom-kill'."),
       (DOWN + timedelta(seconds=6), "systemd[1]: shop-api.service: Scheduled restart job, restart counter is at 1."),
       (DOWN + timedelta(seconds=6), "systemd[1]: shop-api.service: Start request repeated too quickly."),
       (UP - timedelta(seconds=5), "systemd[1]: Starting shop-api.service - Shop API..."),
       (UP, "systemd[1]: Started shop-api.service - Shop API.")]
for tt, msg in oom: sysl.append((tt, f"{sl(tt)} app-02 {msg}", "app-02"))

def by_host(rows, name, fmt):
    for h in sorted({r[-1] for r in rows}):
        with open(f"{name}-{h}.log" if name != "app" else f"app-{h}.json", "w") as f:
            for r in sorted((r for r in rows if r[-1] == h), key=lambda r: r[0]): f.write(fmt(r) + "\n")
by_host(web, "web", lambda r: r[1])
by_host(app, "app", lambda r: json.dumps(r[1]))
by_host(sysl, "syslog", lambda r: r[1])
with open("db-db-01.log", "w") as f:
    for r in sorted(db, key=lambda r: r[0]): f.write(r[1] + "\n")
with open("host_inventory.csv", "w", newline="") as f:
    csv.writer(f).writerows([["host", "role", "datacenter", "service"], ["web-01", "web", "dc1", "shop-web"], ["web-02", "web", "dc2", "shop-web"],
                             ["app-01", "app", "dc1", "shop-api"], ["app-02", "app", "dc2", "shop-api"], ["app-03", "app", "dc1", "shop-api"],
                             ["db-01", "database", "dc1", "postgres"]])
with open("service_owners.csv", "w", newline="") as f:
    csv.writer(f).writerows([["service", "team", "tier", "oncall"], ["shop-web", "web-platform", "1", "web-oncall"],
                             ["shop-api", "commerce", "1", "commerce-oncall"], ["postgres", "dba", "1", "dba-oncall"]])
# Simplified ITSI-style KPI snapshot (5-minute buckets) — computed from the same events
SCORE = {"normal": 100, "medium": 70, "high": 40, "critical": 10}
def sev(v, med, high, crit, lower_is_bad=False):
    if lower_is_bad: return "critical" if v < crit else "high" if v < high else "medium" if v < med else "normal"
    return "critical" if v >= crit else "high" if v >= high else "medium" if v >= med else "normal"
def health_sev(h): return "normal" if h >= 90 else "medium" if h >= 70 else "high" if h >= 40 else "critical"
kpis, health = [], []
for b in range(12):
    s0, s1 = T0 + timedelta(minutes=5 * b), T0 + timedelta(minutes=5 * b + 5)
    lab = s0.strftime("%H:%M")
    reqs = [(t, line) for t, line, h in web if s0 <= t < s1]
    codes = [int(line.split('"')[2].split()[0]) for t, line in reqs]
    rts = sorted(float(line.split("rt=")[1].split()[0]) for t, line in reqs)
    err = round(100 * sum(c >= 500 for c in codes) / len(codes), 1)
    p95 = round(rts[int(0.95 * (len(rts) - 1))], 3)
    down = DOWN < s1 and UP > s0
    avail = round(100 * (2 if down else 3) / 3, 1)
    gc = sum(1 for t, e, h in app if s0 <= t < s1 and e["level"] == "WARN")
    slowq = sum(1 for t, line in db if s0 <= t < s1 and "duration:" in line)
    rows = [("Shop Web", "5xx error rate", err, "%", sev(err, 1, 5, 10), 11), ("Shop Web", "p95 response time", p95, "s", sev(p95, 0.5, 1, 2), 8),
            ("Shop API", "Instances available", avail, "%", sev(avail, 100, 90, 70, True), 10), ("Shop API", "GC pause warnings", gc, "count", sev(gc, 1, 5, 10), 5),
            ("Database", "Slow queries", slowq, "count", sev(slowq, 1, 5, 10), 6)]
    kpis += [(lab, *r) for r in rows]
    svc_h = {}
    for svc in ("Shop Web", "Shop API", "Database"):
        rr = [r for r in rows if r[0] == svc]
        svc_h[svc] = round(sum(SCORE[r[4]] * r[5] for r in rr) / sum(r[5] for r in rr))
    svc_h["Online Shop"] = min(svc_h.values())
    health += [(lab, svc, h, health_sev(h)) for svc, h in svc_h.items()]
with open("itsi_kpis.csv", "w", newline="") as f:
    csv.writer(f).writerows([["time", "service", "kpi", "value", "unit", "severity", "importance"]] + kpis)
with open("itsi_health.csv", "w", newline="") as f:
    csv.writer(f).writerows([["time", "service", "health_score", "severity"]] + health)
print(f"web {len(web)} | app {len(app)} | db {len(db)} | syslog {len(sysl)} events; files per host written")
