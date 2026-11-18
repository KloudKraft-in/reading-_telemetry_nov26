#!/usr/bin/env python3
"""INC-7301 dataset for Observability Day 1 Lab 1 - one incident seen through all four MELT signals.
Writes: metrics.csv (per minute & service), events.jsonl, logs.jsonl, traces.json (OTLP/JSON, 2 traces)."""
import csv, json, random
from datetime import datetime, timedelta, timezone


random.seed(7301)
IST = timezone(timedelta(hours=5, minutes=30))
T0 = datetime(2026, 10, 23, 10, 0, tzinfo=IST)
CHANGE, ROLLBACK = T0 + timedelta(minutes=12), T0 + timedelta(minutes=27)
def iso(t): return t.isoformat(timespec="milliseconds")
def hexid(n): return "".join(random.choice("0123456789abcdef") for _ in range(n))
def p95(xs): xs = sorted(xs); return round(xs[int(0.95 * (len(xs) - 1))]) if xs else 0


rows, logs, sample = [], [], {}
for minute in range(35):
    m0 = T0 + timedelta(minutes=minute)
    timeout = 800 if CHANGE <= m0 < ROLLBACK else 5000
    stats = {s: {"req": 0, "err": 0, "lat": []} for s in ("frontend", "checkout", "payment", "inventory")}
    for i in range(120):
        t = m0 + timedelta(seconds=i * 0.5)
        route = ("/api/products", "/api/cart", "/api/checkout")[i % 4 if i % 4 < 3 else 0]
        tid = hexid(32)
        if route != "/api/checkout":
            inv = random.uniform(8, 40)
            lat = inv + random.uniform(5, 20)
            stats["inventory"]["req"] += 1; stats["inventory"]["lat"].append(inv)
            stats["frontend"]["req"] += 1; stats["frontend"]["lat"].append(lat)
            continue
        psp = min(300 + random.expovariate(1 / 250), 3000)
        failed = psp > timeout
        pay = timeout if failed else psp
        inv = random.uniform(10, 40)
        chk = inv + pay + random.uniform(10, 30)
        for s, v in (("inventory", inv), ("payment", pay), ("checkout", chk), ("frontend", chk + 6)):
            stats[s]["req"] += 1; stats[s]["lat"].append(v)
            if failed and s != "inventory": stats[s]["err"] += 1
        if failed:
            pay_span = hexid(16)
            logs.append({"ts": iso(t + timedelta(milliseconds=inv + pay + 15)), "level": "ERROR", "service": "payment", "trace_id": tid, "span_id": pay_span,
                         "message": f"PSP call timed out after {timeout} ms (psp=acme-pay)", "exception": "java.net.SocketTimeoutException"})
            logs.append({"ts": iso(t + timedelta(milliseconds=chk)), "level": "ERROR", "service": "checkout", "trace_id": tid, "span_id": hexid(16),
                         "message": "Checkout failed: payment timeout", "http_status": 504})
            sample.setdefault("failed", (t, tid, inv, pay, chk, timeout))
        else:
            logs.append({"ts": iso(t + timedelta(milliseconds=chk)), "level": "INFO", "service": "checkout", "trace_id": tid, "span_id": hexid(16),
                         "message": f"Checkout completed in {round(chk)} ms"})
            if minute == 5: sample.setdefault("ok", (t, tid, inv, pay, chk, timeout))
    for s, st in stats.items():
        cpu = {"frontend": 31, "checkout": 38, "payment": 22, "inventory": 27}[s] + random.randint(-3, 3)
        rows.append([m0.strftime("%H:%M"), s, st["req"], st["err"], p95(st["lat"]), cpu])


with open("metrics.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["minute", "service", "requests", "errors_5xx", "p95_ms", "cpu_pct"]); w.writerows(rows)
events = [
    (T0 - timedelta(minutes=5), "deployment", "inventory-service", "Deployed inventory-service v3.2.0 (CHG-2228)", "info"),
    (CHANGE, "config-change", "payment-service", "psp.client.timeout_ms changed 5000 -> 800 (CHG-2231 'fail fast on slow PSP')", "info"),
    (T0 + timedelta(minutes=14, seconds=30), "alert-opened", "frontend", "ALERT CheckoutErrorRate > 3% for 2m (severity=critical)", "critical"),
    (T0 + timedelta(minutes=18), "autoscaling", "frontend", "HPA scaled frontend 3 -> 5 pods (cpu target 30%)", "info"),
    (ROLLBACK, "config-change", "payment-service", "psp.client.timeout_ms changed 800 -> 5000 (rollback of CHG-2231, INC-7301)", "info"),
    (T0 + timedelta(minutes=30), "alert-resolved", "frontend", "RESOLVED CheckoutErrorRate", "info"),
]
with open("events.jsonl", "w") as f:
    for t, kind, svc, msg, sev in events:
        f.write(json.dumps({"ts": iso(t), "type": kind, "service": svc, "severity": sev, "message": msg}) + "\n")
logs.sort(key=lambda r: r["ts"])
with open("logs.jsonl", "w") as f:
    for r in logs: f.write(json.dumps(r) + "\n")


def trace(t, tid, inv, pay, chk, timeout, failed):
    ns = lambda x: str(int((t + timedelta(milliseconds=x)).timestamp() * 1e9))
    fe, ck, iv, py, db = (hexid(16) for _ in range(5))
    def sp(sid, parent, name, a, b, err=None, kind=2):
        s = {"traceId": tid, "spanId": sid, "name": name, "kind": kind, "startTimeUnixNano": ns(a), "endTimeUnixNano": ns(b),
             "status": {"code": 2, "message": err} if err else {"code": 1}}
        if parent: s["parentSpanId"] = parent
        return s
    err = f"PSP call timed out after {timeout} ms" if failed else None
    res = lambda svc, spans: {"resource": {"attributes": [{"key": "service.name", "value": {"stringValue": svc}}]}, "scopeSpans": [{"scope": {"name": "inc-7301"}, "spans": spans}]}
    return [res("frontend", [sp(fe, None, "POST /api/checkout", 0, chk + 6, "HTTP 504" if failed else None)]),
            res("checkout", [sp(ck, fe, "POST /checkout", 3, chk + 3, "payment timeout" if failed else None)]),
            res("inventory", [sp(iv, ck, "POST /inventory/reserve", 5, 5 + inv), sp(db, iv, "UPDATE stock", 7, 3 + inv, kind=3)]),
            res("payment", [sp(py, ck, "POST psp.acme-pay.com/v2/charge", 10 + inv, 10 + inv + pay, err, kind=3)])]
with open("traces.json", "w") as f:
    json.dump({"resourceSpans": trace(*sample["failed"], True) + trace(*sample["ok"], False)}, f, indent=1)
print(f"metrics.csv {len(rows)} rows | events.jsonl {len(events)} | logs.jsonl {len(logs)} | traces.json 2 traces "
      f"(failed {sample['failed'][1]}, ok {sample['ok'][1]})")
