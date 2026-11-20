"""TEL-D1-102 - checkout-service (port 8081).

Inventory problems are hidden behind a generic HTTP 500 - exactly what the
customer sees - so the real cause is only visible in the trace and the logs.
"""
import os

import requests
from fastapi import FastAPI, HTTPException
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.trace import Status, StatusCode
from pydantic import BaseModel

from common import setup_logging, setup_tracing

logger = setup_logging("checkout-service")
tracer = setup_tracing("checkout-service")

INVENTORY = os.getenv("INVENTORY_URL", "http://inventory:8083")
PAYMENT = os.getenv("PAYMENT_URL", "http://payment:8082")

app = FastAPI(title="ShopNow checkout-service")
FastAPIInstrumentor.instrument_app(app)
RequestsInstrumentor().instrument()


class Order(BaseModel):
    sku: str


@app.get("/health")
def health():
    return {"service": "checkout-service", "status": "healthy"}


@app.post("/checkout")
def checkout(order: Order):
    span = trace.get_current_span()
    span.set_attribute("product.sku", order.sku)
    try:
        inv = requests.post(f"{INVENTORY}/reserve/{order.sku}", timeout=5)
        pay = None
        if inv.ok:
            pay = requests.get(f"{PAYMENT}/pay", timeout=5)
    except requests.RequestException as exc:
        logger.error("Dependency call failed: %s", exc)
        span.set_attribute("http.status_code", 500)
        span.set_status(Status(StatusCode.ERROR, str(exc)))
        raise HTTPException(status_code=500, detail="Internal Server Error")

    if not inv.ok or (pay is not None and not pay.ok):
        logger.error("Checkout failed for SKU %s (inventory=%s)", order.sku, inv.status_code)
        span.set_attribute("http.status_code", 500)
        span.set_status(Status(StatusCode.ERROR, "checkout failed"))
        raise HTTPException(status_code=500, detail="Internal Server Error")  # generic on purpose
    logger.info("Checkout completed for SKU %s", order.sku)
    return {"status": "success", "sku": order.sku}
