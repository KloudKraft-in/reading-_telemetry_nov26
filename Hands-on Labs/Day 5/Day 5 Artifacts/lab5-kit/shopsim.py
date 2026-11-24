#!/usr/bin/env python3
"""ShopSim - a small simulated online shop that produces all four MELT signals.
  Metrics : Prometheus text format on http://<host>:8000/metrics
  Logs    : JSON lines in $LOG_DIR/shop.log (each line carries trace_id and span_id)
  Traces  : OTLP/HTTP JSON sent to $OTLP_URL (e.g. http://jaeger:4318/v1/traces)
  Events  : JSON lines in $LOG_DIR/events.log (deployments, config changes, fault switches)
Fault switch: write one word into $CONTROL_DIR/fault ->  none | payment-slow | db-pool
Call path: frontend -> checkout -> inventory -> postgres (db)  and  checkout -> payment (external PSP)."""
import json, os, random, threading, time, urllib.request
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


LOG_DIR, CONTROL_DIR = os.environ.get("LOG_DIR", "logs"), os.environ.get("CONTROL_DIR", "control")
OTLP_URL, RPS = os.environ.get("OTLP_URL", ""), float(os.environ.get("RPS", "8"))
BUCKETS = [0.05, 0.1, 0.25, 0.5, 1, 2.5, 5]
os.makedirs(LOG_DIR, exist_ok=True); os.makedirs(CONTROL_DIR, exist_ok=True)
lock = threading.Lock()
counters, hist, gauges, spans_out = {}, {}, {}, []


def hexid(n): return "%0*x" % (n, random.getrandbits(n * 4))
def inc(key, v=1):
    counters[key] = counters.get(key, 0) + v
def observe(service, route, sec):
    h = hist.setdefault((service, route), {"b": [0] * len(BUCKETS), "sum": 0.0, "count": 0})
    for i, b in enumerate(BUCKETS):
        if sec <= b: h["b"][i] += 1
    h["sum"] += sec; h["count"] += 1
def log(level, service, tid, sid, msg, **extra):
    rec = {"ts": datetime.now().astimezone().isoformat(timespec="milliseconds"),
           "level": level, "service": service, "trace_id": tid, "span_id": sid, "message": msg, **extra}
    with open(os.path.join(LOG_DIR, "shop.log"), "a") as f: f.write(json.dumps(rec) + "\n")
def event(kind, msg, **extra):
    rec = {"ts": datetime.now().astimezone().isoformat(timespec="seconds"), "type": kind, "message": msg, **extra}
    with open(os.path.join(LOG_DIR, "events.log"), "a") as f: f.write(json.dumps(rec) + "\n")


def span(tid, parent, service, name, start, dur, kind=2, error=None, attrs=None):
    sid = hexid(16)
    a = [{"key": k, "value": {"stringValue": str(v)}} for k, v in (attrs or {}).items()]
    s = {"traceId": tid, "spanId": sid, "name": name, "kind": kind,
         "startTimeUnixNano": str(int(start * 1e9)), "endTimeUnixNano": str(int((start + dur) * 1e9)),
         "attributes": a, "status": {"code": 2, "message": error} if error else {"code": 1}}
    if parent: s["parentSpanId"] = parent
    spans_out.append((service, s))
    return sid


