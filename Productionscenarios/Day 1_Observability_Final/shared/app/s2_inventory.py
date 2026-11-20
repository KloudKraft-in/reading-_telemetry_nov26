"""TEL-D1-102 - inventory-service (port 8083)."""
import os
import random
import time

from fastapi import FastAPI, HTTPException
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.trace import Status, StatusCode

from common import setup_logging, setup_tracing

logger = setup_logging("inventory-service")
tracer = setup_tracing("inventory-service")

PINNED_TRACE = "4bf92f3577b34da6a3ce929d0e0e4736"   # the trace named in the ticket
LOCKED_SKU = "PROD-7729"
FAIL_SHARE = float(os.getenv("LOCKED_SKU_FAIL_SHARE", "0.6"))   # intermittent
STOCK = {"PROD-1001": 100, "PROD-2002": 50, "PROD-3003": 75, "PROD-7729": 25}

app = FastAPI(title="ShopNow inventory-service")
FastAPIInstrumentor.instrument_app(app)


@app.get("/health")
def health():
    return {"service": "inventory-service", "status": "healthy"}


@app.post("/reserve/{sku}")
def reserve(sku: str):
    with tracer.start_as_current_span("inventory.reserveStock") as span:
        span.set_attribute("product.sku", sku)
        trace_id = format(span.get_span_context().trace_id, "032x")

        if sku == LOCKED_SKU and (trace_id == PINNED_TRACE or random.random() < FAIL_SHARE):
            time.sleep(0.43)
            msg = ("StockReservationException: SKU PROD-7729 warehouse bin "
                   "locked due to cycle count audit")
            logger.error(msg)
            span.set_attribute("error", True)
            span.set_attribute("error.type", "StockReservationException")
            span.record_exception(RuntimeError(msg))
            span.set_status(Status(StatusCode.ERROR, msg))
            raise HTTPException(status_code=409, detail=msg)

        time.sleep(0.05)
        if sku not in STOCK:
            span.set_status(Status(StatusCode.ERROR, "unknown sku"))
            logger.error("Unknown SKU %s", sku)
            raise HTTPException(status_code=404, detail="SKU not found")
        logger.info("Stock reserved for SKU %s", sku)
        return {"sku": sku, "status": "reserved"}
