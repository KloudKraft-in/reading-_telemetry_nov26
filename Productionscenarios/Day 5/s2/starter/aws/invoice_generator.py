# invoice-generator — TEL-D5-502. Standard library + boto3 (already in the Lambda runtime); no layer, no X-Ray SDK.
# What it does: renders an order invoice (fast), uploads it to the archive bucket (S3 PutObject), returns.
# Telemetry it emits: 2 JSON log lines per invocation and 2 X-Ray subsegments sent as UDP documents to the X-Ray daemon address.
import json, os, random, socket, threading, time
import boto3
from botocore.config import Config

BUCKET = os.environ["ARCHIVE_BUCKET"]
SIMULATE = os.environ.get("STALL_MODE") == "simulate"        # instructor fallback when no VPC is available
s3 = boto3.client("s3", config=Config(connect_timeout=60, read_timeout=60, retries={"max_attempts": 1}))

def trace_ids():
    h = dict(p.split("=", 1) for p in os.environ.get("_X_AMZN_TRACE_ID", "").split(";") if "=" in p)
    return h.get("Root", ""), h.get("Parent", ""), h.get("Sampled") == "1"

def log(level, message, **fields):
    print(json.dumps({"level": level, "service": "invoice-generator", "message": message, "trace_id": trace_ids()[0], **fields}))

def subsegment(name, start, end, annotations=None, fault=False):
    root, parent, sampled = trace_ids()
    addr = os.environ.get("AWS_XRAY_DAEMON_ADDRESS", "")
    if not (sampled and parent and ":" in addr):
        return
    doc = {"id": "%016x" % random.getrandbits(64), "name": name, "type": "subsegment", "trace_id": root,
           "parent_id": parent, "start_time": start, "end_time": end, "annotations": annotations or {}}
    if fault:
        doc["fault"] = True
    host, port = addr.rsplit(":", 1)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.sendto(('{"format": "json", "version": 1}\n' + json.dumps(doc)).encode(), (host, int(port)))
    s.close()

def handler(event, context):
    invoice = "inv-%s" % context.aws_request_id[:8]
    log("INFO", "generating invoice", invoice_id=invoice)
    t0 = time.time()
    body = json.dumps({"invoice": invoice, "lines": 3, "total": 129.9})
    time.sleep(0.15)
    subsegment("render-invoice", t0, time.time(), {"invoice_id": invoice})
    t1 = time.time()
    outcome = {}

    def put():
        try:
            if SIMULATE:
                time.sleep(3600)
            s3.put_object(Bucket=BUCKET, Key="invoices/%s.json" % invoice, Body=body.encode())
            outcome["ok"] = True
        except Exception as e:                                   # a refused or failed call ends the thread
            outcome["error"] = repr(e)

    th = threading.Thread(target=put, daemon=True)
    th.start()
    th.join(timeout=max(0.1, context.get_remaining_time_in_millis() / 1000 - 0.25))
    if th.is_alive():                                            # still blocked: record the span, then wait for the platform to stop us
        subsegment("S3:PutObject", t1, time.time(), {"bucket": BUCKET, "invoice_id": invoice}, fault=True)
        th.join()
    subsegment("S3:PutObject", t1, time.time(), {"bucket": BUCKET, "invoice_id": invoice}, fault="error" in outcome)
    log("INFO" if outcome.get("ok") else "ERROR", "invoice stored" if outcome.get("ok") else "invoice not stored",
        invoice_id=invoice, duration_ms=round((time.time() - t0) * 1000, 1))
    return {"invoice": invoice, "stored": bool(outcome.get("ok"))}
