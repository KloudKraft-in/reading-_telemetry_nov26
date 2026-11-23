#!/usr/bin/env python3
import argparse
import json
import os
import random
import time
import urllib.request
import uuid
from datetime import datetime, timezone

def parse_args():
    p = argparse.ArgumentParser(description="easyTravel JSON log shipper for Loki (Day 4 Lab 3)")
    p.add_argument("--loki", default="http://localhost:3100", help="Loki base URL (e.g. http://localhost:3100)")
    p.add_argument("--flag", default=os.path.expanduser("~/obs-lab/control/fault.flag"), help="Path to fault flag file")
    p.add_argument("--interval", type=float, default=1.0, help="Seconds between log batches")
    return p.parse_args()

def is_fault_on(flag_path):
    if os.path.exists(flag_path):
        try:
            with open(flag_path, "r", encoding="utf-8") as f:
                return f.read().strip().lower() == "on"
        except OSError:
            return False
    return False

def iso_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

def ns_now():
    return str(int(time.time() * 1_000_000_000))

def build_streams(fault_active):
    fe_values = []
    be_values = []
    ts_ns = ns_now()

    for _ in range(random.randint(2, 4)):
        trace_id = uuid.uuid4().hex[:16]
        fe_span = uuid.uuid4().hex[:8]
        be_span = uuid.uuid4().hex[:8]
        route = random.choice(["/", "/search", "/booking"])
        be_route = "/api/journeys" if route == "/search" else "/api/booking"
        dur_be = random.randint(85, 420)
        dur_fe = dur_be + random.randint(15, 60)

        be_msg = f"Booking completed in {dur_be} ms" if route == "/booking" else f"Request handled in {dur_be} ms"
        fe_msg = f"GET {route} -> 200 ({dur_fe} ms)"

        fe_log = {
            "ts": iso_now(),
            "level": "INFO",
            "service": "easytravel-frontend",
            "message": fe_msg,
            "route": route,
            "http_status": 200,
            "duration_ms": dur_fe,
            "exception": "",
            "trace_id": trace_id,
            "span_id": fe_span
        }
        be_log = {
            "ts": iso_now(),
            "level": "INFO",
            "service": "easytravel-backend",
            "message": be_msg,
            "route": be_route,
            "http_status": 200,
            "duration_ms": dur_be,
            "exception": "",
            "trace_id": trace_id,
            "span_id": be_span
        }
        fe_values.append([ts_ns, json.dumps(fe_log, separators=(",", ":"))])
        be_values.append([ts_ns, json.dumps(be_log, separators=(",", ":"))])

    trace_id = uuid.uuid4().hex[:16]
    fe_span = uuid.uuid4().hex[:8]
    be_span = uuid.uuid4().hex[:8]

    if fault_active and random.random() < 0.65:
        dur_be = random.randint(1100, 2300)
        dur_fe = dur_be + random.randint(30, 90)
        be_log = {
            "ts": iso_now(),
            "level": "ERROR",
            "service": "easytravel-backend",
            "message": "Booking failed: CreditCardCheckError500 on /api/checkout/creditcard-check",
            "route": "/api/checkout/creditcard-check",
            "http_status": 500,
            "duration_ms": dur_be,
            "exception": "CreditCardCheckException",
            "trace_id": trace_id,
            "span_id": be_span
        }
        fe_log = {
            "ts": iso_now(),
            "level": "ERROR",
            "service": "easytravel-frontend",
            "message": f"POST /checkout -> 500 ({dur_fe} ms)",
            "route": "/checkout",
            "http_status": 500,
            "duration_ms": dur_fe,
            "exception": "CreditCardCheckException",
            "trace_id": trace_id,
            "span_id": fe_span
        }
    else:
        dur_be = random.randint(240, 680)
        dur_fe = dur_be + random.randint(20, 65)
        be_log = {
            "ts": iso_now(),
            "level": "INFO",
            "service": "easytravel-backend",
            "message": f"Booking completed in {dur_be} ms",
            "route": "/api/checkout/creditcard-check",
            "http_status": 200,
            "duration_ms": dur_be,
            "exception": "",
            "trace_id": trace_id,
            "span_id": be_span
        }
        fe_log = {
            "ts": iso_now(),
            "level": "INFO",
            "service": "easytravel-frontend",
            "message": f"POST /checkout -> 200 ({dur_fe} ms)",
            "route": "/checkout",
            "http_status": 200,
            "duration_ms": dur_fe,
            "exception": "",
            "trace_id": trace_id,
            "span_id": fe_span
        }

    fe_values.append([ts_ns, json.dumps(fe_log, separators=(",", ":"))])
    be_values.append([ts_ns, json.dumps(be_log, separators=(",", ":"))])

    return {
        "streams": [
            {
                "stream": {
                    "service_name": "easytravel-frontend",
                    "deployment_environment": "cohort"
                },
                "values": fe_values
            },
            {
                "stream": {
                    "service_name": "easytravel-backend",
                    "deployment_environment": "cohort"
                },
                "values": be_values
            }
        ]
    }

def push_loki(loki_url, payload):
    url = loki_url.rstrip("/") + "/loki/api/v1/push"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=5) as resp:
        return resp.status

def main():
    args = parse_args()
    os.makedirs(os.path.dirname(os.path.abspath(args.flag)), exist_ok=True)
    if not os.path.exists(args.flag):
        with open(args.flag, "w", encoding="utf-8") as f:
            f.write("off\n")
    print(f"Shipping easyTravel JSON logs to {args.loki} (flag={args.flag})")
    while True:
        try:
            fault = is_fault_on(args.flag)
            payload = build_streams(fault)
            push_loki(args.loki, payload)
        except Exception as e:
            print(f"[WARN] Loki push failed: {e}")
        time.sleep(args.interval)

if __name__ == "__main__":
    main()
