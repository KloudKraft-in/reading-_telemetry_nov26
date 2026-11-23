#!/usr/bin/env python3
"""ShopNow-Production simulator (Day 4) - standard library only.
Generates ~RPS requests per second for 5 transaction types (time-compressed: latencies are sampled, not slept) and exposes
Prometheus metrics on :8095/metrics:  http_request_duration_seconds (histogram) and http_requests_total (counter).
Labels: service, handler, method (+ status on the counter). Latency is bimodal: a fast band plus a 10 % slow tail,
so the slowest transaction (CheckoutController#processPayment) has an average of about 1.9 s but a p95 of about 4.2 s."""
import os, random, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

RPS = float(os.environ.get("RPS", "20"))
BUCKETS = (.05, .1, .25, .5, .75, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 7.5, 10)
def mix(fast, slow, p_slow): return lambda: random.uniform(*slow) if random.random() < p_slow else random.uniform(*fast)
# handler: (service, latency sampler, 5xx rate, weight)
TX = {
  "CheckoutController#processPayment":       ("payment-service",      mix((0.6, 2.8), (3.9, 4.5), 0.10), 0.06, 2),
  "OrderController#createOrder":             ("order-service",        mix((0.3, 1.4), (1.9, 2.3), 0.10), 0.02, 2),
  "InventoryController#reserveStock":        ("inventory-api",        mix((0.1, 0.8), (1.0, 1.4), 0.10), 0.03, 2),
  "NotificationController#sendConfirmation": ("notification-service", mix((0.05, 0.5), (0.7, 0.9), 0.10), 0.01, 1),
  "PaymentController#refund":                ("payment-service",      mix((0.05, 0.3), (0.45, 0.6), 0.10), 0.00, 1),
  "OrderController#getOrderStatus":          ("order-service",        mix((0.01, 0.15), (0.2, 0.3), 0.10), 0.00, 3),
}
lock = threading.Lock()
hist, reqs = {}, {}

def observe(service, handler, sec, status):
    with lock:
        h = hist.setdefault((service, handler), {"b": [0] * len(BUCKETS), "sum": 0.0, "count": 0})
        for i, b in enumerate(BUCKETS):
            if sec <= b: h["b"][i] += 1
        h["sum"] += sec; h["count"] += 1
        reqs[(service, handler, status)] = reqs.get((service, handler, status), 0) + 1

def traffic():
    names = [n for n, v in TX.items() for _ in range(v[3])]
    while True:
        n = random.choice(names); service, sampler, err, _ = TX[n]
        observe(service, n, sampler(), "500" if random.random() < err else "200")
        time.sleep(random.expovariate(RPS))

def render():
    out = ["# HELP http_request_duration_seconds HTTP request latency", "# TYPE http_request_duration_seconds histogram"]
    with lock:
        for (s, h), d in sorted(hist.items()):
            lab = f'service="{s}",handler="{h}",method="POST"'
            for b, c in zip(BUCKETS, d["b"]): out.append(f'http_request_duration_seconds_bucket{{{lab},le="{b}"}} {c}')
            out.append(f'http_request_duration_seconds_bucket{{{lab},le="+Inf"}} {d["count"]}')
            out.append(f'http_request_duration_seconds_sum{{{lab}}} {d["sum"]:.4f}'); out.append(f'http_request_duration_seconds_count{{{lab}}} {d["count"]}')
        out += ["# HELP http_requests_total HTTP requests", "# TYPE http_requests_total counter"]
        for (s, h, st), c in sorted(reqs.items()):
            out.append(f'http_requests_total{{service="{s}",handler="{h}",method="POST",status="{st}"}} {c}')
    return "\n".join(out) + "\n"

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        body = render().encode() if self.path == "/metrics" else b"ok\n"
        self.send_response(200); self.send_header("Content-Type", "text/plain; version=0.0.4"); self.end_headers(); self.wfile.write(body)
    def log_message(self, *a): pass

if __name__ == "__main__":
    for _ in range(4): threading.Thread(target=traffic, daemon=True).start()
    print("shopnow simulator on :8095", flush=True)
    ThreadingHTTPServer(("0.0.0.0", 8095), H).serve_forever()
