#!/usr/bin/env python3
import argparse
import gzip
import json
import os
import random
import time
import urllib.error
import urllib.request
import uuid

HOST_NAME = "ip-172-30-0-220"

FRONTEND_TXNS = [
    ("WebTransaction/Expressjs/GET//", "GET", "/", 0.08, 0.32, 0.01, 0.05, 0.05, 0.22),
    ("WebTransaction/Expressjs/GET//search", "GET", "/search", 0.28, 0.85, 0.02, 0.08, 0.22, 0.72),
    ("WebTransaction/Expressjs/GET//booking", "GET", "/booking", 0.25, 0.78, 0.02, 0.07, 0.19, 0.65),
    ("WebTransaction/Expressjs/POST//checkout", "POST", "/checkout", 0.35, 0.95, 0.03, 0.10, 0.26, 0.78),
]

BACKEND_TXNS = [
    ("WebTransaction/SpringController/JourneyController/searchJourneys", "GET", "/api/journeys", 0.22, 0.75, 0.18, 0.66, 0.01, 0.04),
    ("WebTransaction/SpringController/BookingController/createBooking", "POST", "/api/booking", 0.20, 0.68, 0.14, 0.52, 0.02, 0.08),
    ("WebTransaction/SpringController/PaymentController/creditCardCheck", "POST", "/api/checkout/creditcard-check", 0.26, 0.82, 0.08, 0.26, 0.12, 0.46),
    ("WebTransaction/SpringController/AuthController/login", "POST", "/api/auth", 0.07, 0.24, 0.04, 0.16, 0.00, 0.02),
]


def parse_args():
    p = argparse.ArgumentParser(description="easyTravel New Relic Event API Telemetry Shipper (Day 4 Lab 1)")
    p.add_argument("--license-key", default=os.environ.get("NEW_RELIC_LICENSE_KEY", ""), help="New Relic Ingest License Key")
    p.add_argument("--account-id", default=os.environ.get("NEW_RELIC_ACCOUNT_ID", "8684150"), help="New Relic Account ID")
    p.add_argument("--region", default=os.environ.get("NEW_RELIC_REGION", "US"), choices=["US", "EU"], help="New Relic datacenter region")
    p.add_argument("--flag", default=os.path.expanduser("~/obs-lab/control/fault.flag"), help="Path to CreditCardCheckError500 flag")
    p.add_argument("--interval", type=float, default=3.0, help="Seconds between telemetry batches")
    return p.parse_args()


def is_fault_on(flag_path):
    if os.path.exists(flag_path):
        try:
            with open(flag_path, "r", encoding="utf-8") as f:
                return f.read().strip().lower() == "on"
        except OSError:
            return False
    return False


