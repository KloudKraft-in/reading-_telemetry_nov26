#!/usr/bin/env python3
import http.server
import random
import threading
import time

FLAG_FILE = "/app/fault.flag"
BUCKETS = [0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]

ROUTES = [
    ("easytravel-frontend", "/", "GET", 12, (0.015, 0.06)),
    ("easytravel-frontend", "/search", "GET", 10, (0.03, 0.12)),
    ("easytravel-frontend", "/booking", "POST", 6, (0.06, 0.20)),
    ("easytravel-frontend", "/checkout", "POST", 8, (0.11, 0.245)),
    ("easytravel-backend", "/api/catalog", "GET", 10, (0.02, 0.09)),
    ("easytravel-backend", "/api/booking", "POST", 6, (0.05, 0.18)),
    ("easytravel-backend", "/api/payment", "POST", 8, (0.09, 0.24)),
    ("easytravel-backend", "/api/notify", "POST", 4, (0.02, 0.08)),
]

lock = threading.Lock()
req_counts = {}
dur_buckets = {}
dur_sums = {}
dur_counts = {}

def is_fault_on():
    try:
        with open(FLAG_FILE, "r") as f:
            return f.read().strip().lower() == "on"
    except FileNotFoundError:
        return False

def observe(service, route, method, status, duration):
    req_key = (service, route, method, status)
    req_counts[req_key] = req_counts.get(req_key, 0) + 1
    hist_key = (service, route)
    if hist_key not in dur_buckets:
        dur_buckets[hist_key] = {b: 0 for b in BUCKETS}
        dur_buckets[hist_key]["+Inf"] = 0
        dur_sums[hist_key] = 0.0
        dur_counts[hist_key] = 0
    for b in BUCKETS:
        if duration <= b:
            dur_buckets[hist_key][b] += 1
    dur_buckets[hist_key]["+Inf"] += 1
    dur_sums[hist_key] += duration
    dur_counts[hist_key] += 1

def traffic_loop():
    while True:
        fault = is_fault_on()
        with lock:
            for service, route, method, rate_per_sec, (lo, hi) in ROUTES:
                n = max(1, int(random.gauss(rate_per_sec, 1.5)))
                for _ in range(n):
                    is_checkout_path = route in ("/checkout", "/api/payment")
                    if fault and is_checkout_path and random.random() < 0.35:
                        status = "500"
                        dur = random.uniform(0.18, 0.248)
                    else:
                        status = "200"
                        dur = random.uniform(lo, hi)
                    observe(service, route, method, status, dur)
        time.sleep(1.0)

class MetricsHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/metrics":
            self.send_response(404)
            self.end_headers()
            return
        lines = [
            "# HELP http_server_requests_total Total HTTP requests processed",
            "# TYPE http_server_requests_total counter",
        ]
        with lock:
            for (svc, route, method, status), val in sorted(req_counts.items()):
                lines.append(
                    f'http_server_requests_total{{env="cohort",service="{svc}",route="{route}",method="{method}",status="{status}"}} {val}'
                )
            lines.extend([
                "# HELP http_server_request_duration_seconds HTTP request latency histogram",
                "# TYPE http_server_request_duration_seconds histogram",
            ])
            for (svc, route), bmap in sorted(dur_buckets.items()):
                for b in BUCKETS:
                    lines.append(
                        f'http_server_request_duration_seconds_bucket{{env="cohort",service="{svc}",route="{route}",le="{b}"}} {bmap[b]}'
                    )
                lines.append(
                    f'http_server_request_duration_seconds_bucket{{env="cohort",service="{svc}",route="{route}",le="+Inf"}} {bmap["+Inf"]}'
                )
                lines.append(
                    f'http_server_request_duration_seconds_sum{{env="cohort",service="{svc}",route="{route}"}} {dur_sums[(svc, route)]:.6f}'
                )
                lines.append(
                    f'http_server_request_duration_seconds_count{{env="cohort",service="{svc}",route="{route}"}} {dur_counts[(svc, route)]}'
                )
        payload = ("\n".join(lines) + "\n").encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; version=0.0.4")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format, *args):
        return

if __name__ == "__main__":
    threading.Thread(target=traffic_loop, daemon=True).start()
    server = http.server.ThreadingHTTPServer(("0.0.0.0", 8000), MetricsHandler)
    server.serve_forever()
