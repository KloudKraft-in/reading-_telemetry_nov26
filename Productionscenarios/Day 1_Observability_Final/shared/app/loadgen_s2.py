"""Traffic for TEL-D1-102.

1. Waits for the stack, then sends ONE PROD-7729 order carrying the trace id
   named in the ticket (4bf92f35...4736), so participants can find that trace.
2. Then keeps sending a mix of orders; PROD-7729 fails intermittently.
"""
import os
import random
import time

import requests

URL = os.getenv("TARGET", "http://frontend:8080/api/checkout")
PINNED = "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"
SKUS = ["PROD-1001", "PROD-2002", "PROD-3003", "PROD-7729", "PROD-7729"]


def post(sku, headers=None):
    try:
        return requests.post(URL, json={"sku": sku}, headers=headers or {}, timeout=15).status_code
    except Exception:
        return None


def main():
    for _ in range(120):                      # wait up to ~2 minutes for the stack
        if post("PROD-1001") == 200:
            break
        time.sleep(1)
    time.sleep(3)
    code = post("PROD-7729", {"traceparent": PINNED})
    print(f"[loadgen-s2] pinned trace request sent (HTTP {code})", flush=True)
    while True:
        post(random.choice(SKUS))
        time.sleep(random.uniform(0.4, 1.0))


if __name__ == "__main__":
    main()
