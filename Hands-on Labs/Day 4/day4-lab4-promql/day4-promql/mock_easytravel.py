#!/usr/bin/env python3
import os
import random
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

FAULT_FLAG = "/tmp/creditcard_fault_on"

ROUTES = {
    "easytravel-frontend": ["/", "/search", "/booking", "/checkout"],
    "easytravel-backend": ["/api/journeys", "/api/booking", "/api/checkout/creditcard-check", "/api/auth"],
}

BUCKETS = [0.05, 0.1, 0.25, 0.5, 0.75, 1.0, 1.5, 2.5, 5.0]

counts = {}
buckets = {}
duration_sum = {}
duration_count = {}


def is_fault_active():
    if os.path.exists(FAULT_FLAG):
        try:
            with open(FAULT_FLAG, "r", encoding="utf-8") as f:
                return f.read().strip().lower() == "on"
        except OSError:
            return False
    return False


def record_request(svc, route, method, status, lat):
    key = (svc, route, method, status)
    counts[key] = counts.get(key, 0) + 1

    bkey = (svc, route)
    if bkey not in buckets:
        buckets[bkey] = {b: 0 for b in BUCKETS}
        buckets[bkey]["+Inf"] = 0
        duration_sum[bkey] = 0.0
        duration_count[bkey] = 0

    for b in BUCKETS:
        if lat <= b:
            buckets[bkey][b] += 1
    buckets[bkey]["+Inf"] += 1
    duration_sum[bkey] += lat
    duration_count[bkey] += 1


def tick():
    fault = is_fault_active()

    for route in ROUTES["easytravel-frontend"]:
        batch = random.randint(3, 6)
        for _ in range(batch):
            method = "POST" if route == "/checkout" else "GET"
            status = "200"
            lat = random.uniform(0.06, 0.35)

            if route == "/checkout":
                if fault:
                    lat = random.uniform(0.55, 2.10)
                    if random.random() < 0.35:
                        status = "500"
                else:
                    lat = random.uniform(0.22, 0.78)
            elif route == "/search":
                lat = random.uniform(0.14, 0.65)

            record_request("easytravel-frontend", route, method, status, lat)

    for route in ROUTES["easytravel-backend"]:
        batch = random.randint(2, 5)
        for _ in range(batch):
            method = "POST" if "checkout" in route or "booking" in route else "GET"
            status = "200"
            lat = random.uniform(0.04, 0.28)

            if "checkout" in route:
                if fault:
                    lat = random.uniform(0.50, 1.95)
                    if random.random() < 0.35:
                        status = "500"
                else:
                    lat = random.uniform(0.18, 0.68)

            record_request("easytravel-backend", route, method, status, lat)


class MetricsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/metrics":
            self.send_response(404)
            self.end_headers()
            return

        tick()
        lines = [
            "# HELP http_server_requests_total Total HTTP requests",
            "# TYPE http_server_requests_total counter",
        ]
        for (svc, route, method, status), val in sorted(counts.items()):
            lines.append(
                f'http_server_requests_total{{env="cohort",service="{svc}",route="{route}",method="{method}",status="{status}"}} {val}'
            )

        lines += [
            "# HELP http_server_request_duration_seconds Request duration histogram",
            "# TYPE http_server_request_duration_seconds histogram",
        ]
        for (svc, route), bmap in sorted(buckets.items()):
            for b in BUCKETS:
                lines.append(
                    f'http_server_request_duration_seconds_bucket{{env="cohort",service="{svc}",route="{route}",le="{b}"}} {bmap[b]}'
                )
            lines.append(
                f'http_server_request_duration_seconds_bucket{{env="cohort",service="{svc}",route="{route}",le="+Inf"}} {bmap["+Inf"]}'
            )
            lines.append(
                f'http_server_request_duration_seconds_sum{{env="cohort",service="{svc}",route="{route}"}} {duration_sum[(svc, route)]:.6f}'
            )
            lines.append(
                f'http_server_request_duration_seconds_count{{env="cohort",service="{svc}",route="{route}"}} {duration_count[(svc, route)]}'
            )

        body = ("\n".join(lines) + "\n").encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return


if __name__ == "__main__":
    tick()
    HTTPServer(("0.0.0.0", 8000), MetricsHandler).serve_forever()
