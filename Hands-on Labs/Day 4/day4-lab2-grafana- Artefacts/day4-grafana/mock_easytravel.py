import os, time, random
from http.server import HTTPServer, BaseHTTPRequestHandler

START = time.time()
FAULT_FLAG = "/tmp/creditcard_fault_on"
ROUTES = {
    "easytravel-frontend": ["/", "/search", "/booking", "/checkout"],
    "easytravel-backend": ["/api/journeys", "/api/booking", "/api/checkout/creditcard-check", "/api/auth"]
}
BUCKETS = [0.05, 0.1, 0.25, 0.5, 0.75, 1.0, 1.5, 2.5, 5.0]

counts = {}
buckets = {}

def is_fault_active():
    # Manual Cue C1/C2 override via faultctl.sh (/tmp/creditcard_fault_on)
    # Fallback to automatic 3-minute cycle if manual toggle has not been used
    if os.path.exists(FAULT_FLAG):
        with open(FAULT_FLAG, "r") as f:
            state = f.read().strip().lower()
        return state == "on"
    elapsed = time.time() - START
    return (int(elapsed) % 180) > 120

def tick():
    fault = is_fault_active()
    for svc, rlist in ROUTES.items():
        for r in rlist:
            for _ in range(random.randint(2, 6)):
                status = "200"
                lat = random.uniform(0.06, 0.38)
                if "checkout" in r:
                    lat = random.uniform(0.45, 1.85) if fault else random.uniform(0.25, 0.85)
                    if fault and random.random() < 0.28:
                        status = "500"
                    elif random.random() < 0.03:
                        status = "400"
                elif "search" in r:
                    lat = random.uniform(0.15, 0.75)
                    if random.random() < 0.02:
                        status = "404"
                key = (svc, r, status)
                counts[key] = counts.get(key, 0) + 1
                bkey = (svc, r)
                if bkey not in buckets:
                    buckets[bkey] = {b: 0 for b in BUCKETS}
                    buckets[bkey]["+Inf"] = 0
                for b in BUCKETS:
                    if lat <= b:
                        buckets[bkey][b] += 1
                buckets[bkey]["+Inf"] += 1

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/metrics":
            self.send_response(404); self.end_headers(); return
        tick()
        lines = [
            "# HELP http_server_requests_total Total HTTP requests",
            "# TYPE http_server_requests_total counter"
        ]
        for (svc, r, st), val in counts.items():
            lines.append(f'http_server_requests_total{{env="cohort",service="{svc}",route="{r}",status="{st}"}} {val}')
        lines += [
            "# HELP http_server_request_duration_seconds Request duration histogram",
            "# TYPE http_server_request_duration_seconds histogram"
        ]
        for (svc, r), bmap in buckets.items():
            for b in BUCKETS:
                lines.append(f'http_server_request_duration_seconds_bucket{{env="cohort",service="{svc}",route="{r}",le="{b}"}} {bmap[b]}')
            lines.append(f'http_server_request_duration_seconds_bucket{{env="cohort",service="{svc}",route="{r}",le="+Inf"}} {bmap["+Inf"]}')
        body = ("\n".join(lines) + "\n").encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; version=0.0.4")
        self.end_headers()
        self.wfile.write(body)
    def log_message(self, *args): pass

HTTPServer(("0.0.0.0", 8000), Handler).serve_forever()