def request(fault):
    """Simulate one API request through the services; returns nothing, records M/L/T."""
    t0, tid = time.time(), hexid(32)
    route = random.choices(["/api/products", "/api/cart", "/api/checkout"], [5, 3, 2])[0]
    method = "POST" if route == "/api/checkout" else "GET"
    root = hexid(16)                                   # frontend span id (created last, needs duration)
    status, err = 200, None
    if route != "/api/checkout":
        dur = random.uniform(0.01, 0.06)
        if route == "/api/products":
            q = random.uniform(0.004, 0.02) + (random.uniform(0.4, 1.2) if fault == "db-pool" else 0)
            inv = span(tid, root, "inventory", "GET /inventory/items", t0 + 0.002, q + 0.004)
            span(tid, inv, "postgres", "SELECT items", t0 + 0.004, q, kind=3)
            dur += q
    else:
        cstart = t0 + 0.003
        q = random.uniform(0.01, 0.04); pay = random.uniform(0.08, 0.16)
        pay_err = inv_err = None
        if fault == "db-pool":
            q += random.uniform(0.8, 2.0)
            if random.random() < 0.35: inv_err = "HikariPool-1 - Connection is not available, request timed out after 2000ms"
        if fault == "payment-slow":
            pay = random.uniform(1.8, 3.2)
            if random.random() < 0.25: pay, pay_err = 3.0, "PSP call timed out after 3000 ms"
        chk = hexid(16)
        inv = span(tid, chk, "inventory", "POST /inventory/reserve", cstart + 0.002, q + 0.005, error=inv_err)
        span(tid, inv, "postgres", "UPDATE stock", cstart + 0.004, q, kind=3, error=inv_err)
        p0 = cstart + q + 0.01
        if not inv_err:
            span(tid, chk, "payment", "POST /payments/charge", p0, pay, kind=3, error=pay_err, attrs={"peer.service": "psp-gateway"})
        cdur = q + 0.02 + (0 if inv_err else pay)
        cerr = inv_err or pay_err
        status = 503 if inv_err else 504 if pay_err else 201
        spans_out.append(("checkout", {"traceId": tid, "spanId": chk, "parentSpanId": root, "name": "POST /checkout", "kind": 2,
                                       "startTimeUnixNano": str(int(cstart * 1e9)), "endTimeUnixNano": str(int((cstart + cdur) * 1e9)),
                                       "attributes": [], "status": {"code": 2, "message": cerr} if cerr else {"code": 1}}))
        observe("checkout", "/checkout", cdur); inc(("checkout", "/checkout", "POST", str(status)))
        if not inv_err:
            observe("payment", "/payments/charge", pay); inc(("payment", "/payments/charge", "POST", "504" if pay_err else "200"))
        if inv_err:
            log("ERROR", "inventory", tid, inv, "Stock reservation failed: " + inv_err, exception="java.sql.SQLTransientConnectionException")
            log("ERROR", "checkout", tid, chk, "Checkout failed: inventory unavailable", http_status=503)
            inc(("db_timeouts",))
        elif pay_err:
            log("ERROR", "payment", tid, chk, "Charge failed: " + pay_err, exception="java.net.SocketTimeoutException")
            log("ERROR", "checkout", tid, chk, "Checkout failed: payment timeout", http_status=504)
        else:
            log("INFO", "checkout", tid, chk, "Checkout completed in %d ms" % (cdur * 1000))
        dur = cdur + 0.006
    spans_out.append(("frontend", {"traceId": tid, "spanId": root, "name": f"{method} {route}", "kind": 2,
                                   "startTimeUnixNano": str(int(t0 * 1e9)), "endTimeUnixNano": str(int((t0 + dur) * 1e9)),
                                   "attributes": [{"key": "http.route", "value": {"stringValue": route}},
                                                  {"key": "http.response.status_code", "value": {"intValue": str(status)}}],
                                   "status": {"code": 2} if status >= 500 else {"code": 1}}))
    observe("frontend", route, dur); inc(("frontend", route, method, str(status)))
    if status >= 500:
        log("ERROR", "frontend", tid, root, f"{method} {route} -> {status}", http_status=status, duration_ms=int(dur * 1000))


def resources(fault):
    busy = {"db-pool": 1.0, "payment-slow": 0.35}.get(fault, 0.25)
    gauges[("db_pool_connections_max", "inventory")] = 10
    gauges[("db_pool_connections_active", "inventory")] = 10 if fault == "db-pool" else random.randint(1, 4)
    gauges[("db_pool_pending_threads", "inventory")] = random.randint(15, 40) if fault == "db-pool" else 0
    for svc, base in (("frontend", 0.22), ("checkout", 0.30), ("inventory", 0.18), ("payment", 0.12)):
        extra = 0.5 if (fault == "db-pool" and svc == "inventory") else 0
        gauges[("process_cpu_utilization_ratio", svc)] = round(min(0.97, base + extra + random.uniform(-0.05, 0.05)), 3)
    gauges[("http_client_inflight_requests", "checkout")] = random.randint(20, 35) if fault == "payment-slow" else random.randint(0, 3)


