# shop-order-driver — Day 5 Lab 1: sends 60 orders, one per second, to the shop-checkout function of your seat
import json, os, time
import boto3

lam = boto3.client("lambda")

def handler(event, context):
    target = os.environ["TARGET"]
    count = {"ok": 0, "unhandled": 0}
    for n in range(1, int(event.get("orders", 60)) + 1):
        r = lam.invoke(FunctionName=target, Payload=json.dumps({"order_id": "o-%03d" % n, "n": n}).encode())
        count["unhandled" if r.get("FunctionError") else "ok"] += 1
        time.sleep(1)
    print(json.dumps(count))
    return count
