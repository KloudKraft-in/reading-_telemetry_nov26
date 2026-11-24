# shop-checkout — Day 5 Lab 1: structured JSON logs + X-Ray subsegments, standard library only (no SDK, no layer)
import json, os, random, socket, time

class PaymentTimeout(Exception):
    pass

def trace_ids():
    # _X_AMZN_TRACE_ID looks like: Root=1-...;Parent=<segment id>;Sampled=1
    h = dict(p.split("=", 1) for p in os.environ.get("_X_AMZN_TRACE_ID", "").split(";") if "=" in p)
    return h.get("Root", ""), h.get("Parent", ""), h.get("Sampled") == "1"

def log(level, message, **fields):
    print(json.dumps({"level": level, "message": message, "service": "shop-checkout", "trace_id": trace_ids()[0], **fields}))

def subsegment(name, start, end, annotations=None, fault=False, error=False):
    root, parent, sampled = trace_ids()
    addr = os.environ.get("AWS_XRAY_DAEMON_ADDRESS", "")
    if not (sampled and parent and ":" in addr):
        return
    doc = {"id": "%016x" % random.getrandbits(64), "name": name, "type": "subsegment", "trace_id": root,
           "parent_id": parent, "start_time": start, "end_time": end, "annotations": annotations or {}}
    if fault: doc["fault"] = True
    if error: doc["error"] = True
    host, port = addr.rsplit(":", 1)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.sendto(('{"format": "json", "version": 1}\n' + json.dumps(doc)).encode(), (host, int(port)))
    s.close()

def handler(event, context):
    n = int(event.get("n", 1))
    order = event.get("order_id", "o-%03d" % n)
    result = ("declined" if n % 10 == 0 else "timeout" if n % 20 == 13 else "slow" if n % 15 == 7 else "ok")
    t0 = time.time()
    time.sleep(0.02 + 0.01 * (1 + n % 4))
    subsegment("inventory", t0, time.time(), {"order_id": order})
    t1 = time.time()
    if result == "timeout":
        time.sleep(0.8)
        subsegment("payment", t1, time.time(), {"order_id": order, "payment_result": result}, fault=True)
        log("ERROR", "payment provider timeout", order_id=order, status=504, payment_result=result)
        raise PaymentTimeout("PSP did not answer within 800 ms for " + order)
    time.sleep({"ok": 0.12 + 0.02 * (n % 5), "slow": 1.2, "declined": 0.08}[result])
    subsegment("payment", t1, time.time(), {"order_id": order, "payment_result": result}, error=(result == "declined"))
    ms = round((time.time() - t0) * 1000, 1)
    status = 402 if result == "declined" else 201
    log("WARN" if status == 402 else "INFO", "payment declined" if status == 402 else "order processed",
        order_id=order, status=status, payment_result=result, duration_ms=ms)
    return {"statusCode": status, "body": json.dumps({"order_id": order, "status": status})}
