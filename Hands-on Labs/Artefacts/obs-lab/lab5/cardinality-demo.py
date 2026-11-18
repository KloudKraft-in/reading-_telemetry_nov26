#!/usr/bin/env python3
"""Cardinality demo for Day 2 Lab 5. Serves two versions of the SAME checkout counter on :8001/metrics:
  demo_checkout_requests_total{route,status}             - bounded labels (route x status)
  demo_checkout_requests_by_user_total{route,status,user_id,order_id} - unbounded labels (one new series per order)
Each second 20 checkouts happen for random users out of USERS (default 500)."""
import os, random, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
USERS = int(os.environ.get("USERS", "500"))
low, high, lock, order = {}, {}, threading.Lock(), 100000
def tick():
    global order
    while True:
        with lock:
            for _ in range(20):
                order += 1
                route = random.choice(["/api/checkout", "/api/cart", "/api/products"])
                status = random.choices(["200", "500", "503"], [95, 3, 2])[0]
                low[(route, status)] = low.get((route, status), 0) + 1
                k = (route, status, f"u-{random.randint(1, USERS)}", str(order))
                high[k] = high.get(k, 0) + 1
        time.sleep(1)
class H(BaseHTTPRequestHandler):
    def do_GET(self):
        with lock:
            lines = ["# TYPE demo_checkout_requests_total counter"]
            lines += [f'demo_checkout_requests_total{{route="{r}",status="{s}"}} {v}' for (r, s), v in low.items()]
            lines += ["# TYPE demo_checkout_requests_by_user_total counter"]
            lines += [f'demo_checkout_requests_by_user_total{{route="{r}",status="{s}",user_id="{u}",order_id="{o}"}} {v}'
                      for (r, s, u, o), v in high.items()]
        body = ("\n".join(lines) + "\n").encode()
        self.send_response(200); self.send_header("Content-Type", "text/plain; version=0.0.4"); self.end_headers(); self.wfile.write(body)
    def log_message(self, *a): pass
threading.Thread(target=tick, daemon=True).start()
print("cardinality demo on :8001/metrics", flush=True)
ThreadingHTTPServer(("0.0.0.0", 8001), H).serve_forever()
