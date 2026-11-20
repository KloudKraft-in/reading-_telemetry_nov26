"""Shared helpers for the Day 1 lab services: Loki logging + OpenTelemetry tracing."""
import json
import logging
import os
import time
import urllib.request

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

LOKI_URL = os.getenv("LOKI_URL", "")
OTLP_ENDPOINT = os.getenv("OTLP_ENDPOINT", "")


class _TraceFilter(logging.Filter):
    def filter(self, record):
        ctx = trace.get_current_span().get_span_context()
        if ctx.is_valid:
            record.trace_id = format(ctx.trace_id, "032x")
            record.span_id = format(ctx.span_id, "016x")
        else:
            record.trace_id = record.span_id = "none"
        return True


class _LokiHandler(logging.Handler):
    def __init__(self, app_label):
        super().__init__()
        self.app_label = app_label

    def emit(self, record):
        try:
            body = {"streams": [{
                "stream": {"app": self.app_label, "level": record.levelname},
                "values": [[str(time.time_ns()), self.format(record)]],
            }]}
            req = urllib.request.Request(
                LOKI_URL.rstrip("/") + "/loki/api/v1/push",
                data=json.dumps(body).encode(),
                headers={"Content-Type": "application/json"}, method="POST")
            urllib.request.urlopen(req, timeout=2).close()
        except Exception:
            pass  # never let logging break the request


def setup_logging(app_label):
    """Console logging always; Loki push too when LOKI_URL is set."""
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s %(message)s")
    logger = logging.getLogger(app_label)
    if LOKI_URL:
        h = _LokiHandler(app_label)
        h.setFormatter(logging.Formatter(
            "%(asctime)s %(levelname)s [" + app_label + "] "
            "[trace_id=%(trace_id)s, span_id=%(span_id)s] %(message)s"))
        h.addFilter(_TraceFilter())
        logger.addHandler(h)
    return logger


def setup_tracing(service_name):
    """Send spans to Jaeger over OTLP/HTTP when OTLP_ENDPOINT is set."""
    if not OTLP_ENDPOINT:
        return trace.get_tracer(service_name)
    provider = TracerProvider(resource=Resource.create({"service.name": service_name}))
    provider.add_span_processor(BatchSpanProcessor(
        OTLPSpanExporter(endpoint=OTLP_ENDPOINT.rstrip("/") + "/v1/traces")))
    trace.set_tracer_provider(provider)
    return trace.get_tracer(service_name)
