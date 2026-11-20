"""TEL-D1-103 - telemetry simulator (port 8083).

Stands in for the PostgreSQL primary host, its exporter and the four application
services at shift start. One real problem (disk I/O queue saturation on the
PostgreSQL primary, caused by an unindexed batch analytics query) and five
alerts that are consequences of it.

  /metrics           Prometheus metrics
  /pg_stat_activity  what a DBA would see in PostgreSQL
"""
import math
import time

from fastapi import FastAPI
from prometheus_client import CollectorRegistry, Gauge, make_asgi_app

app = FastAPI(title="ShopNow DB + app telemetry simulator (TEL-D1-103)")
START = time.time()
registry = CollectorRegistry()


def g(name, doc, labels=()):
    return Gauge(name, doc, labels, registry=registry)


# --- database host (USE method: Utilization / Saturation / Errors) ---
DB_QUEUE = g("db_disk_queue_length", "PostgreSQL primary disk queue length (saturation)", ["instance_role"])
DB_AWAIT = g("db_disk_io_await_milliseconds", "PostgreSQL primary average disk I/O wait", ["instance_role"])
DB_CPU = g("db_cpu_utilization_percent", "PostgreSQL primary CPU utilization", ["instance_role"])
DB_MEM = g("db_memory_utilization_percent", "PostgreSQL primary memory utilization", ["instance_role"])
DB_ERR = g("db_disk_hardware_errors_total", "PostgreSQL primary disk hardware errors", ["instance_role"])
# --- application symptoms ---
CHECKOUT_P95 = g("checkout_latency_p95_seconds", "checkout p95 latency", ["service"])
PAY_TIMEOUT = g("payment_timeout_ratio", "share of payment calls timing out", ["service"])
PROFILE_P95 = g("profile_query_p95_seconds", "customer profile query p95", ["service"])
ORDERS_504 = g("order_history_http_504_ratio", "share of order-history requests returning 504", ["service"])


def wobble(base, amp, period=40.0):
    return base + amp * math.sin((time.time() - START) / period * 2 * math.pi)


@app.middleware("http")
async def refresh(request, call_next):
    DB_QUEUE.labels("primary").set(round(wobble(38, 1.5), 1))        # normal < 2
    DB_AWAIT.labels("primary").set(round(wobble(280, 8), 1))         # ms
    DB_CPU.labels("primary").set(round(wobble(42, 1.0), 1))
    DB_MEM.labels("primary").set(round(wobble(65, 0.5), 1))
    DB_ERR.labels("primary").set(0)
    CHECKOUT_P95.labels("checkout-service").set(round(wobble(4.2, 0.2), 2))
    PAY_TIMEOUT.labels("payment-service").set(round(wobble(0.12, 0.01), 3))
    PROFILE_P95.labels("profile-service").set(round(wobble(2.8, 0.2), 2))
    ORDERS_504.labels("order-history").set(round(wobble(0.09, 0.01), 3))
    return await call_next(request)


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/pg_stat_activity")
def pg_stat_activity():
    return {
        "database": "PostgreSQL 15.4 - shopnow-db-primary",
        "role": "primary",
        "sessions": [
            {"pid": 9182, "usename": "analytics_batch", "application_name": "nightly-report-runner",
             "state": "active", "wait_event_type": "IO", "wait_event": "DataFileRead",
             "running_for": "00:47:12",
             "query": "SELECT customer_id, SUM(total) FROM orders o JOIN order_items i "
                      "ON i.order_id = o.id WHERE o.created_at > now() - interval '90 days' "
                      "GROUP BY customer_id ORDER BY 2 DESC  -- no index on created_at (seq scan)"},
            {"pid": 7311, "usename": "checkout_app", "application_name": "checkout-service",
             "state": "active", "wait_event_type": "IO", "wait_event": "DataFileRead",
             "running_for": "00:00:04", "query": "INSERT INTO orders ..."},
            {"pid": 7340, "usename": "profile_app", "application_name": "profile-service",
             "state": "active", "wait_event_type": "IO", "wait_event": "DataFileRead",
             "running_for": "00:00:03", "query": "SELECT * FROM customer_profile WHERE id = $1"},
            {"pid": 7388, "usename": "orders_app", "application_name": "order-history",
             "state": "active", "wait_event_type": "IO", "wait_event": "DataFileRead",
             "running_for": "00:00:30", "query": "SELECT * FROM orders WHERE customer_id = $1"},
        ],
        "replicas": [{"name": "shopnow-db-replica-1", "state": "streaming", "lag_seconds": 0.4}],
    }


app.mount("/metrics", make_asgi_app(registry))
