# shop-orders-generator — Day 5 Lab 2: once a minute (EventBridge) it simulates 30 orders and writes
# CloudWatch Embedded Metric Format (EMF) log lines; CloudWatch turns them into custom metrics. Standard library only.
import json, os, random, time

NAMESPACE = os.environ.get("NAMESPACE", "ShopLab/u00")
ORDERS = 30

def emf(service, requests, errors, latencies, fault):
    return {"_aws": {"Timestamp": int(time.time() * 1000),
                     "CloudWatchMetrics": [{"Namespace": NAMESPACE, "Dimensions": [["Service"]],
                                            "Metrics": [{"Name": "Requests", "Unit": "Count"},
                                                        {"Name": "Errors", "Unit": "Count"},
                                                        {"Name": "LatencyMs", "Unit": "Milliseconds"}]}]},
            "Service": service, "Requests": requests, "Errors": errors, "LatencyMs": latencies, "fault": fault}

def handler(event, context):
    fault = os.environ.get("FAULT", "none").strip()          # none | payment-errors | payment-slow
    rnd = random.Random(int(time.time() // 60))             # same minute -> same numbers for everyone
    pay_lat, pay_err, chk_lat, chk_err = [], 0, [], 0
    for _ in range(ORDERS):
        p = rnd.uniform(90, 220)
        failed = rnd.random() < 0.01
        if fault == "payment-errors" and rnd.random() < 0.40:
            failed = True
        if fault == "payment-slow":
            p = rnd.uniform(900, 1600)
        inv = rnd.uniform(25, 60)
        pay_lat.append(round(p, 1)); chk_lat.append(round(inv + p + rnd.uniform(5, 20), 1))
        pay_err += failed; chk_err += failed
    print(json.dumps(emf("payment", ORDERS, pay_err, pay_lat, fault)))
    print(json.dumps(emf("checkout", ORDERS, chk_err, chk_lat, fault)))
    return {"fault": fault, "errors": chk_err}
