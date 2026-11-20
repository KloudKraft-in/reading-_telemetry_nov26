"""TEL-D1-102 - payment-service (port 8082)."""
import time

from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from common import setup_logging, setup_tracing

logger = setup_logging("payment-service")
setup_tracing("payment-service")

app = FastAPI(title="ShopNow payment-service")
FastAPIInstrumentor.instrument_app(app)


@app.get("/health")
def health():
    return {"service": "payment-service", "status": "healthy"}


@app.get("/pay")
def pay():
    time.sleep(0.1)
    logger.info("Payment authorised")
    return {"status": "paid"}
