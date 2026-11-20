"""Steady traffic for TEL-D1-101: ~6 checkout requests per second."""
import os
import threading
import time

import requests

URL = os.getenv("TARGET", "http://checkout:8081/checkout/pay")
RPS = float(os.getenv("RPS", "6"))


def one():
    try:
        requests.get(URL, timeout=15)
    except Exception:
        pass


def main():
    print(f"[loadgen-s1] {RPS} req/s -> {URL}", flush=True)
    while True:
        threading.Thread(target=one, daemon=True).start()
        time.sleep(1.0 / RPS)


if __name__ == "__main__":
    main()
