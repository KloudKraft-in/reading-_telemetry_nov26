"""TEL-D1-102 - frontend (port 8080)."""
import os

import requests
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from pydantic import BaseModel

from common import setup_logging, setup_tracing

logger = setup_logging("frontend")
setup_tracing("frontend")

CHECKOUT = os.getenv("CHECKOUT_URL", "http://checkout:8081")

app = FastAPI(title="ShopNow frontend")
FastAPIInstrumentor.instrument_app(app)
RequestsInstrumentor().instrument()


class Order(BaseModel):
    sku: str


@app.get("/health")
def health():
    return {"service": "frontend", "status": "healthy"}


@app.post("/api/checkout")
def checkout(order: Order):
    try:
        r = requests.post(f"{CHECKOUT}/checkout", json={"sku": order.sku}, timeout=10)
        return JSONResponse(status_code=r.status_code, content=r.json())
    except requests.RequestException as exc:
        logger.error("Checkout unreachable: %s", exc)
        return JSONResponse(status_code=502, content={"detail": "Bad Gateway"})