def build_events(fault_active):
    now_ms = int(time.time() * 1000)
    events = []

    # 1. Frontend transactions (mix of fast and occasional slow right-tail requests)
    for txn_name, method, uri, d_min, d_max, db_min, db_max, ext_min, ext_max in FRONTEND_TXNS:
        for _ in range(random.randint(2, 4)):
            trace_id = uuid.uuid4().hex
            span_id = uuid.uuid4().hex[:16]
            slow_tail = random.random() < 0.12
            scale = random.uniform(1.8, 2.7) if slow_tail else 1.0

            dur = round(random.uniform(d_min, d_max) * scale, 4)
            db_dur = round(min(dur * 0.35, random.uniform(db_min, db_max) * scale), 4)
            ext_dur = round(min(dur - db_dur - 0.01, random.uniform(ext_min, ext_max) * scale), 4)
            ext_dur = max(0.0, ext_dur)

            is_checkout = uri == "/checkout"
            is_err = bool(is_checkout and fault_active and random.random() < 0.42)

            if is_err:
                dur = round(random.uniform(1.35, 2.65), 4)
                ext_dur = round(dur * 0.78, 4)
                status_code = 500
            else:
                status_code = 200

            events.append({
                "eventType": "Transaction",
                "timestamp": now_ms - random.randint(0, 1500),
                "appName": "easyTravel-Frontend",
                "name": txn_name,
                "transactionType": "Web",
                "request.method": method,
                "request.uri": uri,
                "http.statusCode": status_code,
                "duration": dur,
                "databaseDuration": db_dur,
                "databaseCallCount": random.randint(1, 3),
                "externalDuration": ext_dur,
                "externalCallCount": random.randint(1, 4),
                "error": is_err,
                "host": HOST_NAME,
                "env": "cohort",
                "trace.id": trace_id,
                "span.id": span_id,
            })

            events.append({
                "eventType": "Span",
                "timestamp": now_ms - random.randint(0, 1500),
                "appName": "easyTravel-Frontend",
                "name": f"External/easyTravel-Backend{uri}",
                "category": "http",
                "duration": ext_dur if ext_dur > 0 else dur,
                "trace.id": trace_id,
                "id": span_id,
                "host": HOST_NAME,
            })

            if is_err:
                events.append({
                    "eventType": "TransactionError",
                    "timestamp": now_ms - random.randint(0, 1500),
                    "appName": "easyTravel-Frontend",
                    "transactionName": txn_name,
                    "error.class": "CreditCardCheckError500",
                    "error.message": "HTTP 500 Internal Server Error from easyTravel-Backend /api/checkout/creditcard-check",
                    "http.statusCode": 500,
                    "host": HOST_NAME,
                    "trace.id": trace_id,
                })

    # 2. Backend transactions (DB-heavy search/booking + payment checkout)
    for txn_name, method, uri, d_min, d_max, db_min, db_max, ext_min, ext_max in BACKEND_TXNS:
        for _ in range(random.randint(2, 4)):
            trace_id = uuid.uuid4().hex
            span_id = uuid.uuid4().hex[:16]
            slow_tail = random.random() < 0.14
            scale = random.uniform(1.9, 2.9) if slow_tail else 1.0

            dur = round(random.uniform(d_min, d_max) * scale, 4)
            db_dur = round(min(dur * 0.85, random.uniform(db_min, db_max) * scale), 4)
            ext_dur = round(min(max(0.0, dur - db_dur - 0.01), random.uniform(ext_min, ext_max) * scale), 4)

            is_cc = "creditcard-check" in uri
            is_err = bool(is_cc and fault_active and random.random() < 0.45)

            if is_err:
                dur = round(random.uniform(1.25, 2.55), 4)
                ext_dur = round(dur * 0.68, 4)
                status_code = 500
            else:
                status_code = 200

            events.append({
                "eventType": "Transaction",
                "timestamp": now_ms - random.randint(0, 1500),
                "appName": "easyTravel-Backend",
                "name": txn_name,
                "transactionType": "Web",
                "request.method": method,
                "request.uri": uri,
                "http.statusCode": status_code,
                "duration": dur,
                "databaseDuration": db_dur,
                "databaseCallCount": random.randint(3, 12),
                "externalDuration": ext_dur,
                "externalCallCount": random.randint(0, 2),
                "error": is_err,
                "host": HOST_NAME,
                "env": "cohort",
                "trace.id": trace_id,
                "span.id": span_id,
            })

            events.append({
                "eventType": "Span",
                "timestamp": now_ms - random.randint(0, 1500),
                "appName": "easyTravel-Backend",
                "name": f"Datastore/statement/PostgreSQL{uri}",
                "category": "datastore",
                "duration": db_dur,
                "trace.id": trace_id,
                "id": span_id,
                "host": HOST_NAME,
            })

            if is_err:
                events.append({
                    "eventType": "TransactionError",
                    "timestamp": now_ms - random.randint(0, 1500),
                    "appName": "easyTravel-Backend",
                    "transactionName": txn_name,
                    "error.class": "CreditCardCheckError500",
                    "error.message": "CreditCardCheckError500: Payment gateway returned HTTP 500 on /api/checkout/creditcard-check",
                    "http.statusCode": 500,
                    "host": HOST_NAME,
                    "trace.id": trace_id,
                })

    return events


def post_events(account_id, license_key, region, events):
    base = "https://insights-collector.eu01.nr-data.net" if region == "EU" else "https://insights-collector.newrelic.com"
    url = f"{base}/v1/accounts/{account_id}/events"
    raw = json.dumps(events).encode("utf-8")
    compressed = gzip.compress(raw)
    req = urllib.request.Request(
        url,
        data=compressed,
        headers={
            "Content-Type": "application/json",
            "Content-Encoding": "gzip",
            "Api-Key": license_key,
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.status, resp.read().decode("utf-8", errors="replace")


def main():
    args = parse_args()
    if not args.license_key:
        raise SystemExit("ERROR: Set NEW_RELIC_LICENSE_KEY or pass --license-key <INGEST_KEY>.")

    os.makedirs(os.path.dirname(os.path.abspath(args.flag)), exist_ok=True)
    if not os.path.exists(args.flag):
        with open(args.flag, "w", encoding="utf-8") as f:
            f.write("off\n")

    print(f"Shipping easyTravel Transaction/TransactionError/Span events to New Relic account {args.account_id} ({args.region})...")
    while True:
        try:
            fault = is_fault_on(args.flag)
            batch = build_events(fault)
            status, body = post_events(args.account_id, args.license_key, args.region, batch)
            print(f"[{time.strftime('%H:%M:%S')}] Sent {len(batch)} events (fault={'ON' if fault else 'OFF'}) -> HTTP {status}")
        except urllib.error.HTTPError as e:
            print(f"[ERROR] HTTP {e.code}: {e.read().decode('utf-8', errors='replace')}")
        except Exception as e:
            print(f"[WARN] Post failed: {e}")
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