def metrics_text():
    out = ["# HELP http_server_requests_total Completed HTTP requests.", "# TYPE http_server_requests_total counter"]
    for k, v in sorted((k, v) for k, v in counters.items() if len(k) == 4):
        out.append(f'http_server_requests_total{{service="{k[0]}",route="{k[1]}",method="{k[2]}",status="{k[3]}"}} {v}')
    out += ["# HELP http_server_request_duration_seconds HTTP server request duration.", "# TYPE http_server_request_duration_seconds histogram"]
    for (svc, route), h in sorted(hist.items()):
        lbl = f'service="{svc}",route="{route}"'
        for b, c in zip(BUCKETS, h["b"]): out.append(f'http_server_request_duration_seconds_bucket{{{lbl},le="{b}"}} {c}')
        out += [f'http_server_request_duration_seconds_bucket{{{lbl},le="+Inf"}} {h["count"]}',
                f'http_server_request_duration_seconds_sum{{{lbl}}} {h["sum"]:.6f}', f'http_server_request_duration_seconds_count{{{lbl}}} {h["count"]}']
    out += ["# HELP db_pool_timeouts_total Connection requests that timed out waiting for the pool.", "# TYPE db_pool_timeouts_total counter",
            f'db_pool_timeouts_total{{service="inventory"}} {counters.get(("db_timeouts",), 0)}']
    for name in sorted({k[0] for k in gauges}):
        out.append(f"# TYPE {name} gauge")
        out += [f'{name}{{service="{k[1]}"}} {v}' for k, v in sorted(gauges.items()) if k[0] == name]
    return "\n".join(out) + "\n"


class H(BaseHTTPRequestHandler):
    def do_GET(self):
        with lock: body = metrics_text().encode() if self.path == "/metrics" else b"ShopSim - see /metrics\n"
        self.send_response(200); self.send_header("Content-Type", "text/plain; version=0.0.4"); self.end_headers(); self.wfile.write(body)
    def log_message(self, *a): pass


def export():
    while True:
        time.sleep(2)
        with lock: batch, spans_out[:] = list(spans_out), []
        if not (OTLP_URL and batch): continue
        by = {}
        for svc, s in batch: by.setdefault(svc, []).append(s)
        body = {"resourceSpans": [{"resource": {"attributes": [{"key": "service.name", "value": {"stringValue": svc}}]},
                                   "scopeSpans": [{"scope": {"name": "shopsim"}, "spans": ss}]} for svc, ss in by.items()]}
        try:
            urllib.request.urlopen(urllib.request.Request(OTLP_URL, json.dumps(body).encode(), {"Content-Type": "application/json"}), timeout=5).read()
        except Exception as e:
            print("OTLP export failed:", e, flush=True)


threading.Thread(target=ThreadingHTTPServer(("0.0.0.0", 8000), H).serve_forever, daemon=True).start()
threading.Thread(target=export, daemon=True).start()
fault_file, last = os.path.join(CONTROL_DIR, "fault"), None
event("deployment", "ShopSim started", version=os.environ.get("APP_VERSION", "1.0.0"))
print("ShopSim running: metrics :8000/metrics, logs in", LOG_DIR, flush=True)
while True:
    try: fault = open(fault_file).read().strip() or "none"
    except FileNotFoundError: fault = "none"
    if fault != last:
        event("fault-switch", f"Fault mode is now '{fault}'", fault=fault); print("fault mode:", fault, flush=True); last = fault
    with lock:
        request(fault); resources(fault)
    time.sleep(random.expovariate(RPS))
