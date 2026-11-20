"""TEL-D1-101 - ShopNow checkout-service (port 8081).

Bimodal latency, like the incident ticket:
  ~94% of payments take ~100 ms, ~6% take ~4.6 s (timeouts customers complain about)
  ~3% of requests return HTTP 500.
The *average* stays low, the p95 does not.
"""
import asyncio
import random

from fastapi import FastAPI, HTTPException
from prometheus_client import Counter, Histogram, make_asgi_app

SLOW_SHARE = 0.06
ERROR_SHARE = 0.03

app = FastAPI(title="ShopNow checkout-service (TEL-D1-101)")

REQUESTS = Counter("http_requests_total", "Total HTTP requests",
                   ["service", "endpoint", "status"])
DURATION = Histogram("payment_duration_seconds", "Payment processing duration",
                     ["service"],
                     buckets=(0.05, 0.1, 0.15, 0.25, 0.5, 1, 2.5, 4, 4.5, 5, 10))


@app.get("/health")
def health():
    return {"service": "checkout-service", "status": "healthy"}


@app.get("/checkout/pay")
async def pay():
    slow = random.random() < SLOW_SHARE
    duration = random.uniform(4.55, 4.75) if slow else random.uniform(0.08, 0.14)
    await asyncio.sleep(duration)
    DURATION.labels(service="checkout-service").observe(duration)

    if random.random() < ERROR_SHARE:
        REQUESTS.labels("checkout-service", "checkout/pay", "500").inc()
        raise HTTPException(status_code=500, detail="Payment gateway error")
    REQUESTS.labels("checkout-service", "checkout/pay", "200").inc()
    return {"service": "checkout-service", "status": "success",
            "duration_seconds": round(duration, 3)}


app.mount("/metrics", make_asgi_app())
