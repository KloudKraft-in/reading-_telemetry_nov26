# metric-generator - TEL-D5-503. boto3 + cfnresponse only (both in the Lambda runtime).
# Every minute it publishes 3 custom metrics for ONE seat (CloudWatch namespace ShopNow); at stack creation it back-fills 6 hours.
# The pattern repeats every hour (UTC): CPU incident :30-:44, error incident :50-:57, plus noise.
import os, datetime as dt
import boto3
cw = boto3.client("cloudwatch")
SEAT = os.environ["SEAT"]

def vals(t):
    m = t.minute
    cpu = 91.0 if 30 <= m <= 44 else 93.0 if m % 7 == 3 else 35.0 + (m * 7) % 10
    req = 600 + (m * 13) % 80
    err = round(req * 0.06) if 50 <= m <= 57 else (3 if m % 5 == 2 else 0)
    return cpu, req, err

def points(t):
    cpu, req, err = vals(t)
    hd = [{"Name": "Seat", "Value": SEAT}, {"Name": "Host", "Value": "web-01"}]
    sd = [{"Name": "Seat", "Value": SEAT}, {"Name": "Service", "Value": "checkout"}]
    return [dict(MetricName="CPUUtilization", Dimensions=hd, Timestamp=t, Value=cpu, Unit="Percent"),
            dict(MetricName="Requests", Dimensions=sd, Timestamp=t, Value=req, Unit="Count"),
            dict(MetricName="Errors", Dimensions=sd, Timestamp=t, Value=err, Unit="Count")]

def put(items):
    for i in range(0, len(items), 500):
        cw.put_metric_data(Namespace="ShopNow", MetricData=items[i:i + 500])

def now_min():
    return dt.datetime.now(dt.timezone.utc).replace(second=0, microsecond=0)

def handler(event, context):
    if "RequestType" in event:                       # CloudFormation custom resource
        import cfnresponse
        try:
            if event["RequestType"] == "Create":
                t0 = now_min()
                items = []
                for k in range(360, 0, -1):
                    items += points(t0 - dt.timedelta(minutes=k))
                put(items)
            cfnresponse.send(event, context, cfnresponse.SUCCESS, {})
        except Exception as e:
            cfnresponse.send(event, context, cfnresponse.FAILED, {"Error": str(e)})
        return
    put(points(now_min()))
    return {"published": SEAT}
